# vHAL MCP Server

A Model Context Protocol (MCP) server that provides access to Android Vehicle Hardware Abstraction Layer (vHAL) documentation and source code information.

## Features

- **Documentation Summarization**: Query vHAL documentation with natural language questions
- **Source Code Lookup**: Find Android source code locations and property definitions
- **Property Database**: Access to comprehensive vHAL property definitions and IDs
- **🆕 Source Code Analysis**: Fetch and analyze actual Android source code with real implementation examples

## Installation

```bash
# Clone the repository
git clone https://github.com/felixboudnik/vhal-mcp-server.git
cd vhal-mcp-server

# Install dependencies
uv sync
```

## Usage

### As MCP Server

Configure in your MCP client (e.g., Warp terminal):

```json
{
  "mcpServers": {
    "vhal-mcp-server": {
      "command": "uv",
      "args": ["run", "python", "/path/to/vhal-mcp-server/server.py"],
      "cwd": "/path/to/vhal-mcp-server"
    }
  }
}
```

### Direct Testing

```bash
# Run the test suite
python test_vhal.py

# Start the server directly
python server.py
```

## Available Tools

### `summarize_vhal(question: str)`

Summarizes vHAL documentation based on your question.

**Example:**
```python
summarize_vhal("How do seat properties work in vHAL?")
```

### `lookup_android_source_code(keyword: str, category: str = "vhal")`

Looks up Android source code locations and property definitions.

**Example:**
```python
lookup_android_source_code("SEAT_POSITION", "vhal")
```

### `discover_related_properties(property_or_category: str)`

Discovers related properties, dependencies, and suggested implementation order for vHAL property ecosystems.

**Examples:**
```python
# Analyze a property ecosystem
discover_related_properties("SEAT_MEMORY")

# Analyze a specific property
discover_related_properties("SEAT_MEMORY_SELECT")

# Analyze HVAC ecosystem
discover_related_properties("HVAC_BASIC")
```

### `analyze_vhal_implementation(property_name: str)` 🆕

Analyzes Android source code to show how a vHAL property is implemented, including actual source code, file locations, and usage examples.

**Features:**
- **Real Android Source Code**: Fetches actual source files from Android Googlesource
- **Implementation Analysis**: Extracts property definitions and configurations
- **Usage Examples**: Provides C++/AIDL code examples for developers
- **Source Links**: Direct URLs to Android source repositories
- **Documentation**: Links to relevant Android documentation
- **Implementation Tips**: Best practices and development guidance

**Examples:**
```python
# Analyze steering wheel heating implementation
analyze_vhal_implementation("HVAC_STEERING_WHEEL_HEAT")

# Analyze seat memory implementation
analyze_vhal_implementation("SEAT_MEMORY_SELECT")

# Analyze any vHAL property
analyze_vhal_implementation("HVAC_FAN_SPEED")
```

**Output includes:**
- Source code files with syntax highlighting and line numbers
- Property ID and implementation details
- Dependencies and related components
- C++/AIDL usage examples
- File locations and direct links to Android source
- Implementation tips and best practices

## Development

### Project Structure

```
vhal-mcp-server/
├── server.py              # Main MCP server implementation
├── main.py                # Entry point
├── test_vhal.py          # Test suite
├── pyproject.toml        # Project configuration
├── requirements.txt      # Dependencies
└── README.md            # This file
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if needed
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Links

- [Android vHAL Documentation](https://source.android.com/docs/automotive/vhal)
- [Model Context Protocol](https://github.com/modelcontextprotocol/specification)
- [Android Source Code](https://cs.android.com/)
