"""
Direct Pattern Matching Service
Provides fast regex-based pattern matching for counting queries and entity extraction
"""
import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class MatchResult:
    """Result of a pattern match"""
    line_number: int
    line_text: str
    matched_entities: List[str]
    context: str


class PatternMatcher:
    """
    Direct pattern matching using regex for fast document scanning
    Perfect for counting queries and entity extraction
    """

    # Common entity patterns for pharmaceutical documents
    ENTITY_PATTERNS = {
        'israel': r'(?i)\b(israel|israeli)\b',
        'unsubstantiated': r'(?i)\b(unsubstantiated|not substantiated|unvalidated)\b',
        'substantiated': r'(?i)\b(substantiated|validated|confirmed)\b',
        'complaint': r'(?i)\b(complaint|adverse event|ae|report)\b',
        'usa': r'(?i)\b(usa|united states|u\.s\.a|america|american)\b',
        'uk': r'(?i)\b(uk|united kingdom|u\.k|britain|british)\b',
        'germany': r'(?i)\b(germany|german|deutschland)\b',
        'france': r'(?i)\b(france|french)\b',
        'italy': r'(?i)\b(italy|italian)\b',
        'spain': r'(?i)\b(spain|spanish)\b',
        'canada': r'(?i)\b(canada|canadian)\b',
        'australia': r'(?i)\b(australia|australian)\b',
        'japan': r'(?i)\b(japan|japanese)\b',
        'china': r'(?i)\b(china|chinese)\b',
    }

    def __init__(self):
        # Pre-compile all patterns for performance
        self.compiled_patterns = {
            entity: re.compile(pattern)
            for entity, pattern in self.ENTITY_PATTERNS.items()
        }

    def is_counting_query(self, query: str) -> bool:
        """
        Detect if query is a counting query

        Args:
            query: User query text

        Returns:
            bool: True if query asks for counting
        """
        counting_keywords = [
            r'\bhow many\b',
            r'\bcount\b',
            r'\bnumber of\b',
            r'\btotal\b',
            r'\bsum\b',
        ]

        query_lower = query.lower()
        return any(re.search(pattern, query_lower) for pattern in counting_keywords)

    def extract_entities_from_query(self, query: str) -> List[str]:
        """
        Extract entities mentioned in the query

        Args:
            query: User query text

        Returns:
            List of entity names found in query
        """
        entities = []
        query_lower = query.lower()

        for entity, pattern in self.compiled_patterns.items():
            if pattern.search(query_lower):
                entities.append(entity)

        return entities

    def scan_document(
        self,
        text: str,
        entities: List[str],
        context_lines: int = 2
    ) -> List[MatchResult]:
        """
        Scan document for lines matching all specified entities

        Args:
            text: Full document text
            entities: List of entity names to search for
            context_lines: Number of surrounding lines to include

        Returns:
            List of MatchResult objects
        """
        if not entities:
            return []

        lines = text.split('\n')
        matches = []

        # Get compiled patterns for requested entities
        patterns = {
            entity: self.compiled_patterns.get(entity)
            for entity in entities
            if entity in self.compiled_patterns
        }

        # Scan each line
        for i, line in enumerate(lines):
            matched_entities = []

            # Check which entities match this line
            for entity, pattern in patterns.items():
                if pattern and pattern.search(line):
                    matched_entities.append(entity)

            # If all required entities match, add to results
            if len(matched_entities) == len(patterns):
                # Extract context (surrounding lines)
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                context = '\n'.join(lines[start:end])

                matches.append(MatchResult(
                    line_number=i + 1,
                    line_text=line.strip(),
                    matched_entities=matched_entities,
                    context=context
                ))

        return matches

    def execute_counting_search(
        self,
        query: str,
        text: str
    ) -> Dict[str, Any]:
        """
        Execute a counting search using pattern matching

        Args:
            query: User query
            text: Document text to search

        Returns:
            Dict with count, matches, and summary
        """
        # Extract entities from query
        entities = self.extract_entities_from_query(query)

        # Scan document
        matches = self.scan_document(text, entities)

        # Build result
        result = {
            'is_counting_query': True,
            'query': query,
            'entities_searched': entities,
            'total_matches': len(matches),
            'matches': [
                {
                    'line_number': m.line_number,
                    'line_text': m.line_text,
                    'matched_entities': m.matched_entities,
                    'context': m.context
                }
                for m in matches[:50]  # Limit to first 50 matches for response size
            ],
            'summary': self._generate_summary(query, entities, matches)
        }

        return result

    def _generate_summary(
        self,
        query: str,
        entities: List[str],
        matches: List[MatchResult]
    ) -> str:
        """Generate a human-readable summary of the search"""
        if not matches:
            return f"No matches found for entities: {', '.join(entities)}"

        summary = f"Found {len(matches)} occurrences matching all entities: {', '.join(entities)}"

        # Add sample matches
        if matches:
            summary += f"\n\nSample matches:"
            for match in matches[:3]:
                summary += f"\n- Line {match.line_number}: {match.line_text[:100]}..."

        return summary

    def should_use_pattern_matching(self, query: str) -> Tuple[bool, List[str]]:
        """
        Determine if pattern matching should be used for this query

        Args:
            query: User query

        Returns:
            Tuple of (should_use, entities)
        """
        is_counting = self.is_counting_query(query)
        entities = self.extract_entities_from_query(query)

        # Use pattern matching if it's a counting query and we have entities
        should_use = is_counting and len(entities) > 0

        return should_use, entities


# Singleton instance
pattern_matcher = PatternMatcher()
