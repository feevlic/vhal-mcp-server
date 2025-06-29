import requests
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed


@dataclass
class SourceValidation:
    """Represents validation result for a documentation source."""
    url: str
    is_accessible: bool
    status_code: Optional[int]
    last_modified: Optional[str]
    content_length: Optional[int]
    response_time_ms: Optional[float]
    error_message: Optional[str]
    validation_timestamp: float


@dataclass
class EnhancedSummaryResult:
    """Enhanced summary with source validation and transparency."""
    question: str
    summary_content: str
    source_validations: List[SourceValidation]
    confidence_score: float
    total_sources_checked: int
    accessible_sources_count: int
    cached_sources_count: int
    suggestions_for_failed_sources: List[str]


class VhalSourceValidator:
    """Validates vHAL documentation sources and enhances summaries with transparency."""
    
    TIMEOUT = 5
    MAX_WORKERS = 3
    
    @classmethod
    def validate_source(cls, url: str, session: requests.Session = None) -> SourceValidation:
        """Validate a single source URL."""
        start_time = time.time()
        
        if session is None:
            session = requests.Session()
            
        try:
            # Use HEAD request for efficiency
            response = session.head(url, timeout=cls.TIMEOUT, allow_redirects=True)
            response_time_ms = (time.time() - start_time) * 1000
            
            return SourceValidation(
                url=url,
                is_accessible=response.status_code == 200,
                status_code=response.status_code,
                last_modified=response.headers.get('Last-Modified'),
                content_length=response.headers.get('Content-Length'),
                response_time_ms=response_time_ms,
                error_message=None if response.status_code == 200 else f"HTTP {response.status_code}",
                validation_timestamp=time.time()
            )
            
        except requests.exceptions.RequestException as e:
            response_time_ms = (time.time() - start_time) * 1000
            return SourceValidation(
                url=url,
                is_accessible=False,
                status_code=None,
                last_modified=None,
                content_length=None,
                response_time_ms=response_time_ms,
                error_message=str(e),
                validation_timestamp=time.time()
            )
    
    @classmethod
    def validate_sources_parallel(cls, urls: List[str], max_workers: int = None) -> List[SourceValidation]:
        """Validate multiple sources in parallel."""
        if max_workers is None:
            max_workers = min(cls.MAX_WORKERS, len(urls))
            
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'vHAL-MCP-Server-Validator/1.0',
            'Accept': '*/*',
            'Connection': 'keep-alive'
        })
        
        validations = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(cls.validate_source, url, session): url 
                for url in urls
            }
            
            for future in as_completed(future_to_url, timeout=cls.TIMEOUT * 2):
                try:
                    validation = future.result(timeout=cls.TIMEOUT)
                    validations.append(validation)
                except Exception as e:
                    url = future_to_url[future]
                    validations.append(SourceValidation(
                        url=url,
                        is_accessible=False,
                        status_code=None,
                        last_modified=None,
                        content_length=None,
                        response_time_ms=None,
                        error_message=f"Validation timeout: {str(e)}",
                        validation_timestamp=time.time()
                    ))
        
        return validations
    
    @classmethod
    def calculate_confidence_score(cls, validations: List[SourceValidation]) -> float:
        """Calculate confidence score based on source validation results."""
        if not validations:
            return 0.0
            
        accessible_count = sum(1 for v in validations if v.is_accessible)
        total_count = len(validations)
        
        base_score = (accessible_count / total_count) * 100
        
        # Apply additional factors
        recent_sources = sum(1 for v in validations 
                           if v.is_accessible and v.last_modified 
                           and 'android.com' in v.url)
        if recent_sources > 0:
            base_score += min(10, recent_sources * 2)  # Bonus for official Android sources
            
        return min(100.0, base_score)
    
    @classmethod
    def suggest_alternatives_for_failed_sources(cls, failed_validations: List[SourceValidation]) -> List[str]:
        """Suggest alternative sources for failed URLs."""
        suggestions = []
        
        for validation in failed_validations:
            url = validation.url
            parsed = urlparse(url)
            
            if 'source.android.com' in url:
                suggestions.append(f"Try Android Code Search: https://cs.android.com/search?q={parsed.path.split('/')[-1]}")
            elif 'googlesource.com' in url:
                suggestions.append(f"Check if URL moved: {url.replace('/+/', '/+/refs/heads/main/')}")
            else:
                suggestions.append(f"Search for alternative documentation for: {parsed.path.split('/')[-1]}")
                
        return suggestions
    
    @classmethod
    def format_enhanced_summary(cls, result: EnhancedSummaryResult) -> str:
        """Format the enhanced summary with source validation details."""
        lines = [
            f"# Enhanced vHAL Summary: '{result.question}'",
            "",
            f"**Confidence Score:** {result.confidence_score:.1f}% ({result.accessible_sources_count}/{result.total_sources_checked} sources validated)",
            "",
            "## Source Validation Results",
            ""
        ]
        
        # Sort validations by accessibility status
        sorted_validations = sorted(result.source_validations, 
                                   key=lambda x: (not x.is_accessible, x.url))
        
        for validation in sorted_validations:
            status_icon = "✅" if validation.is_accessible else "❌"
            status_text = f"HTTP {validation.status_code}" if validation.status_code else "Failed"
            
            lines.append(f"{status_icon} **{validation.url}**")
            lines.append(f"   Status: {status_text}")
            
            if validation.last_modified:
                lines.append(f"   Last-Modified: {validation.last_modified}")
            if validation.response_time_ms:
                lines.append(f"   Response Time: {validation.response_time_ms:.1f}ms")
            if validation.error_message:
                lines.append(f"   Error: {validation.error_message}")
            lines.append("")
        
        if result.suggestions_for_failed_sources:
            lines.extend([
                "## Alternative Sources for Failed URLs",
                ""
            ])
            for suggestion in result.suggestions_for_failed_sources:
                lines.append(f"- {suggestion}")
            lines.append("")
        
        lines.extend([
            "## Summary Content",
            "",
            result.summary_content,
            "",
            "---",
            f"*Validation performed at: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}*",
            f"*Total sources checked: {result.total_sources_checked} | Accessible: {result.accessible_sources_count} | Cached: {result.cached_sources_count}*"
        ])
        
        return "\n".join(lines)
