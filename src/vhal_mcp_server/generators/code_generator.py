import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime


class VhalPropertyType(Enum):
    """VHAL property data types"""
    BOOLEAN = "BOOLEAN"
    INT32 = "INT32"
    INT64 = "INT64"
    FLOAT = "FLOAT"
    STRING = "STRING"
    BYTES = "BYTES"
    INT32_VEC = "INT32_VEC"
    FLOAT_VEC = "FLOAT_VEC"
    STRING_VEC = "STRING_VEC"
    BYTES_VEC = "BYTES_VEC"
    MIXED = "MIXED"


class VhalPropertyGroup(Enum):
    """VHAL property groups/categories"""
    BODY = "BODY"
    CABIN = "CABIN"
    CLIMATE = "CLIMATE"
    DISPLAY = "DISPLAY"
    ENGINE = "ENGINE"
    HVAC = "HVAC"
    INFO = "INFO"
    INSTRUMENT_CLUSTER = "INSTRUMENT_CLUSTER"
    LIGHTS = "LIGHTS"
    MIRROR = "MIRROR"
    POWER = "POWER"
    SEAT = "SEAT"
    VEHICLE_MAP_SERVICE = "VEHICLE_MAP_SERVICE"
    WINDOW = "WINDOW"
    VENDOR = "VENDOR"


class VhalChangeMode(Enum):
    """VHAL property change modes"""
    STATIC = "STATIC"
    ON_CHANGE = "ON_CHANGE"
    CONTINUOUS = "CONTINUOUS"


class VhalAccess(Enum):
    """VHAL property access modes"""
    READ = "READ"
    WRITE = "WRITE"
    READ_WRITE = "READ_WRITE"


@dataclass
class VhalPropertyConfig:
    """Configuration for a VHAL property"""
    name: str
    id: str  
    type: str
    group: str
    access: str
    change_mode: str
    description: str
    units: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    areas: Optional[List[str]] = None
    enum_values: Optional[Dict[str, int]] = None
    dependencies: Optional[List[str]] = None
    sample_rate_hz: Optional[float] = None


@dataclass
class GeneratedFile:
    """Represents a generated file"""
    path: str
    content: str
    description: str


@dataclass
class GenerationResult:
    """Result of code generation"""
    property_name: str
    property_id: str
    files: List[GeneratedFile]
    summary: str
    implementation_guide: str


class VhalCodeGenerator:
    """Generates VHAL implementation code for AAOS"""
    
    @staticmethod
    def generate_vhal_implementation(
        name: str,
        property_id: str,
        property_type: str,
        group: str,
        access: str,
        change_mode: str,
        description: str,
        units: Optional[str] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        areas: Optional[List[str]] = None,
        enum_values: Optional[Dict[str, int]] = None,
        dependencies: Optional[List[str]] = None,
        sample_rate_hz: Optional[float] = None
    ) -> GenerationResult:
        """Generate complete VHAL implementation"""
        
        if isinstance(property_id, str):
            if property_id.startswith('0x'):
                prop_id_int = int(property_id, 16)
            else:
                prop_id_int = int(property_id)
        else:
            prop_id_int = property_id
        
        config = VhalPropertyConfig(
            name=name,
            id=property_id,
            type=property_type,
            group=group,
            access=access,
            change_mode=change_mode,
            description=description,
            units=units,
            min_value=min_value,
            max_value=max_value,
            areas=areas or [],
            enum_values=enum_values or {},
            dependencies=dependencies or [],
            sample_rate_hz=sample_rate_hz
        )
        
        files = VhalCodeGenerator._generate_all_files(config)
        
        summary = VhalCodeGenerator._generate_summary(config, len(files))
        guide = VhalCodeGenerator._generate_implementation_guide(config)
        
        return GenerationResult(
            property_name=name,
            property_id=property_id,
            files=files,
            summary=summary,
            implementation_guide=guide
        )
    
    @staticmethod
    def _generate_all_files(config: VhalPropertyConfig) -> List[GeneratedFile]:
        """Generate all necessary files for the VHAL property"""
        files = []
        
        files.append(GeneratedFile(
            path="hardware/interfaces/automotive/vehicle/2.0/types.hal",
            content=VhalCodeGenerator._generate_types_hal(config),
            description="HAL property definition and enum values"
        ))
        
        files.append(GeneratedFile(
            path="hardware/interfaces/automotive/vehicle/2.0/default/impl/vhal_v2_0/DefaultConfig.h",
            content=VhalCodeGenerator._generate_default_config_h(config),
            description="Property configuration and constraints"
        ))
        
        files.append(GeneratedFile(
            path="hardware/interfaces/automotive/vehicle/2.0/default/impl/vhal_v2_0/EmulatedVehicleHal.cpp",
            content=VhalCodeGenerator._generate_emulated_hal_cpp(config),
            description="HAL implementation logic"
        ))
        
        files.append(GeneratedFile(
            path="hardware/interfaces/automotive/vehicle/aidl/android/hardware/automotive/vehicle/VehicleProperty.aidl",
            content=VhalCodeGenerator._generate_aidl_property(config),
            description="AIDL interface definition"
        ))
        
        files.append(GeneratedFile(
            path="packages/services/Car/car-lib/src/android/car/VehiclePropertyIds.java",
            content=VhalCodeGenerator._generate_java_constants(config),
            description="Java property constants"
        ))
        
        files.append(GeneratedFile(
            path="packages/services/Car/car-lib/src/android/car/hardware/property/CarPropertyManager.java",
            content=VhalCodeGenerator._generate_car_property_manager(config),
            description="CarPropertyManager API methods"
        ))
        
        files.append(GeneratedFile(
            path="hardware/interfaces/automotive/vehicle/2.0/default/tests/VehicleHalTest.cpp",
            content=VhalCodeGenerator._generate_hal_test(config),
            description="C++ unit tests"
        ))
        
        files.append(GeneratedFile(
            path="packages/services/Car/tests/carservice_test/src/com/android/car/VehiclePropertyTest.java",
            content=VhalCodeGenerator._generate_java_test(config),
            description="Java integration tests"
        ))
        
        files.append(GeneratedFile(
            path="device/generic/car/emulator/car_emulator_config.json",
            content=VhalCodeGenerator._generate_config_json(config),
            description="Emulator configuration"
        ))
        
        files.append(GeneratedFile(
            path="system/sepolicy/private/car_service.te",
            content=VhalCodeGenerator._generate_sepolicy(config),
            description="SELinux policy rules"
        ))
        
        return files
    
    @staticmethod
    def _generate_types_hal(config: VhalPropertyConfig) -> str:
        """Generate types.hal content"""
        content = f"""/*
 * Copyright (C) 2024 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 */

// Add this to hardware/interfaces/automotive/vehicle/2.0/types.hal

enum VehicleProperty : int32_t {{
    // ... existing properties ...
    
    /**
     * {config.description}
     *
     * @change_mode {config.change_mode}
     * @access {config.access}
     * @data_type {config.type}
     {"@unit " + config.units if config.units else ""}
     */
    {config.name} = {config.id},
}};"""
        
        if config.enum_values:
            content += f"""

/**
 * Enum values for {config.name}
 */
enum {config.name}Values : int32_t {{
"""
            for enum_name, enum_value in config.enum_values.items():
                content += f"    {enum_name} = {enum_value},\n"
            content += "};"
        
        return content
    
    @staticmethod
    def _generate_default_config_h(config: VhalPropertyConfig) -> str:
        """Generate DefaultConfig.h additions"""
        areas_config = ""
        if config.areas:
            areas_list = " | ".join([f"VehicleArea::{area}" for area in config.areas])
            areas_config = f"    .areaConfigs = {{{areas_list}}},"
        
        min_max_config = ""
        if config.min_value is not None and config.max_value is not None:
            min_max_config = f"""    .minSampleRate = {config.sample_rate_hz or 1.0}f,
    .maxSampleRate = {config.sample_rate_hz or 10.0}f,"""
        
        return f"""/*
 * Add this configuration to DefaultConfig.h
 */

{{
    .config = {{
        .prop = static_cast<int32_t>(VehicleProperty::{config.name}),
        .access = VehiclePropertyAccess::{config.access},
        .changeMode = VehiclePropertyChangeMode::{config.change_mode},
{areas_config}
{min_max_config}
    }},
    .initialValue = {VhalCodeGenerator._get_default_value(config.type)},
}},"""
    
    @staticmethod
    def _generate_emulated_hal_cpp(config: VhalPropertyConfig) -> str:
        """Generate EmulatedVehicleHal.cpp additions"""
        return f"""/*
 * Add this to EmulatedVehicleHal.cpp
 */

// In the appropriate get/set property methods:

case static_cast<int32_t>(VehicleProperty::{config.name}): {{
    // Handle {config.name} property
    {VhalCodeGenerator._generate_property_handler(config)}
    break;
}}"""
    
    @staticmethod
    def _generate_aidl_property(config: VhalPropertyConfig) -> str:
        """Generate AIDL property definition"""
        return f"""/*
 * Add this to VehicleProperty.aidl
 */

/**
 * {config.description}
 */
{config.name} = {config.id},"""
    
    @staticmethod
    def _generate_java_constants(config: VhalPropertyConfig) -> str:
        """Generate Java constants"""
        return f"""/*
 * Add this to VehiclePropertyIds.java
 */

/**
 * {config.description}
 * 
 * @hide
 */
@SystemApi
public static final int {config.name} = {config.id};"""
    
    @staticmethod
    def _generate_car_property_manager(config: VhalPropertyConfig) -> str:
        """Generate CarPropertyManager integration"""
        method_name = VhalCodeGenerator._to_camel_case(config.name)
        java_type = VhalCodeGenerator._get_java_type(config.type)
        
        get_method = f"""
    /**
     * Get {config.description.lower()}
     * 
     * @return Current value of {config.name}
     */
    public {java_type} get{method_name}() {{
        return get{java_type}Property(VehiclePropertyIds.{config.name}, 0);
    }}"""
        
        set_method = ""
        if config.access in ["WRITE", "READ_WRITE"]:
            set_method = f"""
    /**
     * Set {config.description.lower()}
     * 
     * @param value New value for {config.name}
     */
    public void set{method_name}({java_type} value) {{
        set{java_type}Property(VehiclePropertyIds.{config.name}, 0, value);
    }}"""
        
        return f"""/*
 * Add these methods to CarPropertyManager.java
 */
{get_method}{set_method}"""
    
    @staticmethod
    def _generate_hal_test(config: VhalPropertyConfig) -> str:
        """Generate HAL test file"""
        return f"""/*
 * Add this test to VehicleHalTest.cpp
 */

TEST_F(VehicleHalTest, {config.name}Test) {{
    // Test property configuration
    auto propConfig = mVehicleHal->getPropConfigs({{static_cast<int32_t>(VehicleProperty::{config.name})}} );
    ASSERT_EQ(propConfig.size(), 1);

    auto& config = propConfig[0];
    EXPECT_EQ(config.prop, static_cast<int32_t>(VehicleProperty::{config.name}));
    EXPECT_EQ(config.access, VehiclePropertyAccess::{config.access});
    EXPECT_EQ(config.changeMode, VehiclePropertyChangeMode::{config.change_mode});

    {VhalCodeGenerator._generate_test_cases(config)}
}}"""
    
    @staticmethod
    def _generate_java_test(config: VhalPropertyConfig) -> str:
        """Generate Java test file"""
        method_name = VhalCodeGenerator._to_camel_case(config.name)
        
        return f"""/*
 * Add this test to VehiclePropertyTest.java
 */

@Test
public void test{method_name}() {{
    // Test property exists
    assertTrue("Property {config.name} should be supported", 
               mCarPropertyManager.isPropertyAvailable(VehiclePropertyIds.{config.name}, 0));
    
    {VhalCodeGenerator._generate_java_test_cases(config)}
}}"""
    
    @staticmethod
    def _generate_config_json(config: VhalPropertyConfig) -> str:
        """Generate configuration JSON"""
        config_dict = {
            "property": config.name,
            "defaultValue": VhalCodeGenerator._get_default_value_json(config.type),
            "access": config.access,
            "changeMode": config.change_mode,
            "type": config.type
        }
        
        if config.areas:
            config_dict["areas"] = config.areas
        
        if config.min_value is not None:
            config_dict["minValue"] = config.min_value
        
        if config.max_value is not None:
            config_dict["maxValue"] = config.max_value
        
        return json.dumps(config_dict, indent=2)
    
    @staticmethod
    def _generate_sepolicy(config: VhalPropertyConfig) -> str:
        """Generate SEPolicy rules"""
        return f"""# Add this to car_service.te

# Allow car service to access {config.name}
allow car_service vehicle_hal:binder call;
allow car_service vehicle_hal:fd use;"""
    
    @staticmethod
    def _generate_summary(config: VhalPropertyConfig, file_count: int) -> str:
        """Generate implementation summary"""
        return f"""# VHAL Implementation Summary: {config.name}

## Property Configuration
- **Property Name**: {config.name}
- **Property ID**: {config.id}
- **Description**: {config.description}
- **Type**: {config.type}
- **Group**: {config.group}
- **Access**: {config.access}
- **Change Mode**: {config.change_mode}
{"- **Units**: " + config.units if config.units else ""}
{"- **Range**: " + str(config.min_value) + " to " + str(config.max_value) if config.min_value is not None else ""}
{"- **Sample Rate**: " + str(config.sample_rate_hz) + " Hz" if config.sample_rate_hz else ""}

## Generated Files
Total files generated: {file_count}

## Next Steps
1. Review all generated code sections
2. Integrate the code into your AAOS build
3. Compile and test the implementation
4. Run the generated test cases
5. Test with actual hardware

## Build Commands
```bash
# Build the HAL
mmma hardware/interfaces/automotive/vehicle/2.0/

# Build Car Service
mmma packages/services/Car/

# Run tests
atest VehicleHalTest VehiclePropertyTest
```

Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"""
    
    @staticmethod
    def _generate_implementation_guide(config: VhalPropertyConfig) -> str:
        """Generate implementation guide"""
        return f"""# {config.name} Implementation Guide

## Overview
{config.description}

## Property Details
- **Name**: {config.name}
- **ID**: {config.id}
- **Type**: {config.type}
- **Group**: {config.group}
- **Access**: {config.access}
- **Change Mode**: {config.change_mode}

## Implementation Files

### 1. HAL Definition
- **File**: `hardware/interfaces/automotive/vehicle/2.0/types.hal`
- **Purpose**: Define the property constant and enum values

### 2. Default Implementation
- **File**: `hardware/interfaces/automotive/vehicle/2.0/default/impl/vhal_v2_0/DefaultConfig.h`
- **Purpose**: Configure default behavior and constraints

### 3. HAL Implementation
- **File**: `hardware/interfaces/automotive/vehicle/2.0/default/impl/vhal_v2_0/EmulatedVehicleHal.cpp`
- **Purpose**: Implement get/set logic for the property

### 4. AIDL Interface
- **File**: `hardware/interfaces/automotive/vehicle/aidl/android/hardware/automotive/vehicle/VehicleProperty.aidl`
- **Purpose**: Expose property to framework

### 5. Java Constants
- **File**: `packages/services/Car/car-lib/src/android/car/VehiclePropertyIds.java`
- **Purpose**: Provide Java constant for app developers

### 6. CarPropertyManager
- **File**: `packages/services/Car/car-lib/src/android/car/hardware/property/CarPropertyManager.java`
- **Purpose**: Provide convenience methods for accessing the property

## Testing
- Unit tests in `VehicleHalTest.cpp`
- Integration tests in `VehiclePropertyTest.java`
- Manual testing with sample applications

## Usage Example

```java
// In your Android application
CarPropertyManager carPropertyManager = car.getCarManager(Car.PROPERTY_SERVICE);

// Read property value
{VhalCodeGenerator._get_java_type(config.type)} value = carPropertyManager.get{VhalCodeGenerator._to_camel_case(config.name)}();

{"// Write property value" if config.access in ["WRITE", "READ_WRITE"] else ""}
{"carPropertyManager.set" + VhalCodeGenerator._to_camel_case(config.name) + "(newValue);" if config.access in ["WRITE", "READ_WRITE"] else ""}
```

## Dependencies
{chr(10).join([f"- {dep}" for dep in config.dependencies]) if config.dependencies else "None"}

## Notes
- Ensure proper permissions are set in AndroidManifest.xml
- Test thoroughly on actual hardware before deployment
- Consider backward compatibility when modifying existing properties"""
    
    # Helper methods
    @staticmethod
    def _get_default_value(property_type: str) -> str:
        """Get default value based on property type"""
        type_defaults = {
            "BOOLEAN": "false",
            "INT32": "0",
            "INT64": "0L",
            "FLOAT": "0.0f",
            "STRING": '""',
            "BYTES": "{}",
            "INT32_VEC": "{}",
            "FLOAT_VEC": "{}",
            "STRING_VEC": "{}",
            "BYTES_VEC": "{}",
            "MIXED": "{}"
        }
        return type_defaults.get(property_type, "0")
    
    @staticmethod
    def _get_default_value_json(property_type: str) -> Any:
        """Get default value for JSON config"""
        type_defaults = {
            "BOOLEAN": False,
            "INT32": 0,
            "INT64": 0,
            "FLOAT": 0.0,
            "STRING": "",
            "BYTES": [],
            "INT32_VEC": [],
            "FLOAT_VEC": [],
            "STRING_VEC": [],
            "BYTES_VEC": [],
            "MIXED": {}
        }
        return type_defaults.get(property_type, 0)
    
    @staticmethod
    def _get_java_type(property_type: str) -> str:
        """Get Java type for property"""
        type_mapping = {
            "BOOLEAN": "Boolean",
            "INT32": "Integer",
            "INT64": "Long",
            "FLOAT": "Float",
            "STRING": "String",
            "BYTES": "byte[]",
            "INT32_VEC": "Integer[]",
            "FLOAT_VEC": "Float[]",
            "STRING_VEC": "String[]",
            "BYTES_VEC": "byte[][]",
            "MIXED": "Object"
        }
        return type_mapping.get(property_type, "Object")
    
    @staticmethod
    def _to_camel_case(snake_str: str) -> str:
        """Convert snake_case to CamelCase"""
        components = snake_str.split('_')
        return ''.join(word.capitalize() for word in components)
    
    @staticmethod
    def _generate_property_handler(config: VhalPropertyConfig) -> str:
        """Generate property handler code"""
        if config.access == "READ":
            return "// Read-only property - return current value"
        elif config.access == "WRITE":
            return "// Write-only property - store value and trigger callbacks"
        else:
            return "// Read-write property - handle both get and set operations"
    
    @staticmethod
    def _generate_test_cases(config: VhalPropertyConfig) -> str:
        """Generate test cases"""
        test_cases = []
        
        if config.access in ["READ", "READ_WRITE"]:
            test_cases.append("// Test reading property value")
        
        if config.access in ["WRITE", "READ_WRITE"]:
            test_cases.append("// Test writing property value")
        
        if config.min_value is not None and config.max_value is not None:
            test_cases.append("// Test boundary values")
        
        return "\n    ".join(test_cases)
    
    @staticmethod
    def _generate_java_test_cases(config: VhalPropertyConfig) -> str:
        """Generate Java test cases"""
        method_name = VhalCodeGenerator._to_camel_case(config.name)
        java_type = VhalCodeGenerator._get_java_type(config.type)
        
        test_cases = []
        
        if config.access in ["READ", "READ_WRITE"]:
            test_cases.append(f"// Test reading\n    {java_type} value = mCarPropertyManager.get{method_name}();")
        
        if config.access in ["WRITE", "READ_WRITE"]:
            default_value = "true" if config.type == "BOOLEAN" else "123"
            test_cases.append(f"// Test writing\n    mCarPropertyManager.set{method_name}({default_value});")
        
        return "\n    ".join(test_cases)
    
    @staticmethod
    def _get_file_extension(file_path: str) -> str:
        """Get appropriate syntax highlighting language for file path"""
        if file_path.endswith('.hal'):
            return 'cpp'  # HAL files use C++-like syntax
        elif file_path.endswith('.h') or file_path.endswith('.cpp'):
            return 'cpp'
        elif file_path.endswith('.java'):
            return 'java'
        elif file_path.endswith('.aidl'):
            return 'java'  # AIDL is Java-like
        elif file_path.endswith('.json'):
            return 'json'
        elif file_path.endswith('.te'):
            return 'bash'  # SEPolicy files
        else:
            return 'text'
