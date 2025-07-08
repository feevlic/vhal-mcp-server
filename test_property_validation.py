#!/usr/bin/env python3
"""Test script for the new vHAL property validation tool."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from vhal_mcp_server.core.property_validator import VhalPropertyValidator

def test_existing_property():
    """Test validation of existing property."""
    print("=== Testing Existing Property ===")
    result = VhalPropertyValidator.validate_property_request(
        property_name="HVAC_FAN_SPEED",
        property_description="Control fan speed for HVAC system"
    )
    print(VhalPropertyValidator.format_validation_result(result))
    print("\n")

def test_similar_property():
    """Test validation of similar property."""
    print("=== Testing Similar Property ===")
    result = VhalPropertyValidator.validate_property_request(
        property_name="HVAC_COOLING_SPEED",
        property_description="Control cooling fan speed"
    )
    print(VhalPropertyValidator.format_validation_result(result))
    print("\n")

def test_new_vendor_property():
    """Test creation of new vendor property."""
    print("=== Testing New Vendor Property ===")
    result = VhalPropertyValidator.validate_property_request(
        property_name="SEAT_MASSAGE_INTENSITY",
        property_description="Control seat massage intensity level",
        property_type="INT32",
        min_value=0,
        max_value=10,
        areas=["SEAT_ROW_1_LEFT", "SEAT_ROW_1_RIGHT"],
        enum_values={"OFF": 0, "LOW": 1, "MEDIUM": 5, "HIGH": 10}
    )
    print(VhalPropertyValidator.format_validation_result(result))
    print("\n")

def test_climate_property():
    """Test climate-related property."""
    print("=== Testing Climate Property ===")
    result = VhalPropertyValidator.validate_property_request(
        property_name="CLIMATE_IONIZER_STATE",
        property_description="Control air ionizer state in climate system",
        property_type="BOOLEAN",
        group="HVAC",
        access="READ_WRITE",
        change_mode="ON_CHANGE"
    )
    print(VhalPropertyValidator.format_validation_result(result))
    print("\n")

if __name__ == "__main__":
    print("Testing vHAL Property Validation Tool")
    print("=" * 60)
    
    test_existing_property()
    test_similar_property()
    test_new_vendor_property()
    test_climate_property()
    
    print("Testing completed!")
