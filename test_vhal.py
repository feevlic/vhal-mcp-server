#!/usr/bin/env python3
"""Test suite for vHAL MCP Server."""

import unittest
from server import summarize_vhal, lookup_android_source_code


class TestVhalMcpServer(unittest.TestCase):
    """Test cases for vHAL MCP server functionality."""
    
    def test_vhal_summarization(self):
        """Test the vHAL summarization functionality."""
        question = "What are vHAL properties and how do they work?"
        
        result = summarize_vhal(question)
        
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        self.assertIn("vHAL", result)
    
    def test_seat_property_lookup(self):
        """Test lookup of SEAT properties."""
        result = lookup_android_source_code("SEAT")
        
        self.assertIsInstance(result, str)
        self.assertIn("SEAT", result)
        self.assertIn("0x0B", result)  # SEAT property IDs start with 0x0B
    
    def test_hvac_property_lookup(self):
        """Test lookup of HVAC properties."""
        result = lookup_android_source_code("HVAC")
        
        self.assertIsInstance(result, str)
        self.assertIn("HVAC", result)
        self.assertIn("0x0A", result)  # HVAC property IDs start with 0x0A
    
    def test_invalid_keyword_lookup(self):
        """Test lookup with an invalid keyword."""
        result = lookup_android_source_code("NONEXISTENT_PROPERTY")
        
        self.assertIsInstance(result, str)
        self.assertIn("Source Code Locations", result)


def run_basic_tests():
    """Run basic functionality tests."""
    print("Running vHAL MCP Server tests...\n")
    
    try:
        # Test summarization
        print("1. Testing vHAL summarization...")
        question = "How do seat properties work in vHAL?"
        result = summarize_vhal(question)
        print(f"   ✓ Summarization successful ({len(result)} characters)")
        
        # Test SEAT lookup
        print("2. Testing SEAT property lookup...")
        result = lookup_android_source_code("SEAT")
        print(f"   ✓ SEAT lookup successful ({len(result)} characters)")
        
        # Test HVAC lookup
        print("3. Testing HVAC property lookup...")
        result = lookup_android_source_code("HVAC")
        print(f"   ✓ HVAC lookup successful ({len(result)} characters)")
        
        print("\n" + "="*60)
        print("All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


if __name__ == "__main__":
    run_basic_tests()
