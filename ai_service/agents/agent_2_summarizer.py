from services.openai_client import openai_client


class Agent2Summarizer:
    """
    Agent 2: Summarization Agent
    Evaluates if Agent 1's answer needs summarization and provides a concise version if needed
    """

    def __init__(self):
        self.name = "Agent 2 - Summarization Agent"

    def process(self, agent_1_output: str, original_prompt: str) -> str:
        """
        Evaluate and potentially summarize Agent 1's output

        Args:
            agent_1_output: Raw answer from Agent 1
            original_prompt: Original user prompt

        Returns:
            str: Summarized answer or original if no summarization needed
        """
        system_message = """You are a summarization expert. Your task is to:
1. Evaluate if the provided answer needs summarization (too long, verbose, or contains unnecessary details)
2. If summarization is needed, provide a concise, clear summary that retains all key information
3. If the answer is already concise, return it as-is

Focus on clarity and brevity while maintaining accuracy."""

        user_message = f"""Original Question: {original_prompt}

Answer to Evaluate:
{agent_1_output}

---

Please determine if this answer needs summarization. If yes, provide a concise summary. If the answer is already clear and concise, simply state that no summarization is needed and return the original answer."""

        response = openai_client.simple_prompt(
            system_message=system_message,
            user_message=user_message,
            temperature=0.5
        )

        return response

    def needs_summarization(self, text: str, threshold: int = 500) -> bool:
        """
        Simple heuristic to check if text needs summarization

        Args:
            text: Text to evaluate
            threshold: Character count threshold

        Returns:
            bool: True if summarization is likely needed
        """
        return len(text) > threshold


# Singleton instance
agent_2 = Agent2Summarizer()
