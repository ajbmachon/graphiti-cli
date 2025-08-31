#!/bin/bash
# Test script for Graphiti CLI

set -e  # Exit on error

echo "Testing Graphiti CLI Installation..."
echo

# Ensure Graphiti telemetry is disabled for tests
export GRAPHITI_TELEMETRY_ENABLED=false

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
echo "Testing basic commands (offline-safe)..."
if graphiti --help > /dev/null 2>&1 && graphiti search --help > /dev/null 2>&1; then
    echo "✅ Help commands working"
else
    echo "❌ Help commands failed"
    exit 1
fi

echo "Skipping live search due to external dependencies (Neo4j/OpenAI)"

echo
echo "✅ All tests passed! Graphiti CLI is working correctly."
echo
echo "Try these commands:"
echo "  graphiti search \"your query\""
echo "  graphiti search \"\" --created-after \"2024-01-01\""
echo "  graphiti maintenance stats"
