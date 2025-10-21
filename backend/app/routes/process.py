from fastapi import APIRouter, HTTPException
from app.models.config import RuntimeJSON
from app.models.response import AIResponse
from app.services.ai_client import ai_client
from app.services.file_service import file_service

router = APIRouter(prefix="/api", tags=["process"])


@router.post("/process", response_model=AIResponse)
async def process_documents(runtime_json: RuntimeJSON):
    """
    Process uploaded documents with AI service

    This endpoint:
    1. Receives a RuntimeJSON with file paths and user prompt
    2. Sends the JSON to the AI service for processing
    3. Returns the AI response with final answer and metrics

    Args:
        runtime_json: RuntimeJSON containing file_paths and prompt

    Returns:
        AIResponse: Complete AI processing result with metrics
    """
    try:
        print(f"Processing request - Files: {runtime_json.file_paths}, Prompt: {runtime_json.prompt[:50]}...")

        from pathlib import Path

        # Validate file paths exist and convert to absolute paths
        absolute_file_paths = []
        for file_path in runtime_json.file_paths:
            # Handle both absolute and relative paths
            full_path = Path(file_path)
            if not full_path.is_absolute():
                full_path = Path.cwd() / file_path

            print(f"Validating file path: {file_path} -> {full_path}")

            if not full_path.exists():
                print(f"File not found: {full_path}")
                raise HTTPException(
                    status_code=404,
                    detail=f"File not found: {file_path}"
                )

            print(f"File validated: {full_path}")
            absolute_file_paths.append(str(full_path))

        # Create new RuntimeJSON with absolute paths
        runtime_json_absolute = RuntimeJSON(
            request_id=runtime_json.request_id,
            file_paths=absolute_file_paths,
            prompt=runtime_json.prompt,
            timestamp=runtime_json.timestamp
        )

        # Send to AI service for processing
        print(f"Sending request to AI service with absolute paths: {absolute_file_paths}")
        ai_response = await ai_client.process_documents(runtime_json_absolute)
        print("Received response from AI service")

        # DEBUG: Log metrics justifications
        print("="*80)
        print("DEBUG: Backend received metrics:")
        print(f"  Groundedness: {ai_response.metrics.groundedness:.2f}")
        print(f"  Groundedness Justification exists: {hasattr(ai_response.metrics, 'groundedness_justification')}")
        if hasattr(ai_response.metrics, 'groundedness_justification'):
            print(f"  Groundedness Justification preview: {ai_response.metrics.groundedness_justification[:100]}...")
        print(f"  Accuracy: {ai_response.metrics.accuracy:.2f}")
        print(f"  Accuracy Justification exists: {hasattr(ai_response.metrics, 'accuracy_justification')}")
        if hasattr(ai_response.metrics, 'accuracy_justification'):
            print(f"  Accuracy Justification preview: {ai_response.metrics.accuracy_justification[:100]}...")
        print(f"  Relevance: {ai_response.metrics.relevance:.2f}")
        print(f"  Relevance Justification exists: {hasattr(ai_response.metrics, 'relevance_justification')}")
        if hasattr(ai_response.metrics, 'relevance_justification'):
            print(f"  Relevance Justification preview: {ai_response.metrics.relevance_justification[:100]}...")
        print("="*80)

        # Optionally: Clean up files after processing
        # file_service.delete_multiple_files(runtime_json.file_paths)

        return ai_response

    except HTTPException as e:
        print(f"HTTPException: {e.detail}")
        raise e
    except Exception as e:
        print(f"Error processing documents: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing documents: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint

    Returns:
        dict: Service status and AI service availability
    """
    ai_service_status = ai_client.health_check()

    return {
        "status": "healthy",
        "ai_service_connected": ai_service_status
    }
