import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration settings for the application"""

    # Google Gemini API
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    # FastAPI Configuration
    FASTAPI_HOST = os.getenv("FASTAPI_HOST", "localhost")
    FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", 8000))

    # Streamlit Configuration
    STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", 8501))

    # File upload settings
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = ['.pdf', '.txt', '.docx']

    # LLM Settings
    MODEL_NAME = "gemini-2.0-flash"
    MAX_OUTPUT_TOKENS = 2048
    TEMPERATURE = 0.3

    # Application Settings
    SUMMARY_MAX_WORDS = 150
    CHALLENGE_QUESTIONS_COUNT = 3

    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present"""
        if not cls.GOOGLE_API_KEY:
            raise ValueError(
                "GOOGLE_API_KEY is required. Please set it in your .env file")

        return True
