import requests
from typing import Dict, Any
from app.models.config import RuntimeJSON
from app.models.response import AIResponse
from app.utils.config import settings
from fastapi import HTTPException


class AIServiceClient:
    """Client for communicating with the AI service"""

    def __init__(self):
        self.ai_service_url = settings.AI_SERVICE_URL
        self.process_endpoint = f"{self.ai_service_url}/api/process"

    async def process_documents(self, runtime_json: RuntimeJSON) -> AIResponse:
        """
        Send runtime JSON to AI service for processing

        Args:
            runtime_json: RuntimeJSON object with file paths and prompt

        Returns:
            AIResponse: Processed response from AI service

        Raises:
            HTTPException: If AI service request fails
        """
        try:
            # Convert Pydantic model to dict
            payload = runtime_json.model_dump(mode='json')
            print(f"AI Client - Sending payload to {self.process_endpoint}")
            print(f"AI Client - Payload: {payload}")

            # Make request to AI service
            response = requests.post(
                self.process_endpoint,
                json=payload,
                timeout=300  # 5 minute timeout for processing
            )

            print(f"AI Client - Response status: {response.status_code}")

            # Check response status
            response.raise_for_status()

            # Parse response
            ai_response_data = response.json()
            print(f"AI Client - Received response data")

            # DEBUG: Check if justifications are in the response
            print("="*80)
            print("DEBUG: Raw JSON response from AI service:")
            if 'metrics' in ai_response_data:
                metrics = ai_response_data['metrics']
                print(f"  Groundedness: {metrics.get('groundedness')}")
                print(f"  Groundedness Justification in JSON: {'groundedness_justification' in metrics}")
                if 'groundedness_justification' in metrics:
                    print(f"  Groundedness Justification preview: {metrics['groundedness_justification'][:100]}...")
                print(f"  Accuracy: {metrics.get('accuracy')}")
                print(f"  Accuracy Justification in JSON: {'accuracy_justification' in metrics}")
                if 'accuracy_justification' in metrics:
                    print(f"  Accuracy Justification preview: {metrics['accuracy_justification'][:100]}...")
                print(f"  Relevance: {metrics.get('relevance')}")
                print(f"  Relevance Justification in JSON: {'relevance_justification' in metrics}")
                if 'relevance_justification' in metrics:
                    print(f"  Relevance Justification preview: {metrics['relevance_justification'][:100]}...")
            print("="*80)

            # Validate and return as AIResponse model
            return AIResponse(**ai_response_data)

        except requests.exceptions.ConnectionError as e:
            print(f"AI Client - Connection error: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail="AI service is unavailable. Please ensure the AI service is running."
            )
        except requests.exceptions.Timeout as e:
            print(f"AI Client - Timeout error: {str(e)}")
            raise HTTPException(
                status_code=504,
                detail="AI service request timed out. Processing took too long."
            )
        except requests.exceptions.HTTPError as e:
            print(f"AI Client - HTTP error: {str(e)}")
            raise HTTPException(
                status_code=e.response.status_code if e.response else 500,
                detail=f"AI service error: {str(e)}"
            )
        except Exception as e:
            print(f"AI Client - Unexpected error: {str(e)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error communicating with AI service: {str(e)}"
            )

    def health_check(self) -> bool:
        """
        Check if AI service is healthy

        Returns:
            bool: True if AI service is responsive
        """
        try:
            response = requests.get(
                f"{self.ai_service_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False


# Singleton instance
ai_client = AIServiceClient()
