# vHAL MCP Server

A Model Context Protocol (MCP) server that provides access to Android Vehicle Hardware Abstraction Layer (vHAL) documentation and source code information.

## Features

- **Documentation Summarization**: Query vHAL documentation with natural language questions
- **Source Code Lookup**: Find Android source code locations and property definitions
- **Property Database**: Access to comprehensive vHAL property definitions and IDs

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
