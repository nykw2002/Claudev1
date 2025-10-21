from pydantic import BaseModel, Field
from typing import List, Literal
from datetime import datetime


class RuntimeJSON(BaseModel):
    """Input schema from backend"""
    request_id: str
    file_paths: List[str]
    prompt: str
    timestamp: datetime


class SectionUsed(BaseModel):
    """PDF section used in answer generation"""
    file: str
    page: int
    text_snippet: str


class Metrics(BaseModel):
    """
    Evaluation metrics from Agent 3

    New evaluation framework based on:
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


class AIResponse(BaseModel):
    """Output schema to backend"""
    request_id: str
    agent_1_output: str
    agent_2_output: str
    agent_3_output: str
    final_answer: str
    metrics: Metrics
    sections_used: List[SectionUsed]
    processing_time_seconds: float
    timestamp: datetime
