from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from datetime import datetime
import uuid
from typing import Dict, Any
import asyncio

# Import our modules
from backend.config import Config
from backend.document_processor import DocumentProcessor
from backend.llm_service import LLMService
from backend.api_models import *

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Smart Research Assistant API",
    description="AI-powered document analysis and question answering system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
document_processor = DocumentProcessor()
llm_service = LLMService()

# In-memory storage for documents and sessions
documents_storage: Dict[str, Dict[str, Any]] = {}
sessions_storage: Dict[str, SessionData] = {}


@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    try:
        Config.validate_config()
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse()


@app.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Upload and process a document
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        # Check file size
        file_content = await file.read()
        if len(file_content) > Config.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {Config.MAX_FILE_SIZE/1024/1024}MB"
            )

        # Generate document ID
        document_id = str(uuid.uuid4())

        # Process document
        processed_doc = document_processor.process_document(
            file_content, file.filename)

        if processed_doc["status"] == "error":
            raise HTTPException(status_code=400, detail=processed_doc["error"])

        # Generate summary
        summary_result = llm_service.generate_summary(processed_doc["text"])
        summary = summary_result.get("summary", "Summary generation failed")

        # Store document
        documents_storage[document_id] = {
            "id": document_id,
            "filename": processed_doc["filename"],
            "file_type": processed_doc["file_type"],
            "text": processed_doc["text"],
            "word_count": processed_doc["word_count"],
            "char_count": processed_doc["char_count"],
            "summary": summary,
            "upload_timestamp": datetime.now(),
            "status": "ready"
        }

        logger.info(f"Document uploaded and processed: {document_id}")

        return DocumentUploadResponse(
            status="success",
            message="Document uploaded and processed successfully",
            document_id=document_id,
            filename=processed_doc["filename"],
            word_count=processed_doc["word_count"],
            char_count=processed_doc["char_count"],
            file_type=processed_doc["file_type"],
            summary=summary
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question about the uploaded document
    """
    try:
        # Validate document exists
        if request.document_id not in documents_storage:
            raise HTTPException(status_code=404, detail="Document not found")

        document = documents_storage[request.document_id]

        # Get answer from LLM
        result = llm_service.answer_question(
            question=request.question,
            document_text=document["text"],
            conversation_history=request.conversation_history
        )

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result.get(
                "error", "Failed to process question"))

        return QuestionResponse(
            answer=result["answer"],
            justification=result["justification"],
            snippet=result["snippet"],
            status="success"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/challenge", response_model=ChallengeQuestionsResponse)
async def generate_challenge_questions(request: ChallengeQuestionsRequest):
    """
    Generate challenge questions based on the document
    """
    try:
        # Validate document exists
        if request.document_id not in documents_storage:
            raise HTTPException(status_code=404, detail="Document not found")

        document = documents_storage[request.document_id]

        # Generate challenge questions
        result = llm_service.generate_challenge_questions(
            document_text=document["text"],
            count=request.count
        )

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result.get(
                "error", "Failed to generate questions"))

        questions = [ChallengeQuestion(**q) for q in result["questions"]]

        return ChallengeQuestionsResponse(
            questions=questions,
            status="success",
            document_id=request.document_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating challenge questions: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/evaluate", response_model=EvaluateAnswerResponse)
async def evaluate_answer(request: EvaluateAnswerRequest):
    """
    Evaluate user's answer to a challenge question
    """
    try:
        # Validate document exists
        if request.document_id not in documents_storage:
            raise HTTPException(status_code=404, detail="Document not found")

        document = documents_storage[request.document_id]

        # Evaluate answer
        result = llm_service.evaluate_answer(
            question=request.question,
            user_answer=request.user_answer,
            correct_answer=request.correct_answer,
            document_text=document["text"]
        )

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result.get(
                "error", "Failed to evaluate answer"))

        return EvaluateAnswerResponse(
            score=result["score"],
            feedback=result["feedback"],
            reference=result["reference"],
            status="success"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error evaluating answer: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/document/{document_id}")
async def get_document_info(document_id: str):
    """
    Get information about a specific document
    """
    try:
        if document_id not in documents_storage:
            raise HTTPException(status_code=404, detail="Document not found")

        document = documents_storage[document_id]

        return DocumentInfo(
            document_id=document_id,
            filename=document["filename"],
            file_type=document["file_type"],
            word_count=document["word_count"],
            char_count=document["char_count"],
            upload_timestamp=document["upload_timestamp"],
            summary=document["summary"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document info: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}")


@app.delete("/document/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document from storage
    """
    try:
        if document_id not in documents_storage:
            raise HTTPException(status_code=404, detail="Document not found")

        del documents_storage[document_id]
        logger.info(f"Document deleted: {document_id}")

        return {"status": "success", "message": "Document deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            message="An unexpected error occurred",
            error_code="INTERNAL_ERROR"
        ).dict()
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=Config.FASTAPI_HOST,
        port=Config.FASTAPI_PORT,
        reload=True,
        log_level="info"
    )
