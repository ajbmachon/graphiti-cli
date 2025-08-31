#!/bin/bash
# Test script for Graphiti CLI

set -e  # Exit on error

echo "Testing Graphiti CLI Installation..."
echo

# Check if graphiti command is available
if ! command -v graphiti &> /dev/null; then
    echo "❌ Error: 'graphiti' command not found"
    echo "Please install with: pip install -e ."
    exit 1
fi

# Check environment variables
if [ -z "$NEO4J_PASSWORD" ]; then
    echo "❌ Error: NEO4J_PASSWORD not set"
    exit 1
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY not set, some operations may fail"
fi

echo "✅ Environment variables configured"
echo

# Test basic functionality
echo "Testing basic search..."
if graphiti search "test" --max-results 1 > /dev/null 2>&1; then
    echo "✅ Basic search working"
else
    echo "❌ Basic search failed"
    exit 1
fi

echo "Testing help command..."
if graphiti --help > /dev/null 2>&1; then
    echo "✅ Help command working"
else
    echo "❌ Help command failed"
    exit 1
fi

echo "Testing search help..."
if graphiti search --help > /dev/null 2>&1; then
    echo "✅ Search help working"
else
    echo "❌ Search help failed"
    exit 1
fi

echo "Testing JSON output..."
if graphiti search "test" --max-results 1 | jq '.' > /dev/null 2>&1; then
    echo "✅ JSON output valid"
else
    echo "❌ JSON output invalid"
    exit 1
fi

echo
echo "✅ All tests passed! Graphiti CLI is working correctly."
echo
echo "Try these commands:"
echo "  graphiti search \"your query\""
echo "  graphiti search \"\" --created-after \"2024-01-01\""
echo "  graphiti maintenance stats"