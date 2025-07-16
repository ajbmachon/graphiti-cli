# Graphiti CLI

A command-line interface that provides direct access to Graphiti's full API capabilities, including temporal filtering, advanced search configuration, and bulk operations.

## Features

- 🤖 **Natural Language Interface** - Query using plain English powered by Claude
- 🕒 **Temporal Queries** - Search by creation date, validity periods
- 🔍 **Advanced Search** - Configure search methods, reranking, quality thresholds  
- 📊 **Graph Analytics** - Statistics, community detection, structure analysis
- 📦 **Bulk Operations** - Import/export episodes, batch processing
- ⚡ **Parallel Execution** - Run multiple searches simultaneously

## Installation

```bash
# Clone or move this folder to your desired location
cd /path/to/graphiti-cli

# Install with pip (creates 'graphiti' command)
pip install -e .

# For natural language query support
pip install -e ".[ai]"
# Then install Claude Code: npm install -g @anthropic-ai/claude-code
```

## Configuration

Set environment variables:
```bash
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="your-password"
export OPENAI_API_KEY="your-api-key"
```

## Quick Start

```bash
# Natural language queries (requires Claude Code)
graphiti query "show me recent authentication changes"
graphiti query "what depends on the payment service?"

# Direct CLI commands
graphiti search "authentication"
graphiti search temporal "updates" --created-after "2024-01-01"
graphiti search advanced "patterns" --method hybrid --reranker cross_encoder

# Graph operations
graphiti maintenance stats --detailed
graphiti maintenance export --group-ids project_x > backup.json
```

## Documentation

- [GUIDE.md](GUIDE.md) - Comprehensive usage guide
- [CLAUDE.md](CLAUDE.md) - AI agent integration guide

## Commands Overview

### Search Commands
- `graphiti search` - Basic search with filters
- `graphiti search temporal` - Time-based queries
- `graphiti search advanced` - Full configuration control

### Episode Management
- `graphiti episodes add` - Add new episodes
- `graphiti episodes get` - Retrieve episodes
- `graphiti episodes process-bulk` - Bulk import

### Maintenance
- `graphiti maintenance stats` - Graph statistics
- `graphiti maintenance export` - Export data
- `graphiti maintenance build-communities` - Community detection
- `graphiti maintenance clear` - Clear data (use with caution)

## Development

This CLI is built with:
- Python 3.10+
- Click for command-line interface
- graphiti-core for knowledge graph operations

## License

Same as graphiti-core project.