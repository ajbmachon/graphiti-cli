#!/usr/bin/env python3
"""Test script for natural language query interface."""
import asyncio
import sys
from cli.query.session import QuerySession


async def test_queries():
    """Test various natural language queries."""
    print("Testing Graphiti Natural Language Query Interface\n")
    
    session = QuerySession(temperature=0.2)
    
    test_cases = [
        "show me recent changes",
        "find authentication components", 
        "what depends on UserService?",
        "get statistics",
        "show patterns in the payment system",
        "find workflows related to checkout"
    ]
    
    for query in test_cases:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")
        
        try:
            command, success, output = await session.process_query(query, dry_run=True)
            print(f"Command: {command}")
            print(f"Success: {success}")
            if not success:
                print(f"Error: {output}")
        except Exception as e:
            print(f"ERROR: {e}")
            
    print("\n✓ Test completed")


if __name__ == "__main__":
    try:
        asyncio.run(test_queries())
    except KeyboardInterrupt:
        print("\n✗ Test interrupted")
        sys.exit(1)