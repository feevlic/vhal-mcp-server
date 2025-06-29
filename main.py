#!/usr/bin/env python3

from src.vhal_mcp_server.server import mcp


def main():
    """Run the vHAL MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
