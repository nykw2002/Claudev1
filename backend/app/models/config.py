from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
import uuid


class ConfigJSON(BaseModel):
    """
    Template schema - represents the structure before user input
    """
    file_paths: List[str] = Field(default_factory=list, description="List of file paths to process")
    prompt: str = Field(default="", description="User's query/prompt")


class RuntimeJSON(BaseModel):
    """
    Runtime schema - populated with user data, sent to AI service
    """
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique request identifier")
    file_paths: List[str] = Field(..., description="List of uploaded file paths")
    prompt: str = Field(..., min_length=1, description="User's query/prompt")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Request timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "123e4567-e89b-12d3-a456-426614174000",
                "file_paths": [
                    "uploads/file1.pdf",
                    "uploads/file2.pdf"
                ],
                "prompt": "How many complaints are from Israel?",
                "timestamp": "2025-10-20T10:30:00Z"
            }
        }
