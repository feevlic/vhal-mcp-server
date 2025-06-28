"""
Documentation summarization utilities for vHAL content.

This module provides functionality to summarize vHAL documentation based on user queries.
"""
import re
from typing import List


class VhalSummarizer:
    """Summarizes vHAL documentation content based on user questions."""
    
    MAX_SECTIONS = 3
    SECTION_LIMIT = 2000
    SUMMARY_LIMIT = 4000
    
    @staticmethod
    def extract_keywords(question: str) -> List[str]:
        """Extract keywords from a user question."""
        return re.findall(r'\b\w+\b', question.lower())
    
    @staticmethod
    def score_content(content: str, keywords: List[str]) -> int:
        """Score content based on keyword relevance."""
        content_lower = content.lower()
        return sum(1 for keyword in keywords if keyword in content_lower)
    
    @classmethod
    def summarize_documentation(cls, question: str, content_sections: List[str]) -> str:
        """Summarize documentation sections based on a question."""
        keywords = cls.extract_keywords(question)
        scored_sections = []
        
        for section in content_sections:
            if not section.strip():
                continue
            score = cls.score_content(section, keywords)
            if score > 0:
                scored_sections.append((score, section[:cls.SECTION_LIMIT]))
        
        scored_sections.sort(key=lambda x: x[0], reverse=True)
        
        if not scored_sections:
            fallback = "\n".join(content_sections)[:1500]
            return f"No specific information found for '{question}'. General vHAL overview:\n\n{fallback}..."
        
        summary_parts = [f"vHAL Summary for: '{question}'\n"]
        for _, section in scored_sections[:cls.MAX_SECTIONS]:
            summary_parts.append(section)
            summary_parts.append("\n" + "="*50 + "\n")
        
        summary = "\n".join(summary_parts)
        if len(summary) > cls.SUMMARY_LIMIT:
            summary = summary[:cls.SUMMARY_LIMIT] + "\n\n[Summary truncated]"
        
        return summary
