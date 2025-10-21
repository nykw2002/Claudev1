import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class OpenAIClient:
    """Client for OpenAI API interactions"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.client = OpenAI(api_key=self.api_key)

    def chat_completion(self, messages: list, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """
        Send a chat completion request to OpenAI

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            str: Response content from OpenAI
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def simple_prompt(self, system_message: str, user_message: str, temperature: float = 0.7) -> str:
        """
        Simple prompt with system and user message

        Args:
            system_message: System instruction
            user_message: User prompt
            temperature: Sampling temperature

        Returns:
            str: Response from OpenAI
        """
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        return self.chat_completion(messages, temperature=temperature)


# Singleton instance
openai_client = OpenAIClient()
