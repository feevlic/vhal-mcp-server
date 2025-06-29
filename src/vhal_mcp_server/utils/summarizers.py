import re
from typing import List, Tuple
from functools import lru_cache


class VhalSummarizer:
    """Summarizes vHAL documentation content based on user questions."""

    MAX_SECTIONS = 3
    SECTION_LIMIT = 2000
    SUMMARY_LIMIT = 4000

    @staticmethod
    @lru_cache(maxsize=128)
    def extract_keywords(question: str) -> Tuple[str, ...]:
        """Extract keywords from a user question - cached and optimized."""
        stopwords = {
            'what',
            'how',
            'are',
            'is',
            'the',
            'a',
            'an',
            'and',
            'or',
            'but',
            'in',
            'on',
            'at',
            'to',
            'for',
            'of',
            'with',
            'by',
            'do',
            'does'}
        keywords = [
            word for word in re.findall(
                r'\b\w{3,}\b',
                question.lower()) if word not in stopwords]
        return tuple(keywords)

    @staticmethod
    @lru_cache(maxsize=256)
    def score_content(content: str, keywords: Tuple[str, ...]) -> int:
        """Score content based on keyword relevance - optimized with caching."""
        if not keywords or not content:
            return 0

        content_lower = content.lower()
        score = 0
        for keyword in keywords:
            count = content_lower.count(keyword)
            if count > 0:
                weight = 2 if len(keyword) > 4 else 1
                score += count * weight

        return score

    @classmethod
    def summarize_documentation(
            cls,
            question: str,
            content_sections: List[str]) -> str:
        """Summarize documentation sections based on a question - optimized version."""
        if not content_sections:
            return f"No documentation content available for: '{question}'"

        keywords = cls.extract_keywords(question)
        if not keywords:
            fallback = content_sections[0][:cls.SECTION_LIMIT]
            return f"vHAL Summary for: '{question}'\n\n{fallback}"

        scored_sections = []

        for section in content_sections:
            section_clean = section.strip()
            if not section_clean or len(section_clean) < 50:
                continue

            score = cls.score_content(section_clean, keywords)
            if score > 0:
                truncated_section = section_clean[:cls.SECTION_LIMIT]
                scored_sections.append((score, truncated_section))

        if not scored_sections:
            best_content = max(content_sections, key=len)[:cls.SECTION_LIMIT]
            return f"No specific information found for '{
                question}'. General vHAL overview:\n\n{best_content}..."

        scored_sections.sort(key=lambda x: x[0], reverse=True)
        top_sections = scored_sections[:cls.MAX_SECTIONS]

        summary_parts = [f"vHAL Summary for: '{question}'\n"]
        total_length = len(summary_parts[0])

        for score, section in top_sections:
            section_with_separator = f"\n{section}\n" + "=" * 50 + "\n"

            if total_length + len(section_with_separator) > cls.SUMMARY_LIMIT:
                break

            summary_parts.append(section)
            summary_parts.append("\n" + "=" * 50 + "\n")
            total_length += len(section_with_separator)

        summary = "\n".join(summary_parts)

        if len(summary) > cls.SUMMARY_LIMIT:
            summary = summary[:cls.SUMMARY_LIMIT - 30] + \
                "\n\n[Summary truncated for length]"

        return summary
