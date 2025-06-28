"""vHAL MCP Server - Main server implementation.

This module provides MCP tools for Android vHAL (Vehicle Hardware Abstraction Layer)
analysis and documentation. It uses modular components for clean separation of concerns.
"""
from mcp.server.fastmcp import FastMCP

# Import modular components
from scrapers import VhalDocumentationScraper
from database import VhalPropertyDatabase, AndroidSourceLookup
from analyzers import AndroidSourceCodeAnalyzer
from relationships import VhalPropertyRelationshipAnalyzer
from summarizers import VhalSummarizer


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
        # Use optimized parallel scraping
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
def analyze_vhal_implementation(property_name: str) -> str:
    """Analyze Android source code to show how a vHAL property is implemented, including actual source code, file locations, and usage examples.
    
    Args:
        property_name: The vHAL property name to analyze (e.g., "HVAC_STEERING_WHEEL_HEAT", "SEAT_MEMORY_SELECT")
        
    Returns:
        Comprehensive analysis of the property implementation including source code, dependencies, and usage examples
    """
    try:
        analysis = AndroidSourceCodeAnalyzer.analyze_property_implementation(property_name)
        
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
