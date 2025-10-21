import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()


class Settings:
    """Application configuration settings"""

    # AI Service
    AI_SERVICE_URL: str = os.getenv("AI_SERVICE_URL", "http://localhost:8001")

    # File Upload Settings
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    ALLOWED_EXTENSIONS: set = set(os.getenv("ALLOWED_EXTENSIONS", ".pdf").split(","))

    # Server Settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # CORS Settings
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]

    def __init__(self):
        # Ensure upload directory exists
        Path(self.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


settings = Settings()
