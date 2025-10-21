from services.openai_client import openai_client
from models.schemas import Metrics, SectionUsed
from typing import List, Dict
import json


class Agent3Evaluator:
    """
    Agent 3: Evaluation Agent
    Evaluates the answers from Agent 1 and Agent 2, determines the final answer,
    and generates quality metrics using the new evaluation framework:

    - Groundedness: Claims supported by verifiable data sources
    - Accuracy: Correctness of responses
    - Relevance: Pertinence to user's query

    Quality threshold: overall_score >= 0.8 (80%)
    """

    def __init__(self):
        self.name = "Agent 3 - Evaluation Agent"

    def process(
        self,
        agent_1_output: str,
        agent_2_output: str,
        original_prompt: str,
        document_texts: List[Dict]
    ) -> Dict:
        """
        Evaluate both agent outputs and determine final answer with metrics

        Args:
            agent_1_output: Raw answer from Agent 1
            agent_2_output: Summarized answer from Agent 2
            original_prompt: Original user prompt
            document_texts: Original document texts for reference

        Returns:
            dict: Contains final_answer, agent_3_output, metrics, and sections_used
        """
        # Get evaluation and final answer
        evaluation_result = self._evaluate_answers(
            agent_1_output,
            agent_2_output,
            original_prompt,
            document_texts
        )

        # Extract sections used from documents
        sections_used = self._extract_sections_used(
            evaluation_result["final_answer"],
            document_texts,
            original_prompt
        )

        return {
            "final_answer": evaluation_result["final_answer"],
            "agent_3_output": evaluation_result["agent_3_output"],
            "metrics": evaluation_result["metrics"],
            "sections_used": sections_used
        }

    def _evaluate_answers(
        self,
        agent_1_output: str,
        agent_2_output: str,
        prompt: str,
        document_texts: List[Dict]
    ) -> Dict:
        """
        Evaluate answers with 3 separate detailed evaluations for each metric.
        Each evaluation examines the original extracted document data.
        """

        # Prepare comprehensive document context
        doc_context = "\n\n".join([
            f"=== Document: {doc['file_name']} ===\n{doc['full_text'][:2000]}"
            for doc in document_texts[:3]  # First 3 docs
        ])

        # Step 1: Determine final answer and confidence
        print("Agent 3: Step 1 - Determining final answer...")
        final_answer_result = self._determine_final_answer(
            agent_1_output, agent_2_output, prompt
        )
        print(f"Agent 3: Final answer determined, confidence: {final_answer_result['confidence_score']:.2f}")

        # Step 2: Evaluate Groundedness (with document context)
        print("Agent 3: Step 2 - Evaluating GROUNDEDNESS with document context...")
        groundedness_result = self._evaluate_groundedness(
            final_answer_result["final_answer"],
            prompt,
            doc_context,
            agent_1_output
        )
        print(f"Agent 3: Groundedness score: {groundedness_result['score']:.2f}")
        print(f"Agent 3: Groundedness justification (preview): {groundedness_result['justification'][:100]}...")

        # Step 3: Evaluate Accuracy (with document context)
        print("Agent 3: Step 3 - Evaluating ACCURACY with document context...")
        accuracy_result = self._evaluate_accuracy(
            final_answer_result["final_answer"],
            prompt,
            doc_context,
            agent_1_output
        )
        print(f"Agent 3: Accuracy score: {accuracy_result['score']:.2f}")
        print(f"Agent 3: Accuracy justification (preview): {accuracy_result['justification'][:100]}...")

        # Step 4: Evaluate Relevance
        print("Agent 3: Step 4 - Evaluating RELEVANCE...")
        relevance_result = self._evaluate_relevance(
            final_answer_result["final_answer"],
            prompt
        )
        print(f"Agent 3: Relevance score: {relevance_result['score']:.2f}")
        print(f"Agent 3: Relevance justification (preview): {relevance_result['justification'][:100]}...")

        # Combine results
        groundedness = groundedness_result["score"]
        accuracy = accuracy_result["score"]
        relevance = relevance_result["score"]

        overall_score = (groundedness + accuracy + relevance) / 3.0
        needs_review = overall_score < 0.8

        # Create Metrics object
        metrics = Metrics(
            confidence_score=final_answer_result["confidence_score"],
            groundedness=groundedness,
            groundedness_justification=groundedness_result["justification"],
            accuracy=accuracy,
            accuracy_justification=accuracy_result["justification"],
            relevance=relevance,
            relevance_justification=relevance_result["justification"],
            sources_used=len(document_texts),
            overall_score=overall_score,
            needs_review=needs_review
        )

        # Create summary for agent_3_output
        agent_3_output = f"""EVALUATION SUMMARY:

Overall Quality Score: {overall_score:.2f} ({overall_score*100:.0f}%)
{'⚠️ NEEDS REVIEW - Score below 80% threshold' if needs_review else '✓ Quality threshold met'}

GROUNDEDNESS: {groundedness:.2f}
{groundedness_result['justification']}

ACCURACY: {accuracy:.2f}
{accuracy_result['justification']}

RELEVANCE: {relevance:.2f}
{relevance_result['justification']}"""

        return {
            "final_answer": final_answer_result["final_answer"],
            "agent_3_output": agent_3_output,
            "metrics": metrics
        }

    def _determine_final_answer(self, agent_1_output: str, agent_2_output: str, prompt: str) -> Dict:
        """Determine the best final answer from Agent 1 and Agent 2 outputs"""
        system_message = """You are an expert answer synthesizer. Review Agent 1's detailed output and Agent 2's summarized output.
Choose the best final answer or combine them intelligently.

Return JSON:
{
    "final_answer": "The best answer (clear, concise, complete)",
    "confidence_score": 0.95
}"""

        user_message = f"""Question: {prompt}

Agent 1 (Detailed): {agent_1_output}
Agent 2 (Summary): {agent_2_output}

Choose the best answer."""

        response = openai_client.simple_prompt(
            system_message=system_message,
            user_message=user_message,
            temperature=0.3
        )

        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            result = json.loads(json_str)

            return {
                "final_answer": result.get("final_answer", agent_2_output),
                "confidence_score": float(result.get("confidence_score", 0.8))
            }
        except Exception as e:
            print(f"Error determining final answer: {e}")
            return {
                "final_answer": agent_2_output,
                "confidence_score": 0.7
            }

    def _evaluate_groundedness(
        self,
        final_answer: str,
        prompt: str,
        doc_context: str,
        agent_1_output: str
    ) -> Dict:
        """
        Evaluate GROUNDEDNESS: Are all claims in the answer supported by the document sources?
        Examines original extracted document data to verify claims.
        """
        system_message = """You are a fact-checking expert evaluating GROUNDEDNESS.

GROUNDEDNESS measures whether claims in the answer are supported by verifiable data from the source documents.

Scoring rubric:
- 1.0: Every claim is directly supported by explicit statements in the documents
- 0.8: Most claims supported, minor details inferred reasonably
- 0.6: Some claims supported, but significant inferences without direct evidence
- 0.4: Many claims lack document support
- 0.2: Most claims are unsupported or contradict documents
- 0.0: Answer is entirely unsupported by documents

Your task:
1. Identify each claim in the answer
2. Check if each claim is directly found in the source documents
3. Note any inferences or unsupported statements
4. Provide detailed justification referencing specific document content

Return JSON:
{
    "score": 0.95,
    "justification": "Detailed explanation: List each claim and whether it's supported by documents. Quote relevant document passages."
}"""

        user_message = f"""Question: {prompt}

Answer to evaluate:
{final_answer}

Agent 1's extracted data and analysis:
{agent_1_output[:1000]}

Original source document content:
{doc_context}

---

Evaluate the GROUNDEDNESS of the answer. Are all claims supported by the source documents?"""

        response = openai_client.simple_prompt(
            system_message=system_message,
            user_message=user_message,
            temperature=0.2
        )

        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            result = json.loads(json_str)

            return {
                "score": float(result.get("score", 0.7)),
                "justification": result.get("justification", "Unable to evaluate groundedness")
            }
        except Exception as e:
            print(f"Error evaluating groundedness: {e}")
            return {
                "score": 0.7,
                "justification": f"Groundedness evaluation error: {str(e)}"
            }

    def _evaluate_accuracy(
        self,
        final_answer: str,
        prompt: str,
        doc_context: str,
        agent_1_output: str
    ) -> Dict:
        """
        Evaluate ACCURACY: Is the answer factually correct based on the document content?
        Cross-references answer against original extracted data.
        """
        system_message = """You are a factual accuracy expert evaluating ACCURACY.

ACCURACY measures whether the answer is factually correct according to the source documents.

Scoring rubric:
- 1.0: Completely accurate, no errors
- 0.8: Accurate with only trivial/formatting differences
- 0.6: Mostly accurate but contains minor factual errors
- 0.4: Contains several factual errors
- 0.2: Many significant factual errors
- 0.0: Fundamentally incorrect

Your task:
1. Compare the answer against the document facts
2. Identify any factual errors (wrong numbers, dates, names, relationships)
3. Verify calculations, counts, or aggregations if present
4. Provide detailed justification with specific examples

Return JSON:
{
    "score": 0.95,
    "justification": "Detailed explanation: Verify each fact. Note any errors. Cross-check calculations."
}"""

        user_message = f"""Question: {prompt}

Answer to evaluate:
{final_answer}

Agent 1's data extraction:
{agent_1_output[:1000]}

Original source document content:
{doc_context}

---

Evaluate the ACCURACY of the answer. Are all facts correct according to the documents?"""

        response = openai_client.simple_prompt(
            system_message=system_message,
            user_message=user_message,
            temperature=0.2
        )

        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            result = json.loads(json_str)

            return {
                "score": float(result.get("score", 0.7)),
                "justification": result.get("justification", "Unable to evaluate accuracy")
            }
        except Exception as e:
            print(f"Error evaluating accuracy: {e}")
            return {
                "score": 0.7,
                "justification": f"Accuracy evaluation error: {str(e)}"
            }

    def _evaluate_relevance(
        self,
        final_answer: str,
        prompt: str
    ) -> Dict:
        """
        Evaluate RELEVANCE: Does the answer directly address the user's question?
        """
        system_message = """You are a relevance expert evaluating RELEVANCE.

RELEVANCE measures whether the answer directly addresses what the user asked.

Scoring rubric:
- 1.0: Perfectly addresses the question, no extraneous information
- 0.8: Addresses question well, minor tangential details
- 0.6: Partially addresses question, some irrelevant content
- 0.4: Loosely related but misses key aspects
- 0.2: Mostly irrelevant to the question
- 0.0: Completely irrelevant

Your task:
1. Identify what the user is asking for
2. Determine if the answer provides exactly that
3. Note any missing information or unnecessary tangents
4. Provide detailed justification

Return JSON:
{
    "score": 0.95,
    "justification": "Detailed explanation: Does the answer address the question? What's missing or extraneous?"
}"""

        user_message = f"""Question: {prompt}

Answer to evaluate:
{final_answer}

---

Evaluate the RELEVANCE of the answer. Does it directly address the user's question?"""

        response = openai_client.simple_prompt(
            system_message=system_message,
            user_message=user_message,
            temperature=0.2
        )

        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            result = json.loads(json_str)

            return {
                "score": float(result.get("score", 0.7)),
                "justification": result.get("justification", "Unable to evaluate relevance")
            }
        except Exception as e:
            print(f"Error evaluating relevance: {e}")
            return {
                "score": 0.7,
                "justification": f"Relevance evaluation error: {str(e)}"
            }

    def _extract_sections_used(
        self,
        final_answer: str,
        document_texts: List[Dict],
        prompt: str
    ) -> List[SectionUsed]:
        """
        Extract relevant sections from documents that were used to generate the answer

        Args:
            final_answer: The final answer text
            document_texts: Original document texts
            prompt: Original prompt

        Returns:
            List[SectionUsed]: Sections from PDFs used in the answer
        """
        sections = []

        # Simple extraction: find pages that contain keywords from the answer
        # In a production system, this would be more sophisticated
        for doc in document_texts:
            for page in doc['pages']:
                # Check if page content is relevant
                page_text = page['text'].lower()
                answer_lower = final_answer.lower()
                prompt_lower = prompt.lower()

                # Simple relevance check
                if any(word in page_text for word in prompt_lower.split() if len(word) > 3):
                    # Extract a snippet (first 200 chars of the page)
                    snippet = page['text'][:200].strip()
                    if snippet:
                        sections.append(SectionUsed(
                            file=doc['file_name'],
                            page=page['page_num'],
                            text_snippet=snippet + "..."
                        ))

                    # Limit to 5 sections
                    if len(sections) >= 5:
                        break

            if len(sections) >= 5:
                break

        return sections


# Singleton instance
agent_3 = Agent3Evaluator()
