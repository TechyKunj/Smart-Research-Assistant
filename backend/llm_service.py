import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from typing import List, Dict, Any, Optional
import logging
import json
import re
from backend.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with Google Gemini API via LangChain"""

    def __init__(self):
        Config.validate_config()
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(Config.MODEL_NAME)

        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )

    def generate_summary(self, document_text: str, max_words: int = 150) -> Dict[str, Any]:
        """
        Generate a concise summary of the document

        Args:
            document_text: Full text of the document
            max_words: Maximum number of words in summary

        Returns:
            Dictionary containing summary and metadata
        """
        try:
            prompt = f"""
            Please provide a concise summary of the following document in no more than {max_words} words. 
            The summary should capture the main points, key findings, and overall theme of the document.
            
            Document:
            {document_text[:4000]}  # Limit input for API constraints
            
            Summary (max {max_words} words):
            """

            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=Config.TEMPERATURE,
                    max_output_tokens=300
                )
            )

            summary = response.text.strip()
            word_count = len(summary.split())

            return {
                "summary": summary,
                "word_count": word_count,
                "status": "success"
            }

        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return {
                "summary": "Error generating summary",
                "word_count": 0,
                "status": "error",
                "error": str(e)
            }

    def answer_question(self, question: str, document_text: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Answer a question based on the document content

        Args:
            question: User's question
            document_text: Full document text
            conversation_history: Previous conversation for context

        Returns:
            Dictionary containing answer and justification
        """
        try:
            # Build context from conversation history
            context = ""
            if conversation_history:
                context = "\n\nPrevious conversation:\n"
                for exchange in conversation_history[-3:]:  # Last 3 exchanges
                    context += f"Q: {exchange.get('question', '')}\nA: {exchange.get('answer', '')}\n"

            prompt = f"""
            Based on the following document, please answer the question. Your answer must be:
            1. Directly supported by the document content
            2. Include specific references to sections/paragraphs where the information is found
            3. If the information is not in the document, clearly state that
            4. Be accurate and avoid hallucination
            
            Document:
            {document_text[:6000]}  # Limit for API constraints
            
            {context}
            
            Question: {question}
            
            Please provide your answer in the following format:
            Answer: [Your detailed answer here]
            
            Justification: [Specific reference to where this information is found in the document, e.g., "This information is found in paragraph 3 of section 2..." or "According to the document's introduction..."]
            
            If the information is not available in the document, state: "This information is not available in the provided document."
            """

            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=Config.TEMPERATURE,
                    max_output_tokens=Config.MAX_OUTPUT_TOKENS
                )
            )

            response_text = response.text.strip()

            # Parse answer and justification
            answer_match = re.search(
                r'Answer:\s*(.*?)(?=\n\nJustification:|$)', response_text, re.DOTALL)
            justification_match = re.search(
                r'Justification:\s*(.*?)$', response_text, re.DOTALL)

            answer = answer_match.group(
                1).strip() if answer_match else response_text
            justification = justification_match.group(1).strip(
            ) if justification_match else "Based on document analysis"

            # Find relevant text snippet
            snippet = self._find_relevant_snippet(
                document_text, answer, question)

            return {
                "answer": answer,
                "justification": justification,
                "snippet": snippet,
                "status": "success"
            }

        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            return {
                "answer": "Error processing question",
                "justification": "Technical error occurred",
                "snippet": "",
                "status": "error",
                "error": str(e)
            }

    def generate_challenge_questions(self, document_text: str, count: int = 3) -> Dict[str, Any]:
        """
        Generate logic-based challenge questions from the document

        Args:
            document_text: Full document text
            count: Number of questions to generate

        Returns:
            Dictionary containing questions and correct answers
        """
        try:
            prompt = f"""
            Based on the following document, generate {count} challenging questions that test comprehension and logical reasoning. 
            The questions should:
            1. Require understanding of the document's content
            2. Test logical reasoning and inference
            3. Have clear, verifiable answers from the document
            4. Be of varying difficulty levels
            5. Cover different aspects of the document
            
            Document:
            {document_text[:6000]}  # Limit for API constraints
            
            Please provide exactly {count} questions in the following JSON format:
            {{
                "questions": [
                    {{
                        "question": "Your challenging question here",
                        "correct_answer": "The correct answer based on the document",
                        "explanation": "Detailed explanation of why this is correct, with document references",
                        "difficulty": "easy/medium/hard"
                    }}
                ]
            }}
            
            Make sure the JSON is valid and properly formatted.
            """

            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.5,  # Slightly higher for creativity
                    max_output_tokens=Config.MAX_OUTPUT_TOKENS
                )
            )

            response_text = response.text.strip()

            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                questions_data = json.loads(json_str)

                return {
                    "questions": questions_data.get("questions", []),
                    "status": "success"
                }
            else:
                # Fallback: parse manually
                questions = self._parse_questions_manually(
                    response_text, count)
                return {
                    "questions": questions,
                    "status": "success"
                }

        except Exception as e:
            logger.error(f"Error generating challenge questions: {str(e)}")
            return {
                "questions": [],
                "status": "error",
                "error": str(e)
            }

    def evaluate_answer(self, question: str, user_answer: str, correct_answer: str, document_text: str) -> Dict[str, Any]:
        """
        Evaluate user's answer to a challenge question

        Args:
            question: The challenge question
            user_answer: User's response
            correct_answer: Expected correct answer
            document_text: Full document text for reference

        Returns:
            Dictionary containing evaluation results
        """
        try:
            prompt = f"""
            Evaluate the user's answer to the following question based on the document content.
            
            Document context:
            {document_text[:4000]}
            
            Question: {question}
            
            Correct Answer: {correct_answer}
            
            User's Answer: {user_answer}
            
            Please evaluate the user's answer and provide:
            1. A score from 0-100 (0 = completely wrong, 100 = perfectly correct)
            2. Detailed feedback explaining what's correct/incorrect
            3. Specific document references that support the evaluation
            
            Format your response as:
            Score: [0-100]
            
            Feedback: [Detailed feedback here]
            
            Document Reference: [Specific references to support your evaluation]
            """

            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=Config.TEMPERATURE,
                    max_output_tokens=1000
                )
            )

            response_text = response.text.strip()

            # Parse score and feedback
            score_match = re.search(r'Score:\s*(\d+)', response_text)
            feedback_match = re.search(
                r'Feedback:\s*(.*?)(?=\n\nDocument Reference:|$)', response_text, re.DOTALL)
            reference_match = re.search(
                r'Document Reference:\s*(.*?)$', response_text, re.DOTALL)

            score = int(score_match.group(1)) if score_match else 0
            feedback = feedback_match.group(1).strip(
            ) if feedback_match else "Unable to evaluate"
            reference = reference_match.group(1).strip(
            ) if reference_match else "No specific reference"

            return {
                "score": score,
                "feedback": feedback,
                "reference": reference,
                "status": "success"
            }

        except Exception as e:
            logger.error(f"Error evaluating answer: {str(e)}")
            return {
                "score": 0,
                "feedback": "Error evaluating answer",
                "reference": "Technical error occurred",
                "status": "error",
                "error": str(e)
            }

    def _find_relevant_snippet(self, document_text: str, answer: str, question: str, max_length: int = 200) -> str:
        """Find the most relevant snippet from the document that supports the answer"""
        try:
            # Split document into sentences
            sentences = re.split(r'[.!?]+', document_text)

            # Find sentences that contain keywords from question or answer
            question_words = set(question.lower().split())
            answer_words = set(answer.lower().split())
            all_keywords = question_words.union(answer_words)

            # Remove common words
            common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be',
                            'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
            keywords = all_keywords - common_words

            # Score sentences based on keyword overlap
            best_sentence = ""
            best_score = 0

            for sentence in sentences:
                if len(sentence.strip()) < 20:  # Skip very short sentences
                    continue

                sentence_words = set(sentence.lower().split())
                overlap = len(keywords.intersection(sentence_words))

                if overlap > best_score:
                    best_score = overlap
                    best_sentence = sentence.strip()

            # Limit snippet length
            if len(best_sentence) > max_length:
                best_sentence = best_sentence[:max_length] + "..."

            return best_sentence

        except Exception as e:
            logger.error(f"Error finding relevant snippet: {str(e)}")
            return ""

    def _parse_questions_manually(self, response_text: str, count: int) -> List[Dict]:
        """Manually parse questions if JSON parsing fails"""
        questions = []

        # Simple regex patterns to extract questions
        question_patterns = [
            r'(?:Question|Q)[\s\d]*[:.]?\s*(.+?)(?=\n|$)',
            r'(\d+\.?\s*.+\?)',
            r'(.+\?)'
        ]

        for pattern in question_patterns:
            matches = re.findall(pattern, response_text, re.MULTILINE)
            for match in matches:
                if len(questions) >= count:
                    break

                question_text = match.strip()
                if len(question_text) > 10 and '?' in question_text:
                    questions.append({
                        "question": question_text,
                        "correct_answer": "Please refer to the document for the answer",
                        "explanation": "Generated from document analysis",
                        "difficulty": "medium"
                    })

        return questions[:count]
