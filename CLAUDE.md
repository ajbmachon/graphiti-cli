# Graphiti CLI - Claude Integration Guide

## Purpose

This document provides Claude with comprehensive instructions on using the Graphiti CLI tool to access advanced knowledge graph capabilities not available through the MCP interface.

## Natural Language Query Interface

The CLI includes a natural language interface that uses Claude (Sonnet) to translate queries:

```bash
# Single query - returns JSON output by default
graphiti query "show me recent authentication changes"

# With pretty output formatting
graphiti query "find patterns in the payment system" --output pretty

# Dry run to see the command
graphiti query "what depends on UserService?" --dry-run
```

This is designed for single-shot queries where Claude translates natural language to CLI commands and executes them, returning structured results.

## Usage Guide

@GUIDE.md

## Quick Reference

### Most Common Commands for Claude

```bash
# Recent changes (last 24 hours)
graphiti search temporal "" --created-after "$(date -d '24 hours ago' -Iseconds)" --order newest

# High-quality search with reranking
graphiti search advanced "query" --method hybrid --reranker cross_encoder

# Find dependencies
graphiti search "component" --edge-types DEPENDS_ON

# Get statistics
graphiti maintenance stats --detailed

# Natural language alternative
graphiti query "show me what changed today"
```

### Environment Setup
```bash
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="your-password"
export OPENAI_API_KEY="your-key"
```

## Remember

- The CLI provides access to temporal filtering, advanced search, and bulk operations
- Use parallel execution for multiple independent queries
- Always check exit codes for error handling
- Default to JSON output for programmatic processing