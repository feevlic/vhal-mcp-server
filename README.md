# vHal MCP Server

MCP server for Android Vehicle Hardware Abstraction Layer (vHAL) documentation and source code analysis. This server provides intelligent tools for exploring vHAL properties, understanding their relationships, and implementing automotive climate control systems.

## Overview

The vHAL MCP Server helps Android Automotive developers by providing:

- **Property Analysis**: Discover vHAL properties and their relationships
- **Source Code Lookup**: Find Android source code implementations
- **Implementation Guidance**: Get step-by-step implementation recommendations
- **Documentation Summarization**: Access curated vHAL documentation insights

## Demo

See the vHAL MCP Server in action:

https://github.com/user-attachments/assets/6fcdc5fb-6cbb-4c69-9528-fa3bdee4acb1

*Example: Analyzing HVAC properties and implementation guidance using Claude Desktop with the vHAL MCP Server*

## Features

### Core Tools

**`summarize_vhal(question)`**
- Summarizes vHAL implementation based on specific questions
- Analyzes Android automotive documentation
- Provides contextual answers for vHAL development

**`lookup_android_source_code(keyword, category)`**
- Searches Android source code for vHAL properties
- Returns property definitions with IDs and categories
- Provides direct links to source code locations

**`discover_related_properties(property_or_category)`**
- Analyzes property relationships and dependencies
- Suggests implementation order for complex features
- Groups properties by functional categories

**`analyze_vhal_implementation(property_name)`**
- Shows detailed source code analysis for specific properties
- Provides implementation examples and usage patterns
- Includes dependency analysis and best practices

**`generate_vhal_implementation_code(...)`**
- Generates complete VHAL property implementation code for AAOS
- Creates all necessary files, configurations, tests, and documentation
- Supports all VHAL data types, property groups, and access modes
- Includes HAL definitions, Java APIs, tests, and build configurations


**`generate_vhal_pr_message(...)`**
- Generates comprehensive pull request messages for VHAL implementations
- Creates structured PR descriptions with technical details and testing requirements
- Includes professional titles, change summaries, and review checklists
- Ready-to-copy-paste format for GitHub/GitLab integration


## Installation

### Prerequisites

- Python 3.12 or higher
- Internet connection for documentation scraping
- MCP-compatible client (Claude Desktop, Zed, or other MCP clients)

### Local Setup

1. **Clone the repository**
   
   Using HTTPS:
   ```bash
   git clone https://github.com/feevlic/vhal-mcp-server.git
   ```
   
   Using SSH:
   ```bash
   git clone git@github.com:feevlic/vhal-mcp-server.git
   ```

2. **Navigate to the project directory**
   ```bash
   cd vhal-mcp-server
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   ```

### MCP Client Configuration

#### Claude Desktop Configuration

1. **Find your `uv` installation path**
   ```bash
   which uv
   ```

2. **Locate your Claude Desktop configuration file**
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

3. **Add the server configuration**
   
   Edit the configuration file and add the following (replace the paths with your actual paths):
   ```json
   {
     "mcpServers": {
       "vhal-mcp-server": {
         "command": "/path/to/your/uv",
         "args": ["run", "--directory", "/path/to/vhal-mcp-server", "python", "main.py"],
         "env": {}
       }
     }
   }
   ```

You can find an example in the config folder.

   **Important**: 
   - Replace `/path/to/your/uv` with the output from step 1 (e.g., `/Users/yourusername/.local/bin/uv`)
   - Replace `/path/to/vhal-mcp-server` with the actual path where you cloned the repository
   - On macOS, GUI applications like Claude Desktop may not have access to your shell's PATH, so using full paths is required

4. **Restart Claude Desktop**
   
   After saving the configuration file, completely quit and restart Claude Desktop for the MCP server to be loaded.

5. **Allow MCP server access**
   
   When you first ask a question that requires the vHAL tools, Claude will prompt you to allow the MCP server to use its tools. Click "Allow" to enable the vHAL analysis capabilities.

## Usage

### Basic Usage

The server exposes MCP tools that can be used through compatible clients. Each tool accepts specific parameters and returns structured information about vHAL properties and implementations.

### Beginner Prompt Examples

Start with these simple prompts to explore vHAL capabilities:

**Basic Property Discovery**
```
Show me all HVAC-related properties and their IDs
```

**Simple Implementation Questions**
```
How do I control the fan speed in Android Automotive?
```

**Property Lookup**
```
Find Android source code for seat heating properties
```

**Basic Temperature Control**
```
What properties do I need to set the cabin temperature?
```

**Understanding Property Types**
```
Explain the HVAC_POWER_ON property and how to use it
```

### Advanced Prompt Examples

Once familiar with basic concepts, try these comprehensive prompts:

**Complete System Implementation**
```
I need to implement a climate control system. Can you:
1. Find all HVAC-related properties
2. Explain their relationships and dependencies  
3. Show me the Android source code implementation
4. Provide a step-by-step implementation guide

Please give me a complete analysis for building this system.
```

**Multi-Zone Climate Control**
```
Analyze the implementation requirements for a dual-zone HVAC system. Include:
- Property relationships between driver and passenger zones
- Dependencies and implementation order
- Source code examples from Android
- Best practices for zone management
```

**Seat Memory System**
```
Design a comprehensive seat memory system that includes:
- Position storage and recall (8-way adjustment)
- Heating and cooling integration
- Memory profile management
- Safety considerations and dependencies

Show me the vHAL properties needed and implementation approach.
```

**Safety-Critical Features**
```
I'm implementing defrost and safety features. Analyze:
- Priority systems for defrost override
- Integration with HVAC main system
- Emergency defrost activation
- Window clearing effectiveness

Provide source code examples and safety considerations.
```

**Performance Optimization**
```
Optimize my HVAC implementation for energy efficiency:
- Auto mode algorithms
- Fan speed optimization
- AC compressor management
- Integration with vehicle power management

Include Android source examples and power consumption strategies.
```

**Custom Property Development**
```
I want to add a new custom HVAC feature for air quality monitoring. Help me:
- Understand the property definition process
- Find similar existing properties for reference
- Design the property specification
- Plan the HAL implementation approach
```

### VHAL Code Generation Examples

Use the `generate_vhal_implementation_code` tool to create complete VHAL implementations:

**Smart Dashboard Lighting System**
```
Generate a complete VHAL implementation for a smart dashboard lighting system with the following specifications:

- Property Name: DASHBOARD_SMART_LIGHTING_MODE
- Property ID: 0x15400B01
- Type: INT32 (enumerated values)
- Group: LIGHTS
- Access: READ_WRITE
- Change Mode: ON_CHANGE
- Description: Smart dashboard lighting control with adaptive brightness and color temperature
- Enum Values: OFF=0, AUTO=1, DAY=2, NIGHT=3, CUSTOM=4
- Dependencies: NIGHT_MODE, CABIN_LIGHTS_STATE

Please use the generate_vhal_implementation_code tool.
```

**Electric Vehicle Charging Management**
```
I need to implement a comprehensive EV charging management system. Create a VHAL property with these requirements:

- Property Name: EV_CHARGING_PORT_STATUS
- Property ID: 0x15400C01
- Type: INT32 (enum)
- Group: POWER
- Access: READ (status monitoring only)
- Change Mode: ON_CHANGE
- Description: Electric vehicle charging port status and connection state
- Enum Values: DISCONNECTED=0, CONNECTED=1, CHARGING=2, ERROR=3, COMPLETE=4, SCHEDULED=5
- Dependencies: EV_BATTERY_LEVEL, EV_CHARGING_RATE
- Areas: GLOBAL

Generate the complete implementation using generate_vhal_implementation_code.
```

**Advanced HVAC Zone Control**
```
Implement an advanced HVAC zone control system for precise temperature management:

- Property Name: HVAC_ZONE_CLIMATE_PROFILE
- Property ID: 0x15400D01
- Type: FLOAT
- Group: HVAC
- Access: READ_WRITE
- Change Mode: CONTINUOUS
- Description: Advanced HVAC zone climate profile with precise temperature control
- Units: celsius
- Min Value: 16.0
- Max Value: 32.0
- Areas: ["SEAT_ROW_1_LEFT", "SEAT_ROW_1_RIGHT", "SEAT_ROW_2_LEFT", "SEAT_ROW_2_RIGHT"]
- Dependencies: HVAC_TEMPERATURE_SET, HVAC_FAN_SPEED
- Sample Rate: 0.5 Hz (update every 2 seconds)

Use generate_vhal_implementation_code to create the full implementation.
```

**Biometric Seat Adjustment**
```
Create a biometric-based seat adjustment system:

- Property Name: SEAT_BIOMETRIC_PROFILE
- Property ID: 0x15400E01
- Type: STRING
- Group: SEAT
- Access: READ_WRITE
- Change Mode: ON_CHANGE
- Description: Biometric-based automatic seat adjustment with user recognition
- Areas: ["SEAT_ROW_1_LEFT", "SEAT_ROW_1_RIGHT"]
- Dependencies: SEAT_HEIGHT_POS, SEAT_FORE_AFT_POS, SEAT_RECLINE_ANGLE

Generate the complete VHAL implementation.
```

### VHAL Pull Request Generation Examples

Use the `generate_vhal_pr_message` tool to create professional pull request messages:

**Smart Dashboard Lighting PR**
```
Generate a comprehensive pull request message for my smart dashboard lighting implementation:

- Property Name: DASHBOARD_SMART_LIGHTING_MODE
- Property ID: 0x15400B01
- Type: INT32
- Group: LIGHTS
- Access: READ_WRITE
- Change Mode: ON_CHANGE
- Description: Smart dashboard lighting control with adaptive brightness and color temperature
- Enum Values: {"OFF": 0, "AUTO": 1, "DAY": 2, "NIGHT": 3, "CUSTOM": 4}
- Dependencies: ["NIGHT_MODE", "CABIN_LIGHTS_STATE"]
- JIRA Ticket: AUTO-1234
- Reviewer Suggestions: ["Verify power consumption impact", "Test night mode transitions"]

Please use the generate_vhal_pr_message tool.
```

**EV Charging System PR**
```
Create a pull request message for my electric vehicle charging management system:

- Property Name: EV_CHARGING_PORT_STATUS
- Property ID: 0x15400C01
- Type: INT32
- Group: POWER
- Access: READ
- Change Mode: ON_CHANGE
- Description: Electric vehicle charging port status and connection state
- Enum Values: {"DISCONNECTED": 0, "CONNECTED": 1, "CHARGING": 2, "ERROR": 3, "COMPLETE": 4, "SCHEDULED": 5}
- Dependencies: ["EV_BATTERY_LEVEL", "EV_CHARGING_RATE"]
- Areas: ["GLOBAL"]
- Breaking Change: false

Generate the complete PR message.
```

**Advanced HVAC Zone Control PR**
```
Generate a pull request message for my advanced HVAC zone control implementation:

- Property Name: HVAC_ZONE_CLIMATE_PROFILE
- Property ID: 0x15400D01
- Type: FLOAT
- Group: HVAC
- Access: READ_WRITE
- Change Mode: CONTINUOUS
- Description: Advanced HVAC zone climate profile with precise temperature control
- Units: celsius
- Min Value: 16.0
- Max Value: 32.0
- Areas: ["SEAT_ROW_1_LEFT", "SEAT_ROW_1_RIGHT", "SEAT_ROW_2_LEFT", "SEAT_ROW_2_RIGHT"]
- Dependencies: ["HVAC_TEMPERATURE_SET", "HVAC_FAN_SPEED"]
- Sample Rate: 0.5
- Breaking Change: false
- JIRA Ticket: HVAC-567
- Reviewer Suggestions: ["Review energy efficiency impact", "Validate zone isolation"]

Create a professional PR message with all technical details and checklists.
```


### Expert Prompt: Complete VHAL System Development

This expert-level prompt demonstrates using all 5 MCP tools in a comprehensive workflow for developing a complete automotive system:

```
I'm developing a next-generation intelligent climate control system for luxury electric vehicles. This system needs to integrate multiple subsystems and provide personalized comfort experiences. Please help me design and implement this system using a comprehensive analysis approach:

**Phase 1: Discovery & Research (Tools 1-2)**
First, help me understand the complete landscape:
1. explain the overall VHAL climate control architecture, focusing on:
   - Multi-zone HVAC systems
   - Integration with seat heating/cooling
   - Energy efficiency considerations for EVs
   - Safety and emergency override systems

2. find all climate-related properties, including:
   - HVAC properties (search: "HVAC")
   - Seat thermal properties (search: "SEAT")
   - Power management properties (search: "POWER")
   - Any auxiliary heating properties (search: "HEAT")

**Phase 2: System Analysis & Dependencies (Tool 3)**
3. analyze the complete ecosystem for:
   - "HVAC_TEMPERATURE_SET" - understand temperature control relationships
   - "SEAT_HEAT" - analyze seat thermal dependencies
   - "HVAC_POWER_ON" - understand system power relationships
   - "HVAC_FAN_SPEED" - analyze airflow control dependencies

**Phase 3: Implementation Deep-Dive (Tool 4)**
4. get detailed source code analysis for:
   - "HVAC_TEMPERATURE_SET" - see how Android implements temperature control
   - "HVAC_AUTO_ON" - understand automatic mode implementation
   - "SEAT_HEAT_LEFT" - analyze seat heating implementation patterns
   - "HVAC_AC_ON" - understand AC compressor control

**Phase 5: Custom Implementation (Tool 5)**
5. Based on the analysis create a new intelligent climate property:

- Property Name: CLIMATE_INTELLIGENT_PROFILE
- Property ID: 0x15400F01
- Type: INT32 (enumerated values)
- Group: HVAC
- Access: READ_WRITE
- Change Mode: ON_CHANGE
- Description: Intelligent climate control with predictive comfort algorithms, energy optimization, and personalized user profiles
- Enum Values: PROFILE_ECO=0, PROFILE_COMFORT=1, PROFILE_SPORT=2, PROFILE_CUSTOM=3, PROFILE_SLEEP=4, PROFILE_DEFROST_PRIORITY=5
- Dependencies: HVAC_TEMPERATURE_SET, HVAC_FAN_SPEED, SEAT_HEAT_LEFT, SEAT_HEAT_RIGHT, HVAC_AC_ON, EV_BATTERY_LEVEL
- Units: none
- Areas: ["GLOBAL", "SEAT_ROW_1_LEFT", "SEAT_ROW_1_RIGHT"]

6. Plase also add a pull reuest message i can add to the Pull request once i implemented it.

**Expected Deliverables:**
After running this comprehensive analysis, I expect to receive:

1. **Complete System Understanding** -  architectural overview and best practices
2. **Property Inventory** -  all relevant properties with IDs and locations
3. **Dependency Maps** - implementation order and relationships
4. **Implementation Patterns** -  real Android source code examples
5. **Production-Ready Code** -  complete implementation files
6. **Pull Request Text** - Copy and Paste Pull request text

This comprehensive approach will give me everything needed to implement a production-quality intelligent climate control system.
```

### VHAL Code Generator Features

The `generate_vhal_implementation_code` tool creates complete, production-ready VHAL implementations:

#### Generated Files

For each VHAL property, the generator creates:

**Core HAL Files:**
- `types.hal` - Property definition and enums
- `DefaultConfig.h` - Property configuration
- `EmulatedVehicleHal.cpp` - Implementation logic
- `VehicleProperty.aidl` - AIDL interface

**Framework Integration:**
- `VehiclePropertyIds.java` - Java constants
- `CarPropertyManager.java` - API methods
- Configuration JSON files

**Testing:**
- `VehicleHalTest.cpp` - C++ unit tests
- `VehiclePropertyTest.java` - Java integration tests

**System Configuration:**
- SEPolicy rules
- Build configurations
- Documentation

#### Tool Parameters

**Required:**
- `name`: Property name (e.g., "HVAC_STEERING_WHEEL_HEAT")
- `property_id`: Unique property ID (hex format, e.g., "0x15400A03")
- `property_type`: Data type (BOOLEAN, INT32, INT64, FLOAT, STRING, BYTES, *_VEC, MIXED)
- `group`: Property group (HVAC, SEAT, LIGHTS, POWER, CLIMATE, etc.)
- `access`: Access mode (READ, WRITE, READ_WRITE)
- `change_mode`: Change mode (STATIC, ON_CHANGE, CONTINUOUS)
- `description`: Property description for documentation

**Optional:**
- `units`: Units (e.g., "celsius", "rpm")
- `min_value`: Minimum value for numeric types
- `max_value`: Maximum value for numeric types
- `areas`: List of vehicle areas/zones
- `enum_values`: Dict of enum names and values for INT32 enum properties
- `dependencies`: List of dependent property names
- `sample_rate_hz`: Sample rate for continuous properties

#### Property Types Supported

**Basic Types:**
- **BOOLEAN**: True/false values
- **INT32**: 32-bit integers
- **INT64**: 64-bit integers  
- **FLOAT**: Floating point numbers
- **STRING**: Text values
- **BYTES**: Binary data

**Vector Types:**
- **INT32_VEC**: Arrays of integers
- **FLOAT_VEC**: Arrays of floats
- **STRING_VEC**: Arrays of strings
- **BYTES_VEC**: Arrays of binary data

**Special Types:**
- **MIXED**: Complex structured data

#### Property Groups

- **BODY**: Body control systems
- **CABIN**: Interior cabin controls
- **CLIMATE**: Climate control systems
- **DISPLAY**: Display and infotainment
- **ENGINE**: Engine management
- **HVAC**: Heating, ventilation, air conditioning
- **INFO**: Vehicle information
- **INSTRUMENT_CLUSTER**: Dashboard instruments
- **LIGHTS**: Lighting systems
- **MIRROR**: Mirror controls
- **POWER**: Power management
- **SEAT**: Seat controls
- **VEHICLE_MAP_SERVICE**: Navigation services
- **WINDOW**: Window controls
- **VENDOR**: Vendor-specific properties

#### Generated Output

When you use the code generator, it produces:

1. **Complete Summary** - Property configuration and overview
2. **Generated Files** - All 10+ necessary implementation files with syntax highlighting
3. **Implementation Guide** - Step-by-step integration instructions
4. **Usage Examples** - Sample code for using the property
5. **Build Commands** - AAOS build and test commands

## Use Cases

### Climate Control System Development

Implement comprehensive HVAC systems with proper property relationships:

- **Temperature Control**: Multi-zone heating and cooling
- **Fan Management**: Speed and direction control with feedback
- **Air Conditioning**: AC compressor and recirculation control
- **Auxiliary Heating**: Seat warmers, steering wheel, and mirror heating
- **Safety Features**: Defrost and defogging capabilities

### Seat Control Systems

Develop advanced seat control features:

- **Memory Systems**: Position storage and recall
- **Comfort Features**: Heating, cooling, and massage functions
- **Movement Control**: Multi-axis positioning and adjustment
- **Safety Integration**: Occupancy detection and airbag coordination

### Property Discovery and Analysis

Understand vHAL property ecosystems:

- **Dependency Mapping**: Identify property relationships
- **Implementation Planning**: Get step-by-step development guidance
- **Source Code Analysis**: Access real Android implementations
- **Best Practices**: Learn from existing property patterns

## Configuration

### MCP Client Integration

To use with MCP-compatible clients, configure the server endpoint and ensure proper tool registration. The server automatically discovers and exposes all available vHAL analysis tools.

### Performance Optimization

The server uses parallel scraping and caching mechanisms for optimal performance:

- **Parallel Documentation Scraping**: Concurrent fetching of Android documentation
- **Property Database Caching**: In-memory storage of frequently accessed properties
- **Source Code Analysis Caching**: Optimized repeated analysis operations

## Development

### Project Structure

```
vhal-mcp-server/
├── server.py              # Main MCP server implementation
├── analyzers.py           # Source code analysis tools
├── database.py            # Property database and lookups
├── relationships.py       # Property relationship analysis
├── scrapers.py           # Documentation scraping utilities
├── summarizers.py        # Documentation summarization
├── models.py             # Data models and structures
└── tests/                # Test suite
```

### Testing

Run the test suite:
```bash
python -m pytest test_vhal.py -v
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes with tests
4. Submit a pull request

## Requirements

- **mcp[cli]** >= 1.10.1 - Model Context Protocol implementation
- **requests** >= 2.31.0 - HTTP client for documentation scraping
- **beautifulsoup4** >= 4.12.0 - HTML parsing for documentation
- **lxml** >= 4.9.0 - XML/HTML processing

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Support

For questions, issues, or contributions:

- **Repository**: https://github.com/feevlic/vhal-mcp-server
- **Issues**: https://github.com/feevlic/vhal-mcp-server/issues
- **Documentation**: Refer to Android vHAL documentation at https://source.android.com/docs/automotive/vhal

## Related Resources

- [Android Automotive Documentation](https://source.android.com/docs/automotive)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
