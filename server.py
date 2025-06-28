from mcp.server.fastmcp import FastMCP
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class VhalCategory(Enum):
    SEAT = "SEAT"
    HVAC = "HVAC"
    GENERAL = "GENERAL"


@dataclass
class VhalProperty:
    name: str
    id: str
    category: VhalCategory
    description: str = ""


@dataclass
class SearchResult:
    url: str
    description: str
    content: Optional[str] = None


class VhalDocumentationScraper:
    BASE_URL = "https://source.android.com/docs/automotive/vhal"
    CONTENT_LIMIT = 5000
    TIMEOUT = 10
    
    KNOWN_PAGES = [
        "https://source.android.com/docs/automotive/vhal",
        "https://source.android.com/docs/automotive/vhal/properties", 
        "https://source.android.com/docs/automotive/vhal/vehicle-areas",
        "https://source.android.com/docs/automotive/vhal/diagnostics",
        "https://source.android.com/docs/automotive/vhal/hal-implementation"
    ]
    
    @staticmethod
    def scrape_page(url: str) -> Optional[str]:
        try:
            response = requests.get(url, timeout=VhalDocumentationScraper.TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            for element in soup(["script", "style"]):
                element.decompose()
            
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = ' '.join(chunk for chunk in chunks if chunk)
            
            return clean_text[:VhalDocumentationScraper.CONTENT_LIMIT]
        except Exception:
            return None
    
    @staticmethod
    def discover_pages() -> List[str]:
        try:
            response = requests.get(VhalDocumentationScraper.BASE_URL, 
                                  timeout=VhalDocumentationScraper.TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            discovered_links = []
            
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href and ('vhal' in href.lower() or 'vehicle' in href.lower()):
                    full_url = urljoin(VhalDocumentationScraper.BASE_URL, href)
                    if full_url.startswith('https://source.android.com/docs/automotive'):
                        discovered_links.append(full_url)
            
            all_links = list(set(discovered_links + VhalDocumentationScraper.KNOWN_PAGES))
            return all_links[:10]
        except Exception:
            return VhalDocumentationScraper.KNOWN_PAGES


class VhalPropertyDatabase:
    PROPERTIES = {
        VhalCategory.SEAT: {
            "SEAT_MEMORY_SELECT": "0x0B56",
            "SEAT_MEMORY_SET": "0x0B57",
            "SEAT_BELT_BUCKLED": "0x0B58",
            "SEAT_BELT_HEIGHT_POS": "0x0B59",
            "SEAT_BELT_HEIGHT_MOVE": "0x0B5A",
            "SEAT_FORE_AFT_POS": "0x0B5B",
            "SEAT_FORE_AFT_MOVE": "0x0B5C",
            "SEAT_BACKREST_ANGLE_1_POS": "0x0B5D",
            "SEAT_BACKREST_ANGLE_1_MOVE": "0x0B5E",
            "SEAT_BACKREST_ANGLE_2_POS": "0x0B5F",
            "SEAT_BACKREST_ANGLE_2_MOVE": "0x0B60",
            "SEAT_HEIGHT_POS": "0x0B61",
            "SEAT_HEIGHT_MOVE": "0x0B62",
            "SEAT_DEPTH_POS": "0x0B63",
            "SEAT_DEPTH_MOVE": "0x0B64",
            "SEAT_TILT_POS": "0x0B65",
            "SEAT_TILT_MOVE": "0x0B66",
            "SEAT_LUMBAR_FORE_AFT_POS": "0x0B67",
            "SEAT_LUMBAR_FORE_AFT_MOVE": "0x0B68",
            "SEAT_LUMBAR_SIDE_SUPPORT_POS": "0x0B69",
            "SEAT_LUMBAR_SIDE_SUPPORT_MOVE": "0x0B6A",
            "SEAT_HEADREST_HEIGHT_POS": "0x0B6B",
            "SEAT_HEADREST_HEIGHT_MOVE": "0x0B6C",
            "SEAT_HEADREST_ANGLE_POS": "0x0B6D",
            "SEAT_HEADREST_ANGLE_MOVE": "0x0B6E",
            "SEAT_HEADREST_FORE_AFT_POS": "0x0B6F",
            "SEAT_HEADREST_FORE_AFT_MOVE": "0x0B70"
        },
        VhalCategory.HVAC: {
            "HVAC_FAN_SPEED": "0x0A01",
            "HVAC_FAN_DIRECTION": "0x0A02",
            "HVAC_TEMPERATURE_CURRENT": "0x0A03",
            "HVAC_TEMPERATURE_SET": "0x0A04",
            "HVAC_DEFROSTER": "0x0A05",
            "HVAC_AC_ON": "0x0A06",
            "HVAC_MAX_AC_ON": "0x0A07",
            "HVAC_MAX_DEFROST_ON": "0x0A08",
            "HVAC_RECIRC_ON": "0x0A09",
            "HVAC_DUAL_ON": "0x0A0A",
            "HVAC_AUTO_ON": "0x0A0B",
            "HVAC_SEAT_TEMPERATURE": "0x0A0C",
            "HVAC_SIDE_MIRROR_HEAT": "0x0A0D",
            "HVAC_STEERING_WHEEL_HEAT": "0x0A0E",
            "HVAC_TEMPERATURE_DISPLAY_UNITS": "0x0A0F",
            "HVAC_ACTUAL_FAN_SPEED_RPM": "0x0A10",
            "HVAC_POWER_ON": "0x0A11",
            "HVAC_FAN_DIRECTION_AVAILABLE": "0x0A12",
            "HVAC_AUTO_RECIRC_ON": "0x0A13",
            "HVAC_SEAT_VENTILATION": "0x0A14"
        }
    }
    
    @classmethod
    def search_properties(cls, keyword: str) -> List[VhalProperty]:
        keyword_upper = keyword.upper()
        matches = []
        
        for category, properties in cls.PROPERTIES.items():
            if keyword_upper in category.value:
                for name, prop_id in properties.items():
                    matches.append(VhalProperty(name, prop_id, category))
                continue
            
            for name, prop_id in properties.items():
                if keyword_upper in name or any(kw in name for kw in keyword_upper.split()):
                    matches.append(VhalProperty(name, prop_id, category))
        
        return matches


class AndroidSourceLookup:
    AIDL_URL = "https://android.googlesource.com/platform/hardware/interfaces/+/refs/heads/main/automotive/vehicle/aidl/android/hardware/automotive/vehicle/VehicleProperty.aidl"
    HAL_BASE_URL = "https://android.googlesource.com/platform/hardware/interfaces/+/refs/heads/main/automotive/vehicle/"
    REFERENCE_IMPL_URL = "https://android.googlesource.com/device/generic/car/+/refs/heads/main/emulator/"
    
    @staticmethod
    def generate_search_url(keyword: str) -> str:
        return f"https://cs.android.com/search?q={keyword}%20automotive%20vehicle"
    
    @classmethod
    def get_source_locations(cls) -> List[SearchResult]:
        return [
            SearchResult(
                url=cls.AIDL_URL,
                description="Vehicle Property AIDL Definition"
            ),
            SearchResult(
                url=cls.HAL_BASE_URL,
                description="HAL Implementation Directory"
            ),
            SearchResult(
                url=cls.REFERENCE_IMPL_URL,
                description="Reference Implementation"
            )
        ]


class VhalSummarizer:
    MAX_SECTIONS = 3
    SECTION_LIMIT = 2000
    SUMMARY_LIMIT = 4000
    
    @staticmethod
    def extract_keywords(question: str) -> List[str]:
        return re.findall(r'\b\w+\b', question.lower())
    
    @staticmethod
    def score_content(content: str, keywords: List[str]) -> int:
        content_lower = content.lower()
        return sum(1 for keyword in keywords if keyword in content_lower)
    
    @classmethod
    def summarize_documentation(cls, question: str, content_sections: List[str]) -> str:
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


mcp = FastMCP("vHAL MCP Server")


@mcp.tool()
def summarize_vhal(question: str) -> str:
    """Summarize vHAL implementation based on a question.
    
    Args:
        question: Question about vHAL implementation
        
    Returns:
        Summary of relevant vHAL information from Android documentation
    """
    try:
        pages = VhalDocumentationScraper.discover_pages()
        content_sections = []
        
        for page_url in pages:
            content = VhalDocumentationScraper.scrape_page(page_url)
            if content:
                content_sections.append(content)
        
        return VhalSummarizer.summarize_documentation(question, content_sections)
        
    except Exception as e:
        return f"Error generating vHAL summary: {str(e)}"

# Add a tool for looking up Android source code
@mcp.tool()
def lookup_android_source_code(keyword: str, category: str = "vhal") -> str:
    """Lookup Android source code for a given keyword.
    
    Args:
        keyword: Search term (e.g., "SEAT", "HVAC", "vehicle properties")
        category: Category to focus search on (default: "vhal")
        
    Returns:
        Detailed information about the source code location and content
    """
    try:
        property_matches = VhalPropertyDatabase.search_properties(keyword)
        source_locations = AndroidSourceLookup.get_source_locations()
        search_url = AndroidSourceLookup.generate_search_url(keyword)
        
        result_parts = [
            f"Android Source Code Lookup for: '{keyword}'\n",
            "=" * 50
        ]
        
        if property_matches:
            result_parts.append("\n## Vehicle Property Definitions:")
            
            categories = {}
            for prop in property_matches:
                if prop.category not in categories:
                    categories[prop.category] = []
                categories[prop.category].append(prop)
            
            for category, props in categories.items():
                result_parts.append(f"\n### {category.value} Properties:")
                for prop in props:
                    result_parts.append(f"  - {prop.name}: {prop.id}")
        
        result_parts.append("\n## Source Code Locations:")
        for location in source_locations:
            result_parts.append(f"\n### {location.description}:")
            result_parts.append(f"URL: {location.url}")
        
        result_parts.append(f"\n## Search URL:")
        result_parts.append(f"Android Code Search: {search_url}")
        
        if any("SEAT" in prop.name for prop in property_matches):
            result_parts.extend([
                "\n## Seat Property Usage:",
                "- Area Type: VehicleAreaSeat (typically 0x05000000 base)",
                "- Data Type: Usually INT32 for positions, BOOLEAN for states",
                "- Access: Most seat properties are READ_WRITE",
                "- Change Mode: ON_CHANGE for most properties"
            ])
        
        return "\n".join(result_parts)
        
    except Exception as e:
        return f"Error during Android source code lookup: {str(e)}"

# Make sure the server can be run directly
if __name__ == "__main__":
    mcp.run()
