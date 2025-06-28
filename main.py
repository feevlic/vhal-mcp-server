#!/usr/bin/env python3
"""vHAL MCP Server entry point."""

from server import mcp


def main():
    """Run the vHAL MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
