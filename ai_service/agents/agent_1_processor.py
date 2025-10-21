from services.openai_client import openai_client
from typing import Dict, List


class Agent1Processor:
    """
    Agent 1: Raw Data Processor
    Processes the document content and generates an initial answer to the user's prompt
    """

    def __init__(self):
        self.name = "Agent 1 - Raw Data Processor"

    def process(self, document_texts: List[Dict], prompt: str) -> str:
        """
        Process raw document data and generate an answer

        Args:
            document_texts: List of extracted PDF texts with metadata
            prompt: User's question/prompt

        Returns:
            str: Raw answer from Agent 1
        """
        # Combine all document texts
        combined_text = self._combine_documents(document_texts)

        # Create system message
        system_message = """You are a document analysis expert. Your task is to carefully read the provided documents and answer the user's question accurately and comprehensively.

Analyze the documents thoroughly and provide a detailed answer based on the information found. Include specific details, numbers, and references when available."""

        # Create user message with documents and prompt
        user_message = f"""Documents:
{combined_text}

---

User Question: {prompt}

Please provide a detailed answer based on the documents above."""

        # Get response from OpenAI
        response = openai_client.simple_prompt(
            system_message=system_message,
            user_message=user_message,
            temperature=0.3  # Lower temperature for more focused answers
        )

        return response

    def _combine_documents(self, document_texts: List[Dict]) -> str:
        """Combine multiple document texts into a single string"""
        combined = ""
        for doc in document_texts:
            combined += f"\n{'='*80}\n"
            combined += f"Document: {doc['file_name']}\n"
            combined += f"Total Pages: {doc['total_pages']}\n"
            combined += f"{'='*80}\n"
            combined += doc['full_text']
            combined += f"\n{'='*80}\n\n"
        return combined


# Singleton instance
agent_1 = Agent1Processor()
