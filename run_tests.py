#!/usr/bin/env python3
"""Test runner for vHAL MCP Server.

This script sets up the proper Python path and runs the test suite.
"""

import sys
import os

# Add the current directory to Python path for src imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    from tests.test_vhal import run_basic_tests
    
    print("vHAL MCP Server Test Suite")
    print("=" * 50)
    
    success = run_basic_tests()
    
    if success:
        print("\n All tests passed!")
        sys.exit(0)
    else:
        print("\n Some tests failed!")
        sys.exit(1)
