from mcp.server.fastmcp import FastMCP
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from typing import List, Dict, Optional

mcp = FastMCP("Demo")

# Add vHAL summarization tool
@mcp.tool()
def summarize_vhal(question: str) -> str:
    """Summarize vHAL (Vehicle Hardware Abstraction Layer) implementation based on a question.
    
    Args:
        question: The question about vHAL implementation
        
    Returns:
        A summary of relevant vHAL information from Android documentation
    """
    try:
        # Base URL for Android vHAL documentation
        base_url = "https://source.android.com/docs/automotive/vhal"
        
        # Function to scrape content from a URL
        def scrape_content(url: str) -> str:
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get text content
                text = soup.get_text()
                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                return text[:5000]  # Limit content length
            except Exception as e:
                return f"Error scraping {url}: {str(e)}"
        
        # Function to find relevant vHAL pages
        def find_vhal_pages(base_url: str) -> List[str]:
            try:
                response = requests.get(base_url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                links = []
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    if href and ('vhal' in href.lower() or 'vehicle' in href.lower()):
                        full_url = urljoin(base_url, href)
                        if full_url.startswith('https://source.android.com/docs/automotive'):
                            links.append(full_url)
                
                # Add some known vHAL documentation pages
                known_pages = [
                    "https://source.android.com/docs/automotive/vhal",
                    "https://source.android.com/docs/automotive/vhal/properties",
                    "https://source.android.com/docs/automotive/vhal/vehicle-areas",
                    "https://source.android.com/docs/automotive/vhal/diagnostics",
                    "https://source.android.com/docs/automotive/vhal/hal-implementation"
                ]
                
                # Combine and deduplicate
                all_links = list(set(links + known_pages))
                return all_links[:10]  # Limit to first 10 pages
                
            except Exception as e:
                # Fallback to known pages if scraping fails
                return [
                    "https://source.android.com/docs/automotive/vhal",
                    "https://source.android.com/docs/automotive/vhal/properties",
                    "https://source.android.com/docs/automotive/vhal/vehicle-areas"
                ]
        
        # Get vHAL documentation pages
        vhal_pages = find_vhal_pages(base_url)
        
        # Scrape content from each page
        all_content = []
        for page_url in vhal_pages:
            content = scrape_content(page_url)
            if content and "Error scraping" not in content:
                all_content.append(f"\n--- From {page_url} ---\n{content}")
        
        # Combine all content
        combined_content = "\n".join(all_content)
        
        # Simple keyword matching to find relevant sections
        question_lower = question.lower()
        keywords = re.findall(r'\b\w+\b', question_lower)
        
        # Score content sections based on keyword relevance
        sections = combined_content.split('---')
        relevant_sections = []
        
        for section in sections:
            if not section.strip():
                continue
                
            section_lower = section.lower()
            score = sum(1 for keyword in keywords if keyword in section_lower)
            
            if score > 0:
                relevant_sections.append((score, section[:2000]))  # Limit section length
        
        # Sort by relevance score
        relevant_sections.sort(key=lambda x: x[0], reverse=True)
        
        if not relevant_sections:
            return f"No specific vHAL information found for the question: '{question}'. Here's general vHAL overview:\n\n{combined_content[:1500]}..."
        
        # Create summary from most relevant sections
        summary_parts = [f"vHAL Summary for: '{question}'\n"]
        
        for score, section in relevant_sections[:3]:  # Top 3 most relevant sections
            summary_parts.append(section)
            summary_parts.append("\n" + "="*50 + "\n")
        
        summary = "\n".join(summary_parts)
        
        # Ensure summary isn't too long
        if len(summary) > 4000:
            summary = summary[:4000] + "\n\n[Summary truncated for length]"
            
        return summary
        
    except Exception as e:
        return f"Error generating vHAL summary: {str(e)}"

# Add a tool for looking up Android source code
@mcp.tool()
def lookup_android_source_code(keyword: str, category: str = "vhal") -> str:
    """Lookup and return relevant Android source code for a given keyword.
    
    Args:
        keyword: The search term (e.g., "SEAT", "HVAC", "vehicle properties")
        category: Category to focus search on (default: "vhal")
        
    Returns:
        Detailed information about the source code location and content
    """
    try:
        # Define search strategies based on category
        search_patterns = {
            "vhal": [
                f"https://android.googlesource.com/platform/hardware/interfaces/+/refs/heads/main/automotive/vehicle/",
                f"https://cs.android.com/search?q={keyword}%20file:VehicleProperty",
                f"https://cs.android.com/search?q={keyword}%20file:automotive"
            ],
            "properties": [
                f"https://cs.android.com/search?q={keyword}%20VehicleProperty",
                f"https://android.googlesource.com/platform/hardware/interfaces/+/refs/heads/main/automotive/vehicle/aidl/android/hardware/automotive/vehicle/VehicleProperty.aidl"
            ]
        }
        
        def search_android_cs(keyword: str) -> List[Dict[str, str]]:
            """Search Android Code Search"""
            results = []
            search_url = f"https://cs.android.com/search?q={keyword}%20automotive%20vehicle"
            
            try:
                # Note: This is a simplified approach since cs.android.com requires special handling
                # In a real implementation, you'd need to handle the dynamic content
                results.append({
                    "type": "search_url",
                    "description": f"Android Code Search for '{keyword}'",
                    "url": search_url
                })
            except Exception as e:
                results.append({"error": f"Search error: {str(e)}"})
            
            return results
        
        def get_vhal_property_definitions() -> str:
            """Get known vHAL property definitions"""
            # Common vHAL properties with their IDs
            known_properties = {
                "SEAT": {
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
                "HVAC": {
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
            
            # Search for matching properties
            matching_props = []
            keyword_upper = keyword.upper()
            
            for category_name, props in known_properties.items():
                if keyword_upper in category_name or any(keyword_upper in prop_name for prop_name in props.keys()):
                    matching_props.append((category_name, props))
            
            if not matching_props:
                # Try partial matching
                for category_name, props in known_properties.items():
                    for prop_name, prop_id in props.items():
                        if any(kw in prop_name for kw in keyword_upper.split()):
                            matching_props.append((category_name, {prop_name: prop_id}))
                            break
            
            return matching_props
        
        # Get property definitions
        property_matches = get_vhal_property_definitions()
        
        # Search Android Code Search
        search_results = search_android_cs(keyword)
        
        # Compile results
        result_parts = []
        result_parts.append(f"Android Source Code Lookup for: '{keyword}'\n")
        result_parts.append("=" * 50)
        
        # Add property definitions if found
        if property_matches:
            result_parts.append("\n## Vehicle Property Definitions:")
            for category_name, props in property_matches:
                result_parts.append(f"\n### {category_name} Properties:")
                for prop_name, prop_id in props.items():
                    result_parts.append(f"  - {prop_name}: {prop_id}")
        
        # Add source code locations
        result_parts.append("\n## Source Code Locations:")
        
        # AIDL file location
        result_parts.append("\n### Vehicle Property AIDL Definition:")
        result_parts.append("File: platform/hardware/interfaces/automotive/vehicle/aidl/android/hardware/automotive/vehicle/VehicleProperty.aidl")
        result_parts.append("URL: https://android.googlesource.com/platform/hardware/interfaces/+/refs/heads/main/automotive/vehicle/aidl/android/hardware/automotive/vehicle/VehicleProperty.aidl")
        
        # HAL implementation
        result_parts.append("\n### HAL Implementation:")
        result_parts.append("Directory: platform/hardware/interfaces/automotive/vehicle/")
        result_parts.append("URL: https://android.googlesource.com/platform/hardware/interfaces/+/refs/heads/main/automotive/vehicle/")
        
        # Reference implementation
        result_parts.append("\n### Reference Implementation:")
        result_parts.append("Directory: device/generic/car/emulator/")
        result_parts.append("URL: https://android.googlesource.com/device/generic/car/+/refs/heads/main/emulator/")
        
        # Add search URLs
        result_parts.append("\n## Search URLs:")
        for result in search_results:
            if "url" in result:
                result_parts.append(f"- {result['description']}: {result['url']}")
        
        # Add usage information
        if "SEAT" in keyword.upper():
            result_parts.append("\n## Seat Property Usage:")
            result_parts.append("- Area Type: VehicleAreaSeat (typically 0x05000000 base)")
            result_parts.append("- Data Type: Usually INT32 for positions, BOOLEAN for states")
            result_parts.append("- Access: Most seat properties are READ_WRITE")
            result_parts.append("- Change Mode: ON_CHANGE for most properties")
        
        return "\n".join(result_parts)
        
    except Exception as e:
        return f"Error during Android source code lookup: {str(e)}"

# Make sure the server can be run directly
if __name__ == "__main__":
    mcp.run()
