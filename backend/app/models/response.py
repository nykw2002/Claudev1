from pydantic import BaseModel, Field
from typing import List, Literal
from datetime import datetime


class SectionUsed(BaseModel):
    """
    Represents a section from the PDF that was used to generate the answer
    """
    file: str = Field(..., description="Filename of the PDF")
    page: int = Field(..., description="Page number")
    text_snippet: str = Field(..., description="Relevant text excerpt")


class Metrics(BaseModel):
    """
    Evaluation metrics from Agent 3 using new evaluation framework

    Based on three key metrics:
    - Groundedness: Claims supported by verifiable data sources
    - Accuracy: Correctness of responses
    - Relevance: Pertinence to user's query

    Quality threshold: overall_score >= 0.8 (80%)

    Each metric includes a detailed justification based on:
    - Agent 1 and Agent 2 outputs
    - Original extracted document data
    - User's query context
    """
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in the answer")
    groundedness: float = Field(..., ge=0.0, le=1.0, description="Claims based on reliable data sources")
    groundedness_justification: str = Field(..., description="Detailed justification for groundedness score")
    accuracy: float = Field(..., ge=0.0, le=1.0, description="Correctness of the response")
    accuracy_justification: str = Field(..., description="Detailed justification for accuracy score")
    relevance: float = Field(..., ge=0.0, le=1.0, description="Pertinence to user's query")
    relevance_justification: str = Field(..., description="Detailed justification for relevance score")
    sources_used: int = Field(..., ge=0, description="Number of document sources used")
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Average of groundedness, accuracy, relevance")
    needs_review: bool = Field(..., description="True if overall_score < 0.8")


class AgentOutput(BaseModel):
    """
    Output from individual agents
    """
    agent_name: str = Field(..., description="Name of the agent")
    output: str = Field(..., description="Agent's output text")


class AIResponse(BaseModel):
    """
    Complete response from AI service back to backend
    """
    request_id: str = Field(..., description="Original request ID")
    agent_1_output: str = Field(..., description="Raw answer from Agent 1")
    agent_2_output: str = Field(..., description="Summarized answer from Agent 2")
    agent_3_output: str = Field(..., description="Evaluation reasoning from Agent 3")
    final_answer: str = Field(..., description="Final evaluated answer")
    metrics: Metrics = Field(..., description="Evaluation metrics")
    sections_used: List[SectionUsed] = Field(default_factory=list, description="PDF sections used")
    processing_time_seconds: float = Field(..., description="Total processing time")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "123e4567-e89b-12d3-a456-426614174000",
                "agent_1_output": "Based on the document, there are 15 complaints from Israel.",
                "agent_2_output": "15 complaints from Israel.",
                "agent_3_output": "Agent 2's concise answer directly addresses the question with high accuracy. All claims are supported by document sources with strong groundedness.",
                "final_answer": "There are 15 complaints from Israel in the provided documents.",
                "metrics": {
                    "confidence_score": 0.95,
                    "accuracy_assessment": "high",
                    "completeness": 0.88,
                    "sources_used": 3
                },
                "sections_used": [
                    {
                        "file": "file1.pdf",
                        "page": 3,
                        "text_snippet": "Israel: 15 complaints recorded..."
                    }
                ],
                "processing_time_seconds": 12.5,
                "timestamp": "2025-10-20T10:30:15Z"
            }
        }
