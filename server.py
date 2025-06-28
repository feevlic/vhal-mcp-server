from mcp.server.fastmcp import FastMCP
import requests
import threading
from urllib3.util import Retry
from requests.adapters import HTTPAdapter

from scrapers import VhalDocumentationScraper
from database import VhalPropertyDatabase, AndroidSourceLookup
from analyzers import AndroidSourceCodeAnalyzer
from relationships import VhalPropertyRelationshipAnalyzer
from summarizers import VhalSummarizer
from code_generator import VhalCodeGenerator
from pr_generator import VhalPullRequestGenerator

class SessionManager:
    """Centralized session manager for all HTTP requests."""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize optimized session with connection pooling."""
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=2,
            backoff_factor=0.1,
            status_forcelist=[429, 500, 502, 503, 504],
            respect_retry_after_header=False  # Don't wait too long
        )
        
        # Configure adapter with connection pooling
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20,
            pool_block=False
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set optimized headers
        self.session.headers.update({
            'User-Agent': 'vHAL-MCP-Server/1.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=300'  # 5 minute cache hint
        })
    
    def get_session(self):
        """Get the shared session instance."""
        return self.session

_session_manager = SessionManager()

# Pre-initialize critical components
def _initialize_components():
    """Pre-initialize components for faster first-time access."""
    try:
        # Pre-build database indexes
        VhalPropertyDatabase._build_indexes()
        
        # Pre-warm the scraper with session
        VhalDocumentationScraper._session = _session_manager.get_session()
        AndroidSourceCodeAnalyzer._session = _session_manager.get_session()
        
        # Pre-cache known pages
        VhalDocumentationScraper.discover_pages()
        
    except Exception:
        pass  # Fail silently during initialization

# Initialize components in background
import threading
initialization_thread = threading.Thread(target=_initialize_components, daemon=True)
initialization_thread.start()


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
        # Use optimized parallel scraping with cached session
        if VhalDocumentationScraper._session is None:
            VhalDocumentationScraper._session = _session_manager.get_session()
        pages = VhalDocumentationScraper.discover_pages()
        
        # Parallel scraping for much better performance
        content_sections = VhalDocumentationScraper.scrape_pages_parallel(pages)
        
        if not content_sections:
            return "Unable to fetch vHAL documentation. Please check your internet connection or try again later."
        
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


@mcp.tool()
def discover_related_properties(property_or_category: str) -> str:
    """Discover related properties, dependencies, and implementation order for vHAL properties.
    
    Args:
        property_or_category: Property name (e.g., "SEAT_MEMORY_SELECT") or category (e.g., "SEAT_MEMORY", "HVAC_BASIC")
        
    Returns:
        Comprehensive analysis of related properties, dependencies, and suggested implementation order
    """
    try:
        ecosystem = VhalPropertyRelationshipAnalyzer.analyze_property_relationships(property_or_category)
        
        result_parts = [
            f"Property Ecosystem Analysis for: '{ecosystem.primary_property}'\n",
            "=" * 70,
            f"\nCategory: {ecosystem.category.value}"
        ]
        
        # Related Properties Section
        if ecosystem.related_properties:
            result_parts.append("\n\nRelated Properties:")
            
            # Group by relationship type and priority
            grouped_props = {}
            for prop in ecosystem.related_properties:
                if prop.relationship_type not in grouped_props:
                    grouped_props[prop.relationship_type] = []
                grouped_props[prop.relationship_type].append(prop)
            
            # Sort relationship types by priority
            priority_order = ["core_properties", "movement_properties", "dependent_properties", 
                            "related_properties", "optional_properties", "advanced_properties"]
            
            for rel_type in priority_order:
                if rel_type in grouped_props:
                    props = sorted(grouped_props[rel_type], key=lambda x: x.priority)
                    result_parts.append(f"\n### {rel_type.replace('_', ' ').title()}:")
                    
                    for prop in props:
                        # Get property ID if available
                        prop_id = ""
                        for category, properties in VhalPropertyDatabase.PROPERTIES.items():
                            if prop.property_name in properties:
                                prop_id = f" ({properties[prop.property_name]})"
                                break
                        
                        result_parts.append(f"  • {prop.property_name}{prop_id}")
                        result_parts.append(f"    {prop.description}")
        
        # Dependencies Section
        if ecosystem.dependencies:
            result_parts.append("\n\nDependencies:")
            for prop, deps in ecosystem.dependencies.items():
                result_parts.append(f"\n• {prop} depends on:")
                for dep in deps:
                    result_parts.append(f"  - {dep}")
        
        # Implementation Steps Section
        if ecosystem.implementation_steps:
            result_parts.append("\n\nSuggested Implementation Order:")
            
            for step in ecosystem.implementation_steps:
                result_parts.append(f"\n### Step {step.step_number}: {step.title}")
                result_parts.append(f"**Description:** {step.description}")
                
                if step.properties:
                    result_parts.append("\n**Properties to implement:**")
                    for prop in step.properties:
                        # Get property ID
                        prop_id = ""
                        for category, properties in VhalPropertyDatabase.PROPERTIES.items():
                            if prop in properties:
                                prop_id = f" ({properties[prop]})"
                                break
                        result_parts.append(f"  • {prop}{prop_id}")
                
                if step.dependencies:
                    result_parts.append("\n**Dependencies:**")
                    for dep in step.dependencies:
                        result_parts.append(f"  • {dep}")
                
                if step.considerations:
                    result_parts.append("\n**Implementation considerations:**")
                    for consideration in step.considerations:
                        result_parts.append(f"  • {consideration}")
                        
                result_parts.append("")  # Add spacing
        
        # Usage Notes Section
        if ecosystem.usage_notes:
            result_parts.append("\nImplementation Notes:")
            for note in ecosystem.usage_notes:
                result_parts.append(f"• {note}")
        
        # Additional Resources Section
        result_parts.extend([
            "\n\nAdditional Resources:",
            "• Use `lookup_android_source_code()` to find implementation examples",
            "• Use `summarize_vhal()` for detailed documentation on specific topics",
            "• Refer to Android vHAL documentation: https://source.android.com/docs/automotive/vhal"
        ])
        
        return "\n".join(result_parts)
        
    except Exception as e:
        return f"Error analyzing property relationships: {str(e)}"


@mcp.tool()
def generate_vhal_implementation_code(
    name: str,
    property_id: str,
    property_type: str,
    group: str,
    access: str,
    change_mode: str,
    description: str,
    units: str = None,
    min_value: float = None,
    max_value: float = None,
    areas: list = None,
    enum_values: dict = None,
    dependencies: list = None,
    sample_rate_hz: float = None
) -> str:
    """Generate complete VHAL property implementation code for Android Automotive OS (AAOS).
    
    This tool generates all necessary files, configurations, tests, and documentation
    needed to implement a new VHAL property from scratch.
    
    Args:
        name: Property name (e.g., "HVAC_STEERING_WHEEL_HEAT")
        property_id: Unique property ID (hex format, e.g., "0x15400A03")
        property_type: Data type (BOOLEAN, INT32, INT64, FLOAT, STRING, BYTES, *_VEC, MIXED)
        group: Property group (HVAC, SEAT, LIGHTS, POWER, CLIMATE, etc.)
        access: Access mode (READ, WRITE, READ_WRITE)
        change_mode: Change mode (STATIC, ON_CHANGE, CONTINUOUS)
        description: Property description for documentation
        units: Optional units (e.g., "celsius", "rpm")
        min_value: Optional minimum value for numeric types
        max_value: Optional maximum value for numeric types
        areas: Optional list of vehicle areas/zones
        enum_values: Optional dict of enum names and values for INT32 enum properties
        dependencies: Optional list of dependent property names
        sample_rate_hz: Optional sample rate for continuous properties
        
    Returns:
        Complete implementation including all generated files, summary, and implementation guide
    """
    try:
        # Generate the complete implementation
        result = VhalCodeGenerator.generate_vhal_implementation(
            name=name,
            property_id=property_id,
            property_type=property_type,
            group=group,
            access=access,
            change_mode=change_mode,
            description=description,
            units=units,
            min_value=min_value,
            max_value=max_value,
            areas=areas,
            enum_values=enum_values,
            dependencies=dependencies,
            sample_rate_hz=sample_rate_hz
        )
        
        # Format the output
        output_parts = [
            f"VHAL Implementation Generated for: {result.property_name}\n",
            "=" * 80,
            "\n## SUMMARY",
            result.summary,
            "\n\n## GENERATED FILES",
            "\nThe following code sections have been generated:"
        ]
        
        # Add each generated file
        for i, file in enumerate(result.files, 1):
            output_parts.extend([
                f"\n\n### {i}. {file.description}",
                f"**File:** `{file.path}`",
                f"\n```{VhalCodeGenerator._get_file_extension(file.path)}",
                file.content,
                "```"
            ])
        
        # Add implementation guide
        output_parts.extend([
            "\n\n## IMPLEMENTATION GUIDE",
            result.implementation_guide
        ])
        
        return "\n".join(output_parts)
        
    except Exception as e:
        return f"Error generating VHAL implementation: {str(e)}"


@mcp.tool()
def generate_vhal_pr_message(
    property_name: str,
    property_id: str,
    property_type: str,
    group: str,
    access: str,
    change_mode: str,
    description: str,
    units: str = None,
    min_value: float = None,
    max_value: float = None,
    areas: list = None,
    enum_values: dict = None,
    dependencies: list = None,
    sample_rate_hz: float = None,
    breaking_change: bool = False,
    jira_ticket: str = None,
    reviewer_suggestions: list = None
) -> str:
    """Generate a comprehensive pull request message for VHAL property implementation.
    
    This tool creates a structured, professional PR description that includes all necessary
    details about the VHAL property, implementation changes, testing requirements, and
    review checklist.
    
    Args:
        property_name: Property name (e.g., "HVAC_STEERING_WHEEL_HEAT")
        property_id: Unique property ID (hex format, e.g., "0x15400A03")
        property_type: Data type (BOOLEAN, INT32, INT64, FLOAT, STRING, BYTES, *_VEC, MIXED)
        group: Property group (HVAC, SEAT, LIGHTS, POWER, CLIMATE, etc.)
        access: Access mode (READ, WRITE, READ_WRITE)
        change_mode: Change mode (STATIC, ON_CHANGE, CONTINUOUS)
        description: Property description for documentation
        units: Optional units (e.g., "celsius", "rpm")
        min_value: Optional minimum value for numeric types
        max_value: Optional maximum value for numeric types
        areas: Optional list of vehicle areas/zones
        enum_values: Optional dict of enum names and values for INT32 enum properties
        dependencies: Optional list of dependent property names
        sample_rate_hz: Optional sample rate for continuous properties
        breaking_change: Whether this introduces breaking changes (default: False)
        jira_ticket: Optional JIRA ticket reference
        reviewer_suggestions: Optional list of specific review points
        
    Returns:
        Complete pull request message ready to copy-paste into GitHub/GitLab
    """
    try:
        # Generate the PR message structure
        pr_message = VhalPullRequestGenerator.generate_pr_message(
            property_name=property_name,
            property_id=property_id,
            property_type=property_type,
            group=group,
            access=access,
            change_mode=change_mode,
            description=description,
            units=units,
            min_value=min_value,
            max_value=max_value,
            areas=areas,
            enum_values=enum_values,
            dependencies=dependencies,
            sample_rate_hz=sample_rate_hz,
            breaking_change=breaking_change,
            jira_ticket=jira_ticket,
            reviewer_suggestions=reviewer_suggestions
        )
        
        # Format the complete PR message
        formatted_message = VhalPullRequestGenerator.format_pr_message(pr_message)
        
        # Add header and instructions
        output_parts = [
            "# Pull Request Message Generated",
            "",
            "## PR Title",
            f"```",
            pr_message.title,
            f"```",
            "",
            "## PR Description",
            "Copy and paste the following into your pull request:",
            "",
            "```markdown",
            formatted_message,
            "```",
            "",
            "## Usage Instructions",
            "1. **Copy the PR Title** from the first code block",
            "2. **Copy the PR Description** from the second code block",
            "3. **Paste into your GitHub/GitLab PR**",
            "4. **Review and customize** any sections as needed",
            "5. **Check off completed items** in the checklist as you go",
            "",
            "## Features Included",
            "-  **Professional Title** with appropriate emoji and property type",
            "-  **Comprehensive Description** with motivation and overview",
            "-  **Detailed Changes Summary** listing all modified files",
            "-  **Technical Specifications** with complete property details",
            "-  **Testing Coverage** with specific test cases and commands",
            "-  **Documentation Links** and usage examples",
            "-  **Review Checklist** for thorough code review",
            "-  **Breaking Changes** section (if applicable)",
            "",
            "Ready to streamline your VHAL development workflow! 🚀"
        ]
        
        return "\n".join(output_parts)
        
    except Exception as e:
        return f"Error generating PR message: {str(e)}"


@mcp.tool()
def analyze_vhal_implementation(property_name: str, android_version: str = None) -> str:
    """Analyze Android source code to show how a vHAL property is implemented, including actual source code, file locations, and usage examples.
    
    Args:
        property_name: The vHAL property name to analyze (e.g., "HVAC_STEERING_WHEEL_HEAT", "SEAT_MEMORY_SELECT")
        android_version: Optional Android version to analyze (e.g., "android13", "android14", "android15", "android16")
                        If not specified, uses Android 15 as default. Supported versions:
                        - android13: Android 13 (first vHAL introduction)
                        - android14: Android 14 (major vHAL changes)
                        - android15: Android 15 (current stable, default)
                        - android16: Android 16 (latest)
        
    Returns:
        Comprehensive analysis of the property implementation including source code, dependencies, and usage examples
    """
    try:
        # Ensure analyzer has access to optimized session
        if AndroidSourceCodeAnalyzer._session is None:
            AndroidSourceCodeAnalyzer._session = _session_manager.get_session()
        analysis = AndroidSourceCodeAnalyzer.analyze_property_implementation(property_name, android_version)
        
        result_parts = [
            f"vHAL Implementation Analysis for: '{analysis.property_name}'\n",
            "=" * 80,
            f"\nProperty ID: {analysis.property_id}"
        ]
        
        # Source Files Section
        if analysis.source_files:
            result_parts.append("\n\nSource Files Analysis:")
            
            for i, file in enumerate(analysis.source_files, 1):
                result_parts.append(f"\n### {i}. {file.filename}")
                result_parts.append(f"**Purpose:** {file.purpose}")
                result_parts.append(f"**Language:** {file.language}")
                result_parts.append(f"**Lines:** {file.line_count}")
                result_parts.append(f"**Path:** {file.path}")
                result_parts.append(f"**URL:** {file.url}")
                
                if file.content and file.language != "error":
                    # Show first 30 lines of code with line numbers
                    lines = file.content.splitlines()[:30]
                    if lines:
                        result_parts.append(f"\n**Source Code Preview:**")
                        result_parts.append(f"```{file.language}")
                        for line_num, line in enumerate(lines, 1):
                            result_parts.append(f"{line_num:4d}: {line}")
                        if len(file.content.splitlines()) > 30:
                            result_parts.append("...")
                            result_parts.append(f"[File continues for {file.line_count - 30} more lines]")
                        result_parts.append("```")
                elif file.language == "error":
                    result_parts.append(f"\n**Error:** {file.content}")
                
                result_parts.append("")  # Add spacing
        
        # Implementation Details Section
        if analysis.implementation_details:
            result_parts.append("\n\nImplementation Details:")
            for detail_key, detail_value in analysis.implementation_details.items():
                result_parts.append(f"\n### {detail_key.replace('_', ' ').title()}")
                result_parts.append(detail_value)
        
        # Dependencies Section
        if analysis.dependencies:
            result_parts.append("\n\nDependencies:")
            for dependency in analysis.dependencies:
                result_parts.append(f"• {dependency}")
        
        # Usage Examples Section
        if analysis.usage_examples:
            result_parts.append("\n\nUsage Examples:")
            for i, example in enumerate(analysis.usage_examples, 1):
                result_parts.append(f"\n### Example {i}:")
                result_parts.append(f"```cpp\n{example}\n```")
        
        # Related Files Section
        if analysis.related_files:
            result_parts.append("\n\nRelated Implementation Files:")
            for related_file in analysis.related_files:
                result_parts.append(f"• {related_file}")
        
        # Documentation Links Section
        if analysis.documentation_links:
            result_parts.append("\n\nDocumentation & Resources:")
            for link in analysis.documentation_links:
                result_parts.append(f"• {link}")
        
        # Implementation Tips Section
        result_parts.extend([
            "\n\nImplementation Tips:",
            "• Study the AIDL definitions to understand data types and structure",
            "• Check DefaultProperties.cpp for configuration examples",
            "• Use the emulator implementation as a reference for testing",
            "• Follow the pattern established in existing properties for consistency",
            "• Pay attention to area mapping and access control requirements"
        ])
        
        return "\n".join(result_parts)
        
    except Exception as e:
        return f"Error analyzing vHAL implementation: {str(e)}"


# Make sure the server can be run directly
if __name__ == "__main__":
    mcp.run()
