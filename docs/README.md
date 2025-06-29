# Documentation

This directory contains documentation and media files for the vHAL MCP Server project.

## Assets

- `assets/` - Contains media files like demo videos and screenshots

## Project Structure

The project follows a professional Python package structure:

```
vhal-mcp-server/
├── src/vhal_mcp_server/     # Main package source code
│   ├── core/                # Core functionality (database, analyzers, scrapers)
│   ├── generators/          # Code and documentation generators
│   ├── utils/               # Utility functions and helpers
│   ├── server.py           # Main MCP server implementation
│   └── models.py           # Data models and types
├── tests/                   # Test suite
├── docs/                    # Documentation and assets
├── config/                  # Configuration files
└── main.py                  # Application entry point
```

## Development

The modular structure makes it easy to:

- Add new property analyzers in `core/`
- Extend code generation capabilities in `generators/`
- Add utility functions in `utils/`
- Write comprehensive tests in `tests/`
- Maintain configuration separately in `config/`
