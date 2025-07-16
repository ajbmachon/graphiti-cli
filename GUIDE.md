# Graphiti CLI - Comprehensive Usage Guide

## Overview

The Graphiti CLI provides direct access to the knowledge graph with advanced temporal filtering, search configuration, and bulk operations that aren't available through the MCP interface. Use this tool when you need sophisticated knowledge retrieval or management capabilities.

## Natural Language Interface (NEW!)

The CLI now includes a natural language query interface powered by Claude:

```bash
# Ask questions in plain English
graphiti query "show me recent authentication changes"

# Interactive mode for conversations
graphiti query --interactive

# See what command would be executed
graphiti query "find patterns in the payment system" --dry-run
```

Install with `pip install -e ".[ai]"` and set `ANTHROPIC_API_KEY`. See [query examples](examples/query_examples.md) for more.

## When to Use Graphiti CLI vs MCP

**Use Graphiti CLI when you need:**
- 🕒 **Temporal queries** - "What changed in the last 7 days?"
- 🔍 **Advanced search** - Cross-encoder reranking, quality thresholds, BFS traversal
- 📊 **Graph analytics** - Statistics, community detection, structure analysis
- 📦 **Bulk operations** - Import/export, batch processing
- ⚡ **Parallel searches** - Run multiple queries simultaneously
- 🤖 **Natural language** - Query without memorizing syntax

**Continue using MCP for:**
- Simple searches without temporal constraints
- Adding individual memories
- Basic entity/edge type filtering

## Essential Commands

### 1. Finding Recent Information

```bash
# Changes in the last 24 hours
graphiti search temporal "" --created-after "$(date -d '24 hours ago' -Iseconds)" --order newest

# Updates this week  
graphiti search temporal "authentication" --created-after "$(date -d '7 days ago' -Iseconds)"

# Changes in a specific period
graphiti search temporal "config" --created-after "2024-01-01" --created-before "2024-02-01"
```

### 2. High-Quality Search Results

```bash
# Use cross-encoder for best relevance
graphiti search advanced "design patterns" --method hybrid --reranker cross_encoder

# Filter low-quality results
graphiti search advanced "solutions" --quality-threshold 0.8

# Get diverse perspectives with MMR
graphiti search advanced "approaches" --reranker mmr --diversity 0.7
```

### 3. Relationship Discovery

```bash
# Find dependencies up to 3 levels deep
graphiti search advanced "" --method bfs --max-depth 3 --center-node "component-uuid"

# Find all edges of specific types
graphiti search "payment service" --edge-types DEPENDS_ON --edge-types IMPLEMENTS_PATTERN
```

### 4. Entity-Specific Searches

```bash
# Search only Components and Patterns
graphiti search "authentication" --entity-types Component --entity-types Pattern

# Find all Workflows in a project
graphiti search "" --entity-types Workflow --group-ids project_architecture
```

## Parallel Execution Patterns

### Multiple Independent Searches
```bash
# Run searches in parallel and combine results
{
  graphiti search temporal "auth changes" --created-after "2024-01-01" &
  graphiti search temporal "database updates" --created-after "2024-01-01" &
  graphiti search temporal "api modifications" --created-after "2024-01-01" &
  wait
} | jq -s 'add'
```

### Progressive Search Refinement
```bash
# Start broad, then narrow
graphiti search "authentication" --max-results 50 > broad_results.json

# Analyze results, then search with more specificity
graphiti search "authentication" \
  --entity-types Component \
  --edge-types DEPENDS_ON \
  --group-ids project_core
```

## Temporal Analysis Workflows

### What Changed Recently?
```bash
# Get all recent changes in a project
graphiti search temporal "" \
  --created-after "$(date -d '1 week ago' -Iseconds)" \
  --group-ids project_x \
  --order newest
```

### Historical Analysis
```bash
# Find original design decisions
graphiti search temporal "architecture decisions" \
  --created-before "$(date -d '6 months ago' -Iseconds)" \
  --order oldest
```

### Change Tracking
```bash
# Track evolution of a component
graphiti search temporal "UserService" \
  --entity-types Component \
  --order oldest \
  --max-results 100
```

## Advanced Search Strategies

### Quality-Focused Searches
```bash
# Only high-confidence results for critical queries
graphiti search advanced "security vulnerabilities" \
  --method hybrid \
  --reranker cross_encoder \
  --quality-threshold 0.9
```

### Graph Traversal
```bash
# Explore relationships from a starting point
graphiti search advanced "" \
  --method bfs \
  --center-node "7f8a9b1c-2d3e-4f5a-6b7c-8d9e0f1a2b3c" \
  --max-depth 2
```

### Combined Filters
```bash
# Complex query with multiple constraints
graphiti search "payment processing" \
  --entity-types Component \
  --edge-types DEPENDS_ON \
  --group-ids project_ecommerce \
  --max-results 20
```

## Graph Analytics

### Understanding Structure
```bash
# Get comprehensive statistics
graphiti maintenance stats --detailed

# Analyze specific project
graphiti maintenance stats --group-ids project_x --detailed
```

### Community Detection
```bash
# Build topic clusters
graphiti maintenance build-communities --group-ids project_x

# Then search within communities
graphiti search "microservices" --output pretty
```

## Data Management

### Export for Analysis
```bash
# Export project knowledge
graphiti maintenance export --group-ids project_x > project_x_graph.json

# Export without embeddings (smaller file)
graphiti maintenance export --group-ids project_x > project_x_compact.json
```

### Bulk Episode Processing
```bash
# Import multiple episodes
cat episodes.json | graphiti episodes process-bulk - --group-id project_y

# Dry run first
graphiti episodes process-bulk episodes.json --dry-run
```

## Output Processing

### JSON Manipulation
```bash
# Extract specific fields
graphiti search "query" | jq '.[] | {name: .name, type: .type}'

# Filter by score
graphiti search "query" | jq '.[] | select(.score > 0.8)'

# Count results by type
graphiti search "query" | jq 'group_by(.type) | map({type: .[0].type, count: length})'
```

### Pretty Output for Reading
```bash
# Human-readable format
graphiti search "authentication" --output pretty

# Save pretty output
graphiti search "patterns" --output pretty > patterns_report.txt
```

## Common Use Cases

### 1. "What's new in this area?"
```bash
graphiti search temporal "authentication system" \
  --created-after "$(date -d '48 hours ago' -Iseconds)" \
  --order newest
```

### 2. "Find all dependencies"
```bash
graphiti search "PaymentService" \
  --edge-types DEPENDS_ON \
  --max-results 50
```

### 3. "Historical context"
```bash
graphiti episodes get \
  --group-id project_x \
  --last-n 100 \
  --output pretty
```

### 4. "Cross-reference patterns"
```bash
# Find components implementing specific patterns
graphiti search "" \
  --edge-types ImplementsPattern \
  --group-ids project_architecture
```

## Error Handling

### Check Exit Codes
```bash
if graphiti search "test query"; then
  echo "Search successful"
else
  case $? in
    1) echo "General error" ;;
    2) echo "Invalid parameters" ;;
    3) echo "Connection error" ;;
  esac
fi
```

### Validate Before Bulk Operations
```bash
# Always dry-run first
graphiti episodes process-bulk large_data.json --dry-run

# Check stats before clearing
graphiti maintenance stats --group-ids old_project
```

## Performance Tips

1. **Use appropriate limits** - Default to 10-20 results, increase only when needed
2. **Filter early** - Use entity/edge type filters to reduce search space
3. **Temporal constraints** - Narrow time windows for faster queries
4. **Parallel execution** - Run independent searches simultaneously
5. **Output format** - Use JSON for further processing, pretty only for reading

## Integration with Other Tools

### Combine with jq
```bash
# Complex analysis pipeline
graphiti search temporal "" --created-after "2024-01-01" |
  jq '.[] | select(.type == "Component") | .name' |
  sort | uniq -c | sort -nr
```

### Feed to other commands
```bash
# Find and analyze components
graphiti search "service" --entity-types Component |
  jq -r '.[] | .uuid' |
  xargs -I {} graphiti search advanced "" --center-node {} --method bfs
```

## Troubleshooting

### No Results?
1. Check date formats - use ISO-8601
2. Verify entity/edge type names exactly match
3. Try broader search without filters
4. Check group IDs exist

### Slow Performance?
1. Reduce max-results
2. Add temporal constraints  
3. Use specific entity/edge filters
4. Avoid deep BFS traversal

### Connection Issues?
```bash
# Verify environment
echo $NEO4J_URI
echo $NEO4J_PASSWORD | wc -c  # Should be > 0

# Test connection
graphiti search "test" --max-results 1
```

## Best Practices

1. **Always use temporal filtering** when looking for recent changes
2. **Start broad, then narrow** - Use progressive refinement
3. **Leverage parallel execution** for multiple queries
4. **Export before major changes** - Create backups
5. **Use dry-run** for bulk operations
6. **Pretty output sparingly** - JSON is more efficient
7. **Check stats regularly** - Understand graph growth

Remember: The CLI unlocks Graphiti's full power. Use it whenever MCP limitations prevent you from getting the insights you need.