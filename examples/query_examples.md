# Natural Language Query Examples

The `graphiti query` command lets you interact with the knowledge graph using natural language instead of memorizing CLI syntax.

## Installation

```bash
# Install with AI features
pip install -e ".[ai]"

# Install Claude Code (handles API keys internally)
npm install -g @anthropic-ai/claude-code
```

## Basic Usage

```bash
# Single query
graphiti query "show me recent changes"

# Interactive mode
graphiti query --interactive

# Dry run (see command without executing)
graphiti query "find authentication components" --dry-run
```

## Example Queries

### Temporal Searches
```bash
graphiti query "what changed today?"
graphiti query "show me updates from last week"
graphiti query "find recent authentication changes"
graphiti query "what was modified yesterday in the payment system?"
```

### Entity Type Searches
```bash
graphiti query "find all components"
graphiti query "show authentication patterns"
graphiti query "list workflows for checkout"
graphiti query "find setup procedures"
```

### Relationship Queries
```bash
graphiti query "what depends on UserService?"
graphiti query "which components implement the repository pattern?"
graphiti query "show me what belongs to the payment project"
graphiti query "find documentation for the auth module"
```

### Quality-Focused Searches
```bash
graphiti query "show me the most relevant security components"
graphiti query "find high quality authentication patterns"
graphiti query "get diverse perspectives on the architecture"
```

### Maintenance Operations
```bash
graphiti query "show statistics"
graphiti query "export the knowledge graph"
graphiti query "get detailed stats about the payment project"
```

## Interactive Mode

Start an interactive session:
```bash
graphiti query -i
```

Then have a conversation:
```
❯ show me recent changes
❯ focus on authentication components  
❯ what patterns do they implement?
❯ show dependencies
❯ exit
```

## Tips

1. **Be specific** - "authentication components" is better than just "auth"
2. **Use time words** - "recent", "yesterday", "last week" trigger temporal search
3. **Name entity types** - "components", "patterns", "workflows" for filtering
4. **Ask about relationships** - "depends on", "implements", "belongs to"
5. **Request quality** - "most relevant", "high quality" uses advanced search

## History

```bash
# View recent queries
graphiti query --history

# Clear history
graphiti query --clear-history
```

## Troubleshooting

If queries aren't being interpreted correctly:
1. Try rephrasing more explicitly
2. Use `--dry-run` to see what command would be executed
3. Ensure Claude Code is installed: `claude-code --version`
4. Use interactive mode for multi-step queries

If Claude Code isn't found:
- Install it: `npm install -g @anthropic-ai/claude-code`
- Make sure Node.js is installed
- Check that claude-code is in your PATH