from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    """Response model for document upload"""
    status: str
    message: str
    document_id: str
    filename: str
    word_count: int
    char_count: int
    file_type: str
    summary: str


class QuestionRequest(BaseModel):
    """Request model for asking questions"""
    document_id: str
    question: str
    conversation_history: Optional[List[Dict]] = []


class QuestionResponse(BaseModel):
    """Response model for question answering"""
    answer: str
    justification: str
    snippet: str
    status: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ChallengeQuestion(BaseModel):
    """Model for a challenge question"""
    question: str
    correct_answer: str
    explanation: str
    difficulty: str


class ChallengeQuestionsRequest(BaseModel):
    """Request model for generating challenge questions"""
    document_id: str
    count: int = 3


class ChallengeQuestionsResponse(BaseModel):
    """Response model for challenge questions"""
    questions: List[ChallengeQuestion]
    status: str
    document_id: str


class EvaluateAnswerRequest(BaseModel):
    """Request model for evaluating user answers"""
    document_id: str
    question: str
    user_answer: str
    correct_answer: str


class EvaluateAnswerResponse(BaseModel):
    """Response model for answer evaluation"""
    score: int
    feedback: str
    reference: str
    status: str
    timestamp: datetime = Field(default_factory=datetime.now)


class DocumentInfo(BaseModel):
    """Model for document information"""
    document_id: str
    filename: str
    file_type: str
    word_count: int
    char_count: int
    upload_timestamp: datetime
    summary: str


class ErrorResponse(BaseModel):
    """Standard error response model"""
    status: str = "error"
    message: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = "1.0.0"


class ConversationEntry(BaseModel):
    """Model for conversation history entry"""
    question: str
    answer: str
    justification: str
    timestamp: datetime = Field(default_factory=datetime.now)


class SessionData(BaseModel):
    """Model for session data"""
    session_id: str
    document_id: Optional[str] = None
    document_info: Optional[DocumentInfo] = None
    conversation_history: List[ConversationEntry] = []
    challenge_questions: List[ChallengeQuestion] = []
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
