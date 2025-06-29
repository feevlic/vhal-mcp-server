#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced source validation MCP tool.
This shows how the new tool provides transparency and validation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from vhal_mcp_server.core.source_validator import VhalSourceValidator, SourceValidation, EnhancedSummaryResult
from vhal_mcp_server.core.scrapers import VhalDocumentationScraper
from vhal_mcp_server.utils.summarizers import VhalSummarizer
import time

def test_enhanced_summary():
    """Test the enhanced summary with source validation."""
    print("🔍 Testing Enhanced vHAL Summary with Source Validation\n")
    
    # Example question
    question = "How do I implement HVAC temperature control in Android Automotive?"
    
    print(f"Question: {question}\n")
    print("=" * 80)
    
    # Discover some test sources
    test_sources = [
        "https://source.android.com/docs/automotive/vhal",
        "https://source.android.com/docs/automotive/vhal/properties",
        "https://nonexistent-url.example.com/test",  # This should fail
        "https://httpstat.us/404",  # This should return 404
    ]
    
    print("📋 Testing source validation...")
    
    # Validate sources
    validations = VhalSourceValidator.validate_sources_parallel(test_sources)
    
    # Create mock summary content (in real implementation, this comes from scraper)
    summary_content = f"""
vHAL Summary for: '{question}'

HVAC temperature control in Android Automotive is implemented through the Vehicle Hardware Abstraction Layer (vHAL) using specific properties defined in the VehicleProperty.aidl file.

Key Properties:
- HVAC_TEMPERATURE_SET (0x15200001): Sets target temperature for HVAC zones
- HVAC_TEMPERATURE_ACTUAL (0x15200002): Reports actual temperature readings
- HVAC_POWER_ON (0x15200005): Controls HVAC system power state

Implementation involves:
1. Defining property configurations in DefaultProperties.json
2. Implementing HAL methods in the vehicle HAL service
3. Creating appropriate area configurations for different zones
4. Setting up proper access controls and change modes

Example usage shows setting temperature to 22°C for driver zone through the vHAL interface.
"""
    
    # Calculate metrics
    confidence_score = VhalSourceValidator.calculate_confidence_score(validations)
    accessible_count = sum(1 for v in validations if v.is_accessible)
    failed_validations = [v for v in validations if not v.is_accessible]
    suggestions = VhalSourceValidator.suggest_alternatives_for_failed_sources(failed_validations)
    
    # Create enhanced result
    enhanced_result = EnhancedSummaryResult(
        question=question,
        summary_content=summary_content,
        source_validations=validations,
        confidence_score=confidence_score,
        total_sources_checked=len(test_sources),
        accessible_sources_count=accessible_count,
        cached_sources_count=0,  # Not using cache in this test
        suggestions_for_failed_sources=suggestions
    )
    
    # Format and display result
    formatted_result = VhalSourceValidator.format_enhanced_summary(enhanced_result)
    print(formatted_result)
    
    print("\n" + "=" * 80)
    print("✅ Enhanced Summary Test Complete!")
    print(f"   - Confidence Score: {confidence_score:.1f}%")
    print(f"   - Accessible Sources: {accessible_count}/{len(test_sources)}")
    print(f"   - Failed Sources: {len(failed_validations)}")
    print(f"   - Alternative Suggestions: {len(suggestions)}")

def test_source_validation_only():
    """Test just the source validation functionality."""
    print("\n🔗 Testing Source Validation Only\n")
    
    # Test a mix of valid and invalid URLs
    test_urls = [
        "https://source.android.com/docs/automotive/vhal",
        "https://httpbin.org/status/200",  # Should work
        "https://httpbin.org/status/404",  # Should fail with 404
        "https://nonexistent-domain-12345.com",  # Should fail with DNS error
    ]
    
    print("URLs to validate:")
    for url in test_urls:
        print(f"  - {url}")
    
    print("\nValidating sources...")
    
    start_time = time.time()
    validations = VhalSourceValidator.validate_sources_parallel(test_urls)
    end_time = time.time()
    
    print(f"\nValidation completed in {end_time - start_time:.2f} seconds")
    print("\nResults:")
    
    for validation in validations:
        status = "✅ PASS" if validation.is_accessible else "❌ FAIL"
        print(f"\n{status} {validation.url}")
        print(f"    Status Code: {validation.status_code or 'N/A'}")
        print(f"    Response Time: {validation.response_time_ms:.1f}ms" if validation.response_time_ms else "    Response Time: N/A")
        if validation.error_message:
            print(f"    Error: {validation.error_message}")
        if validation.last_modified:
            print(f"    Last Modified: {validation.last_modified}")

if __name__ == "__main__":
    print("🚀 vHAL MCP Enhanced Source Validation Test\n")
    
    # Test source validation functionality
    test_source_validation_only()
    
    # Test the complete enhanced summary
    test_enhanced_summary()
    
    print("\n🎉 All tests completed!")
    print("\nThis demonstrates how the enhanced tool provides:")
    print("  ✅ Source URL validation and accessibility checking")
    print("  ✅ Confidence scoring based on source reliability")  
    print("  ✅ Clear transparency about data sources")
    print("  ✅ Alternative suggestions for failed sources")
    print("  ✅ Performance metrics and response times")
    print("  ✅ Professional formatting for end users")
