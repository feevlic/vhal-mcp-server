#!/usr/bin/env python3
import unittest
from src.vhal_mcp_server.server import summarize_vhal, lookup_android_source_code, discover_related_properties, analyze_vhal_implementation


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

    def test_discover_seat_memory_properties(self):
        """Test discovery of SEAT_MEMORY related properties."""
        result = discover_related_properties("SEAT_MEMORY")

        self.assertIsInstance(result, str)
        self.assertIn("SEAT_MEMORY", result)
        self.assertIn("Implementation Order", result)
        self.assertIn("SEAT_MEMORY_SELECT", result)
        self.assertIn("SEAT_MEMORY_SET", result)

    def test_discover_hvac_basic_properties(self):
        """Test discovery of HVAC_BASIC related properties."""
        result = discover_related_properties("HVAC_BASIC")

        self.assertIsInstance(result, str)
        self.assertIn("HVAC", result)
        self.assertIn("HVAC_POWER_ON", result)
        self.assertIn("HVAC_TEMPERATURE_SET", result)

    def test_discover_specific_property_relationships(self):
        """Test discovery using a specific property name."""
        result = discover_related_properties("SEAT_FORE_AFT_POS")

        self.assertIsInstance(result, str)
        self.assertIn("SEAT", result)
        self.assertIn("Related Properties", result)

    def test_discover_unknown_property(self):
        """Test discovery with an unknown property."""
        result = discover_related_properties("UNKNOWN_PROPERTY")

        self.assertIsInstance(result, str)
        self.assertIn("not found in known ecosystems", result)


def run_basic_tests():
    """Run basic functionality tests."""
    print("Running vHAL MCP Server tests...\n")

    try:
        print("1. Testing vHAL summarization...")
        question = "How do seat properties work in vHAL?"
        result = summarize_vhal(question)
        print(f"   ✓ Summarization successful ({len(result)} characters)")

        print("2. Testing SEAT property lookup...")
        result = lookup_android_source_code("SEAT")
        print(f"   ✓ SEAT lookup successful ({len(result)} characters)")

        print("3. Testing HVAC property lookup...")
        result = lookup_android_source_code("HVAC")
        print(f"   ✓ HVAC lookup successful ({len(result)} characters)")

        print("4. Testing property relationship discovery...")
        result = discover_related_properties("SEAT_MEMORY")
        print(f"   ✓ Property discovery successful ({len(result)} characters)")

        print("5. Testing HVAC ecosystem discovery...")
        result = discover_related_properties("HVAC_BASIC")
        print(
            f"   ✓ HVAC ecosystem discovery successful ({
                len(result)} characters)")

        print("6. Testing vHAL implementation analysis...")
        result = analyze_vhal_implementation("HVAC_STEERING_WHEEL_HEAT")
        print(
            f"   ✓ Implementation analysis successful ({
                len(result)} characters)")

        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        return True

    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


if __name__ == "__main__":
    run_basic_tests()
