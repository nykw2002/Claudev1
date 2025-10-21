from fastapi import FastAPI, HTTPException
from models.schemas import RuntimeJSON, AIResponse
from tools.pdf_text_extractor import extract_text_from_multiple_pdfs
from services.pattern_matcher import pattern_matcher
from agents.agent_1_processor import agent_1
from agents.agent_2_summarizer import agent_2
from agents.agent_3_evaluator import agent_3
from datetime import datetime
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Create FastAPI application
app = FastAPI(
    title="AI Document Processing Service",
    description="AI service with 3-agent pipeline for document analysis",
    version="1.0.0"
)


@app.post("/api/process", response_model=AIResponse)
async def process_documents(runtime_json: RuntimeJSON):
    """
    Process documents through the 3-agent pipeline

    Pipeline:
    1. Agent 1: Process raw data and generate initial answer
    2. Agent 2: Evaluate and summarize if needed
    3. Agent 3: Evaluate both answers and generate final answer with metrics

    Args:
        runtime_json: RuntimeJSON with file_paths and prompt

    Returns:
        AIResponse: Complete processing result with metrics
    """
    start_time = time.time()

    try:
        # Step 1: Extract text from PDFs (with automatic scanned PDF detection)
        print(f"Processing request {runtime_json.request_id}")
        print(f"Extracting text from {len(runtime_json.file_paths)} file(s)...")

        document_texts = extract_text_from_multiple_pdfs(
            runtime_json.file_paths
        )

        # Check if we should use pattern matching for this query
        should_use_pattern, entities = pattern_matcher.should_use_pattern_matching(
            runtime_json.prompt
        )

        if should_use_pattern:
            print(f"Using PATTERN MATCHING + AI for counting query. Entities: {entities}")

            # Combine all document texts
            full_text = "\n".join([doc["full_text"] for doc in document_texts])

            # Execute pattern matching to extract relevant sections
            pattern_result = pattern_matcher.execute_counting_search(
                runtime_json.prompt,
                full_text
            )

            print(f"Pattern matching found {pattern_result['total_matches']} matches")

            # Build condensed context from matches for AI processing
            condensed_context = f"Relevant sections extracted by pattern matching:\n\n"

            for i, match in enumerate(pattern_result['matches'][:50], 1):  # Top 50 matches
                condensed_context += f"Match {i} (Line {match['line_number']}):\n"
                condensed_context += f"{match['context']}\n"
                condensed_context += "-" * 80 + "\n\n"

            # Use condensed context instead of full document
            # Match the structure expected by agents
            condensed_doc = [{
                "file_path": runtime_json.file_paths[0] if runtime_json.file_paths else "extracted_sections",
                "file_name": "Pattern Matched Sections",
                "total_pages": 1,
                "pages": [{"page_num": 1, "text": condensed_context}],
                "full_text": condensed_context
            }]

            print(f"Condensed context: {len(condensed_context)} characters (vs {len(full_text)} original)")

            # Now send condensed context to AI agents
            print("Agent 1: Processing pattern-matched sections...")
            agent_1_output = agent_1.process(condensed_doc, runtime_json.prompt)

            print("Agent 2: Evaluating summarization need...")
            agent_2_output = agent_2.process(agent_1_output, runtime_json.prompt)

            print("Agent 3: Evaluating and generating metrics...")
            evaluation_result = agent_3.process(
                agent_1_output,
                agent_2_output,
                runtime_json.prompt,
                condensed_doc
            )

        else:
            print("Using FULL AI PIPELINE for complex query...")

            # Step 2: Agent 1 - Process raw data
            print("Agent 1: Processing documents...")
            agent_1_output = agent_1.process(document_texts, runtime_json.prompt)

            # Step 3: Agent 2 - Summarization check
            print("Agent 2: Evaluating summarization need...")
            agent_2_output = agent_2.process(agent_1_output, runtime_json.prompt)

            # Step 4: Agent 3 - Evaluation and metrics
            print("Agent 3: Evaluating and generating metrics...")
            evaluation_result = agent_3.process(
                agent_1_output,
                agent_2_output,
                runtime_json.prompt,
                document_texts
            )

        # Calculate processing time
        processing_time = time.time() - start_time

        # Build response
        response = AIResponse(
            request_id=runtime_json.request_id,
            agent_1_output=agent_1_output,
            agent_2_output=agent_2_output,
            agent_3_output=evaluation_result["agent_3_output"],
            final_answer=evaluation_result["final_answer"],
            metrics=evaluation_result["metrics"],
            sections_used=evaluation_result["sections_used"],
            processing_time_seconds=round(processing_time, 2),
            timestamp=datetime.utcnow()
        )

        print(f"Processing complete in {processing_time:.2f}s")

        # DEBUG: Log metrics to verify justifications are included
        print("="*80)
        print("DEBUG: Metrics being returned:")
        print(f"  Groundedness: {response.metrics.groundedness:.2f}")
        print(f"  Groundedness Justification: {response.metrics.groundedness_justification[:100]}...")
        print(f"  Accuracy: {response.metrics.accuracy:.2f}")
        print(f"  Accuracy Justification: {response.metrics.accuracy_justification[:100]}...")
        print(f"  Relevance: {response.metrics.relevance:.2f}")
        print(f"  Relevance Justification: {response.metrics.relevance_justification[:100]}...")
        print(f"  Overall Score: {response.metrics.overall_score:.2f}")
        print(f"  Needs Review: {response.metrics.needs_review}")
        print("="*80)

        return response

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing documents: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Check if OpenAI API key is configured
    api_key = os.getenv("OPENAI_API_KEY")
    api_configured = api_key is not None and api_key != "your_openai_api_key_here"

    return {
        "status": "healthy",
        "service": "AI Document Processing",
        "openai_configured": api_configured
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Document Processing Service",
        "version": "1.0.0",
        "agents": [
            "Agent 1: Raw Data Processor",
            "Agent 2: Summarization Agent",
            "Agent 3: Evaluation Agent"
        ],
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
