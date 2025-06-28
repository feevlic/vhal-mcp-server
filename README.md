# vHAL MCP Server

MCP server for Android Vehicle Hardware Abstraction Layer (vHAL) documentation and source code analysis. This server provides intelligent tools for exploring vHAL properties, understanding their relationships, and implementing automotive climate control systems.

## Overview

The vHAL MCP Server helps Android Automotive developers by providing:

- **Property Analysis**: Discover vHAL properties and their relationships
- **Source Code Lookup**: Find Android source code implementations
- **Implementation Guidance**: Get step-by-step implementation recommendations
- **Documentation Summarization**: Access curated vHAL documentation insights

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

## Installation

### Prerequisites

- Python 3.12 or higher
- Internet connection for documentation scraping
- MCP-compatible client (Claude Desktop, Zed, or other MCP clients)

### Local Setup

1. **Clone the repository**
   
   Using HTTPS:
   ```bash
   git clone https://github.com/felixboudnik/vhal-mcp-server.git
   ```
   
   Using SSH:
   ```bash
   git clone git@github.com:felixboudnik/vhal-mcp-server.git
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

   **Important**: 
   - Replace `/path/to/your/uv` with the output from step 1 (e.g., `/Users/yourusername/.local/bin/uv`)
   - Replace `/path/to/vhal-mcp-server` with the actual path where you cloned the repository
   - On macOS, GUI applications like Claude Desktop may not have access to your shell's PATH, so using full paths is required

4. **Restart Claude Desktop**
   
   After saving the configuration file, completely quit and restart Claude Desktop for the MCP server to be loaded.

5. **Allow MCP server access**
   
   When you first ask a question that requires the vHAL tools, Claude will prompt you to allow the MCP server to use its tools. Click "Allow" to enable the vHAL analysis capabilities.

#### Zed Editor Configuration

Add to your Zed settings.json:

```json
{
  "assistant": {
    "default_model": {
      "provider": "anthropic",
      "model": "claude-3-5-sonnet-20241022"
    },
    "version": "2"
  },
  "context_servers": [
    {
      "id": "vhal-mcp-server",
      "executable": "python",
      "args": ["/path/to/vhal-mcp-server/main.py"]
    }
  ]
}
```

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

- **Repository**: https://github.com/felixboudnik/vhal-mcp-server
- **Issues**: https://github.com/felixboudnik/vhal-mcp-server/issues
- **Documentation**: Refer to Android vHAL documentation at https://source.android.com/docs/automotive/vhal

## Related Resources

- [Android Automotive Documentation](https://source.android.com/docs/automotive)
- [Vehicle HAL (vHAL) Properties](https://source.android.com/docs/automotive/vhal/properties)
- [Android Source Code Search](https://cs.android.com/)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
