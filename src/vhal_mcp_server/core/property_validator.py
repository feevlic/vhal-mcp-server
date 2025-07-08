"""Property validation tool for checking Android vHAL properties and generating VENDOR_ properties.

This module provides functionality to validate whether a requested property already exists
in the latest Android release and either suggests using the existing property or generates
a new VENDOR_ property following Android best practices.
"""

import re
import requests
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from ..models import VhalProperty, VhalCategory
from .database import VhalPropertyDatabase
from .analyzers import AndroidSourceCodeAnalyzer
from ..generators.code_generator import VhalCodeGenerator


@dataclass
class PropertyValidationResult:
    """Result of property validation check."""
    property_name: str
    property_description: str
    exists_in_android: bool
    existing_property: Optional[VhalProperty] = None
    android_version: str = "android16"
    recommendation: str = ""
    generated_vendor_property: Optional[Dict] = None
    similar_properties: List[VhalProperty] = None
    confidence_score: float = 0.0


class VhalPropertyValidator:
    """Validator for checking Android vHAL properties and generating VENDOR_ properties."""
    
    LATEST_ANDROID_VERSION = "android16"
    
    # Common property patterns that suggest existing functionality
    COMMON_PATTERNS = {
        "temperature": ["HVAC_TEMPERATURE_SET", "HVAC_TEMPERATURE_CURRENT"],
        "fan": ["HVAC_FAN_SPEED", "HVAC_FAN_DIRECTION"],
        "seat": ["SEAT_MEMORY_SELECT", "SEAT_FORE_AFT_POS", "SEAT_HEIGHT_POS"],
        "heat": ["HVAC_STEERING_WHEEL_HEAT", "HVAC_SIDE_MIRROR_HEAT", "HVAC_SEAT_TEMPERATURE"],
        "light": ["CABIN_LIGHTS_STATE", "HEADLIGHTS", "CABIN_LIGHTS_SWITCH"],
        "power": ["HVAC_POWER_ON", "ENGINE_ON", "IGNITION_STATE"],
        "door": ["DOOR_LOCK", "DOOR_POS", "DOOR_MOVE"],
        "window": ["WINDOW_POS", "WINDOW_MOVE", "WINDOW_LOCK"],
        "climate": ["HVAC_AC_ON", "HVAC_DEFROSTER", "HVAC_AUTO_ON"],
        "memory": ["SEAT_MEMORY_SELECT", "SEAT_MEMORY_SET"],
        "position": ["SEAT_FORE_AFT_POS", "SEAT_HEIGHT_POS", "SEAT_TILT_POS"],
        "mirror": ["MIRROR_Z_POS", "MIRROR_Y_POS", "MIRROR_Z_MOVE"],
        "audio": ["AUDIO_VOLUME", "AUDIO_FOCUS", "AUDIO_ROUTING_POLICY"],
        "navigation": ["CURRENT_GEAR", "GEAR_SELECTION", "PARKING_BRAKE_ON"]
    }
    
    # Extended property database for Android 16
    ANDROID_16_PROPERTIES = {
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
            "HVAC_SEAT_VENTILATION": "0x0A14",
            "HVAC_ELECTRIC_DEFROSTER_ON": "0x0A15",
            "HVAC_TEMPERATURE_VALUE_SUGGESTION": "0x0A16",
            "HVAC_CABIN_TEMPERATURE": "0x0A17",
            "HVAC_OUTSIDE_TEMPERATURE": "0x0A18",
            "HVAC_SEAT_TEMPERATURE_DESIRED": "0x0A19",
            "HVAC_SEAT_VENTILATION_DESIRED": "0x0A1A"
        },
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
            "SEAT_HEADREST_FORE_AFT_MOVE": "0x0B70",
            "SEAT_FOOTWELL_LIGHTS_STATE": "0x0B71",
            "SEAT_FOOTWELL_LIGHTS_SWITCH": "0x0B72",
            "SEAT_EASY_ACCESS_ENABLED": "0x0B73",
            "SEAT_AIRBAG_ENABLED": "0x0B74",
            "SEAT_CUSHION_SIDE_SUPPORT_POS": "0x0B75",
            "SEAT_CUSHION_SIDE_SUPPORT_MOVE": "0x0B76",
            "SEAT_LUMBAR_VERTICAL_POS": "0x0B77",
            "SEAT_LUMBAR_VERTICAL_MOVE": "0x0B78",
            "SEAT_WALK_IN_POS": "0x0B79",
            "SEAT_OCCUPANCY": "0x0B7A"
        },
        VhalCategory.LIGHTS: {
            "HEADLIGHTS": "0x0C01",
            "HEADLIGHTS_SWITCH": "0x0C02",
            "HIGH_BEAM_LIGHTS_STATE": "0x0C03",
            "HIGH_BEAM_LIGHTS_SWITCH": "0x0C04",
            "TURN_SIGNAL_STATE": "0x0C05",
            "HAZARD_LIGHTS_STATE": "0x0C06",
            "HAZARD_LIGHTS_SWITCH": "0x0C07",
            "CABIN_LIGHTS_STATE": "0x0C08",
            "CABIN_LIGHTS_SWITCH": "0x0C09",
            "READING_LIGHTS_STATE": "0x0C0A",
            "READING_LIGHTS_SWITCH": "0x0C0B",
            "FOG_LIGHTS_STATE": "0x0C0C",
            "FOG_LIGHTS_SWITCH": "0x0C0D",
            "DAYTIME_RUNNING_LIGHTS_STATE": "0x0C0E",
            "AUTOMATIC_LIGHT_SENSOR": "0x0C0F",
            "LIGHT_SWITCH_AUTO": "0x0C10",
            "LIGHT_STATE": "0x0C11",
            "LIGHT_SWITCH": "0x0C12",
            "PARKING_LIGHTS_STATE": "0x0C13",
            "PARKING_LIGHTS_SWITCH": "0x0C14",
            "TRAILER_LIGHTS_STATE": "0x0C15",
            "TRAILER_LIGHTS_SWITCH": "0x0C16",
            "AMBIENT_LIGHTS_STATE": "0x0C17",
            "AMBIENT_LIGHTS_SWITCH": "0x0C18"
        },
        VhalCategory.POWER: {
            "IGNITION_STATE": "0x0D01",
            "ENGINE_ON": "0x0D02",
            "BATTERY_LEVEL": "0x0D03",
            "FUEL_LEVEL": "0x0D04",
            "FUEL_DOOR_OPEN": "0x0D05",
            "EV_BATTERY_LEVEL": "0x0D06",
            "EV_CHARGE_PORT_OPEN": "0x0D07",
            "EV_CHARGE_PORT_CONNECTED": "0x0D08",
            "EV_BATTERY_INSTANTANEOUS_CHARGE_RATE": "0x0D09",
            "RANGE_REMAINING": "0x0D0A",
            "TIRE_PRESSURE": "0x0D0B",
            "CRITICALLY_LOW_TIRE_PRESSURE": "0x0D0C",
            "ENGINE_COOLANT_TEMP": "0x0D0D",
            "ENGINE_OIL_LEVEL": "0x0D0E",
            "ENGINE_OIL_TEMP": "0x0D0F",
            "ENGINE_RPM": "0x0D10",
            "WHEEL_TICK": "0x0D11",
            "FUEL_CONSUMPTION_UNITS_DISTANCE_OVER_VOLUME": "0x0D12",
            "VEHICLE_SPEED_DISPLAY_UNITS": "0x0D13",
            "POWER_POLICY_REQ": "0x0D14",
            "POWER_POLICY_GROUP_REQ": "0x0D15"
        },
        VhalCategory.BODY: {
            "DOOR_POS": "0x0E01",
            "DOOR_MOVE": "0x0E02",
            "DOOR_LOCK": "0x0E03",
            "DOOR_CHILD_LOCK_ENABLED": "0x0E04",
            "MIRROR_Z_POS": "0x0E05",
            "MIRROR_Z_MOVE": "0x0E06",
            "MIRROR_Y_POS": "0x0E07",
            "MIRROR_Y_MOVE": "0x0E08",
            "MIRROR_LOCK_ENABLED": "0x0E09",
            "MIRROR_FOLD": "0x0E0A",
            "WINDOW_POS": "0x0E0B",
            "WINDOW_MOVE": "0x0E0C",
            "WINDOW_LOCK": "0x0E0D",
            "VEHICLE_MAP_SERVICE": "0x0E0E",
            "LOCATION_CHARACTERIZATION": "0x0E0F",
            "ULTRASONICS_SENSOR_POSITION": "0x0E10",
            "ULTRASONICS_SENSOR_ORIENTATION": "0x0E11",
            "ULTRASONICS_SENSOR_FIELD_OF_VIEW": "0x0E12",
            "ULTRASONICS_SENSOR_DETECTION_RANGE": "0x0E13",
            "ULTRASONICS_SENSOR_SUPPORTED_RANGES": "0x0E14",
            "GENERAL_SAFETY_REGULATION_COMPLIANCE_REQUIREMENT": "0x0E15",
            "ELECTRONIC_TOLL_COLLECTION_CARD_TYPE": "0x0E16",
            "ELECTRONIC_TOLL_COLLECTION_CARD_STATUS": "0x0E17",
            "FRONT_FOG_LIGHTS_STATE": "0x0E18",
            "FRONT_FOG_LIGHTS_SWITCH": "0x0E19",
            "REAR_FOG_LIGHTS_STATE": "0x0E1A",
            "REAR_FOG_LIGHTS_SWITCH": "0x0E1B",
            "EV_CHARGE_CURRENT_DRAW_LIMIT": "0x0E1C",
            "EV_CHARGE_PERCENT_LIMIT": "0x0E1D",
            "EV_CHARGE_STATE": "0x0E1E",
            "EV_CHARGE_SWITCH": "0x0E1F",
            "TRAILER_PRESENT": "0x0E20"
        }
    }
    
    @classmethod
    def validate_property_request(
        cls,
        property_name: str,
        property_description: str,
        property_type: str = "INT32",
        group: str = "VENDOR",
        access: str = "READ_WRITE",
        change_mode: str = "ON_CHANGE",
        units: str = None,
        min_value: float = None,
        max_value: float = None,
        areas: List[str] = None,
        enum_values: Dict[str, int] = None,
        dependencies: List[str] = None,
        sample_rate_hz: float = None,
        android_version: str = None
    ) -> PropertyValidationResult:
        """Validate if a property request should use existing Android property or create VENDOR_ property.
        
        Args:
            property_name: Requested property name
            property_description: Description of what the property does
            property_type: Data type (default: INT32)
            group: Property group (default: VENDOR)
            access: Access mode (default: READ_WRITE)
            change_mode: Change mode (default: ON_CHANGE)
            units: Optional units
            min_value: Optional minimum value
            max_value: Optional maximum value
            areas: Optional list of vehicle areas
            enum_values: Optional enum values
            dependencies: Optional dependencies
            sample_rate_hz: Optional sample rate
            android_version: Android version to check (default: android16)
            
        Returns:
            PropertyValidationResult with recommendation
        """
        
        if android_version is None:
            android_version = cls.LATEST_ANDROID_VERSION
            
        # Clean up property name
        clean_property_name = property_name.upper().strip()
        
        # Check if exact property exists
        existing_property = cls._check_exact_property_exists(clean_property_name, android_version)
        
        if existing_property:
            return PropertyValidationResult(
                property_name=clean_property_name,
                property_description=property_description,
                exists_in_android=True,
                existing_property=existing_property,
                android_version=android_version,
                recommendation=cls._generate_existing_property_recommendation(existing_property),
                confidence_score=1.0
            )
        
        # Check for similar properties
        similar_properties, confidence = cls._find_similar_properties(clean_property_name, property_description)
        
        if similar_properties and confidence > 0.7:
            return PropertyValidationResult(
                property_name=clean_property_name,
                property_description=property_description,
                exists_in_android=True,
                existing_property=similar_properties[0],
                android_version=android_version,
                recommendation=cls._generate_similar_property_recommendation(similar_properties[0], clean_property_name),
                similar_properties=similar_properties,
                confidence_score=confidence
            )
        
        # Generate VENDOR_ property
        vendor_property_name = f"VENDOR_{clean_property_name}"
        vendor_property_id = cls._generate_vendor_property_id(vendor_property_name)
        
        # Generate the vendor property implementation
        try:
            vendor_implementation = VhalCodeGenerator.generate_vhal_implementation(
                name=vendor_property_name,
                property_id=vendor_property_id,
                property_type=property_type,
                group="VENDOR",
                access=access,
                change_mode=change_mode,
                description=f"Vendor-specific property: {property_description}",
                units=units,
                min_value=min_value,
                max_value=max_value,
                areas=areas,
                enum_values=enum_values,
                dependencies=dependencies,
                sample_rate_hz=sample_rate_hz
            )
            
            vendor_property_data = {
                "name": vendor_property_name,
                "property_id": vendor_property_id,
                "property_type": property_type,
                "group": "VENDOR",
                "access": access,
                "change_mode": change_mode,
                "description": f"Vendor-specific property: {property_description}",
                "implementation": vendor_implementation
            }
            
        except Exception as e:
            vendor_property_data = {
                "name": vendor_property_name,
                "property_id": vendor_property_id,
                "error": f"Failed to generate implementation: {str(e)}"
            }
        
        return PropertyValidationResult(
            property_name=clean_property_name,
            property_description=property_description,
            exists_in_android=False,
            android_version=android_version,
            recommendation=cls._generate_vendor_property_recommendation(vendor_property_name, property_description),
            generated_vendor_property=vendor_property_data,
            similar_properties=similar_properties,
            confidence_score=0.0
        )
    
    @classmethod
    def _check_exact_property_exists(cls, property_name: str, android_version: str) -> Optional[VhalProperty]:
        """Check if exact property exists in Android release."""
        
        # Check in Android 16 extended database
        for category, properties in cls.ANDROID_16_PROPERTIES.items():
            if property_name in properties:
                return VhalProperty(property_name, properties[property_name], category)
        
        # Check in current database
        for category, properties in VhalPropertyDatabase.PROPERTIES.items():
            if property_name in properties:
                return VhalProperty(property_name, properties[property_name], category)
        
        return None
    
    @classmethod
    def _find_similar_properties(cls, property_name: str, description: str) -> tuple[List[VhalProperty], float]:
        """Find similar properties based on name and description."""
        similar_properties = []
        max_confidence = 0.0
        
        # Extract keywords from property name and description
        name_keywords = set(re.findall(r'\w+', property_name.lower()))
        desc_keywords = set(re.findall(r'\w+', description.lower()))
        all_keywords = name_keywords.union(desc_keywords)
        
        # Check against pattern matching
        for keyword in all_keywords:
            if keyword in cls.COMMON_PATTERNS:
                for pattern_property in cls.COMMON_PATTERNS[keyword]:
                    existing_prop = cls._check_exact_property_exists(pattern_property, cls.LATEST_ANDROID_VERSION)
                    if existing_prop:
                        similar_properties.append(existing_prop)
                        confidence = cls._calculate_similarity_confidence(property_name, pattern_property, description)
                        max_confidence = max(max_confidence, confidence)
        
        # Search in all properties for partial matches
        all_properties = []
        for category, properties in cls.ANDROID_16_PROPERTIES.items():
            for name, prop_id in properties.items():
                all_properties.append(VhalProperty(name, prop_id, category))
        
        for prop in all_properties:
            prop_keywords = set(re.findall(r'\w+', prop.name.lower()))
            intersection = name_keywords.intersection(prop_keywords)
            if intersection:
                confidence = len(intersection) / len(name_keywords.union(prop_keywords))
                if confidence > 0.3:  # Minimum threshold
                    similar_properties.append(prop)
                    max_confidence = max(max_confidence, confidence)
        
        # Remove duplicates and sort by relevance
        unique_properties = []
        seen_names = set()
        for prop in similar_properties:
            if prop.name not in seen_names:
                unique_properties.append(prop)
                seen_names.add(prop.name)
        
        return unique_properties[:5], max_confidence  # Return top 5 most similar
    
    @classmethod
    def _calculate_similarity_confidence(cls, requested_name: str, existing_name: str, description: str) -> float:
        """Calculate confidence score for similarity between properties."""
        req_words = set(re.findall(r'\w+', requested_name.lower()))
        exist_words = set(re.findall(r'\w+', existing_name.lower()))
        desc_words = set(re.findall(r'\w+', description.lower()))
        
        # Name similarity (60% weight)
        name_intersection = req_words.intersection(exist_words)
        name_similarity = len(name_intersection) / len(req_words.union(exist_words)) if req_words.union(exist_words) else 0
        
        # Description relevance (40% weight)
        desc_intersection = desc_words.intersection(exist_words)
        desc_relevance = len(desc_intersection) / len(desc_words) if desc_words else 0
        
        return (name_similarity * 0.6) + (desc_relevance * 0.4)
    
    @classmethod
    def _generate_vendor_property_id(cls, property_name: str) -> str:
        """Generate unique property ID for vendor property."""
        # Generate hash-based ID in vendor range (0x70000000 - 0x7FFFFFFF)
        import hashlib
        hash_obj = hashlib.md5(property_name.encode())
        hash_hex = hash_obj.hexdigest()[:6]
        vendor_id = 0x70000000 + int(hash_hex, 16) % 0x0FFFFFFF
        return f"0x{vendor_id:08X}"
    
    @classmethod
    def _generate_existing_property_recommendation(cls, existing_property: VhalProperty) -> str:
        """Generate recommendation for using existing property."""
        return f"""✅ **RECOMMENDATION: Use Existing Android Property**

**Property Found:** `{existing_property.name}`
**Property ID:** `{existing_property.id}`
**Category:** `{existing_property.category.value}`

**Why use this property:**
- This property already exists in Android {cls.LATEST_ANDROID_VERSION}
- Following Android best practices: reuse existing properties when available
- Ensures compatibility with Android Automotive OS
- Reduces implementation complexity and maintenance overhead

**Next Steps:**
1. Review the property documentation and implementation
2. Use `analyze_vhal_implementation('{existing_property.name}')` to see how it's implemented
3. Integrate this property into your HAL implementation
4. Test with Android Automotive OS

**Implementation Notes:**
- No need to create custom VENDOR_ property
- Follow existing property patterns and configurations
- Ensure proper area mapping and access control"""
    
    @classmethod
    def _generate_similar_property_recommendation(cls, similar_property: VhalProperty, requested_name: str) -> str:
        """Generate recommendation for using similar property."""
        return f"""⚠️ **RECOMMENDATION: Consider Using Similar Android Property**

**Similar Property Found:** `{similar_property.name}`
**Property ID:** `{similar_property.id}`
**Category:** `{similar_property.category.value}`

**Why consider this property:**
- Very similar to your requested property: `{requested_name}`
- Already exists in Android {cls.LATEST_ANDROID_VERSION}
- May fulfill your requirements with minor adjustments
- Follows Android best practices

**Decision Required:**
Please evaluate if `{similar_property.name}` meets your requirements:

1. **If YES** → Use the existing property (recommended)
   - Use `analyze_vhal_implementation('{similar_property.name}')` to see implementation
   - Integrate into your HAL following Android patterns

2. **If NO** → Create VENDOR_ property
   - Proceed with generating a custom VENDOR_ property
   - Document why the existing property doesn't meet your needs

**Next Steps:**
1. Review property documentation: `analyze_vhal_implementation('{similar_property.name}')`
2. Compare with your specific requirements
3. Make implementation decision based on compatibility"""
    
    @classmethod
    def _generate_vendor_property_recommendation(cls, vendor_property_name: str, description: str) -> str:
        """Generate recommendation for creating vendor property."""
        return f"""🔧 **RECOMMENDATION: Create VENDOR_ Property**

**Generated Property:** `{vendor_property_name}`
**Property ID:** Auto-generated in vendor range

**Why create a VENDOR_ property:**
- No equivalent property exists in Android {cls.LATEST_ANDROID_VERSION}
- Custom functionality requires vendor-specific implementation
- Follows Android best practices for OEM extensions

**Vendor Property Benefits:**
- Unique to your implementation
- Won't conflict with future Android updates
- Maintains separation between AOSP and vendor code
- Allows custom behavior and configuration

**Implementation Guidelines:**
1. **Naming:** Always prefix with `VENDOR_` (already applied)
2. **Property ID:** Use vendor-specific range (0x70000000-0x7FFFFFFF)
3. **Documentation:** Document purpose, usage, and any dependencies
4. **Testing:** Implement comprehensive tests for vendor properties
5. **Compatibility:** Ensure graceful handling on different Android versions

**Next Steps:**
1. Review the generated implementation code below
2. Customize as needed for your specific requirements
3. Integrate into your HAL implementation
4. Test thoroughly with your vehicle platform
5. Document for future maintenance

**Note:** This is a custom vendor property and will not be available in AOSP builds."""

    @classmethod
    def format_validation_result(cls, result: PropertyValidationResult) -> str:
        """Format validation result for display."""
        output_parts = [
            f"# vHAL Property Validation Result\n",
            "=" * 80,
            f"\n**Requested Property:** `{result.property_name}`",
            f"**Description:** {result.property_description}",
            f"**Android Version:** {result.android_version}",
            f"\n## Analysis Result\n",
            result.recommendation
        ]
        
        if result.exists_in_android and result.existing_property:
            output_parts.extend([
                "\n## Existing Property Details\n",
                f"**Property Name:** `{result.existing_property.name}`",
                f"**Property ID:** `{result.existing_property.id}`",
                f"**Category:** `{result.existing_property.category.value}`",
                f"\n**Usage Examples:**",
                f"```cpp",
                f"// Get property value",
                f"VehiclePropValue propValue;",
                f"propValue.prop = {result.existing_property.id};  // {result.existing_property.name}",
                f"propValue.areaId = 0;  // Global or specific area",
                f"// Use vHAL interface to get/set value",
                f"```",
                f"\n**Next Steps:**",
                f"1. Use `analyze_vhal_implementation('{result.existing_property.name}')` for detailed analysis",
                f"2. Use `discover_related_properties('{result.existing_property.name}')` for related properties",
                f"3. Integration guidance: `generate_vhal_implementation_code(...)` if needed"
            ])
        
        if result.similar_properties:
            output_parts.append("\n## Similar Properties Found\n")
            for i, prop in enumerate(result.similar_properties, 1):
                output_parts.extend([
                    f"### {i}. {prop.name}",
                    f"**Property ID:** `{prop.id}`",
                    f"**Category:** `{prop.category.value}`",
                    f"**Analysis:** Use `analyze_vhal_implementation('{prop.name}')` for details\n"
                ])
        
        if result.generated_vendor_property:
            vendor_data = result.generated_vendor_property
            output_parts.extend([
                "\n## Generated VENDOR_ Property\n",
                f"**Property Name:** `{vendor_data['name']}`",
                f"**Property ID:** `{vendor_data['property_id']}`",
                f"**Property Type:** `{vendor_data.get('property_type', 'N/A')}`",
                f"**Group:** `{vendor_data.get('group', 'VENDOR')}`",
                f"**Access:** `{vendor_data.get('access', 'N/A')}`",
                f"**Change Mode:** `{vendor_data.get('change_mode', 'N/A')}`",
                f"**Description:** {vendor_data.get('description', 'N/A')}"
            ])
            
            if 'error' in vendor_data:
                output_parts.append(f"\n**Error:** {vendor_data['error']}")
            elif 'implementation' in vendor_data:
                output_parts.extend([
                    "\n## Complete Implementation\n",
                    "The complete VHAL implementation has been generated. ",
                    "Use `generate_vhal_implementation_code()` with the above parameters ",
                    "to get the full implementation code."
                ])
        
        output_parts.extend([
            "\n## Best Practices\n",
            "- **Always check existing properties first** before creating vendor properties",
            "- **Use VENDOR_ prefix** for all custom properties",
            "- **Document thoroughly** for future maintenance",
            "- **Test comprehensively** with your vehicle platform",
            "- **Follow Android patterns** for consistency",
            "\n## Additional Resources\n",
            "- [Android vHAL Documentation](https://source.android.com/docs/automotive/vhal)",
            "- [vHAL Property Guidelines](https://source.android.com/docs/automotive/vhal/properties)",
            "- Use other MCP tools: `summarize_vhal()`, `lookup_android_source_code()`, `discover_related_properties()`"
        ])
        
        return "\n".join(output_parts)

