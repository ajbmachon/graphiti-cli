# Graphiti CLI Memory System Guide for Claude

## Critical: Your Persistent Memory System

You have access to Graphiti - a temporal knowledge graph that serves as your persistent memory across sessions. Use the CLI to access advanced features not available through MCP.

## Essential Startup Routine (EVERY Session)

```bash
# 1. Check existing project groups
graphiti query "find groups for [project-name]"

# 2. Load user preferences  
graphiti search "user preferences communication style" --group-ids user_preferences

# 3. Check debugging patterns
graphiti search "claude limitations debugging patterns" --group-ids general_debugging claude_limitations

# 4. Project-specific knowledge (if applicable)
graphiti search "[project-name]" --group-ids "codebase_[project]_*"
```

## Memory Organization

### Core Intelligence Groups (Always Available)
- `user_preferences` - User's communication style, patterns
- `prompting_best_practices` - What works for subagents
- `prompting_patterns` - Successful templates (evolving)
- `general_debugging` - Tool failures across projects
- `claude_limitations` - Your specific failure modes
- `domain_knowledge` - General tech insights

### Project Groups (Check First, Create if Missing)
- `codebase_[project]_architecture` - System design
- `codebase_[project]_components` - Modules, classes
- `codebase_[project]_flows` - Data/user flows
- `codebase_[project]_dependencies` - Relationships

## Naming Conventions (MANDATORY)

### Entity Prefixes
- `COMPONENT:[project]:[name]` - Software components
- `PATTERN:[category]:[name]` - Design patterns
- `WORKFLOW:[domain]:[name]` - Process flows
- `DEBUG:[tool]:[issue]` - Debug solutions
- `LIMIT:[claude]:[failure]` - Your limitations
- `PREF:[category]:[detail]` - User preferences
- `LEARN:[domain]:[insight]` - Learning captures

### Episode Names
- `ANALYZE:[project]:[component]` - Analysis results
- `SOLVE:[project]:[issue]` - Solutions
- `GROUP:[group_id]` - Group registry

## Critical Search Strategies

### Finding Recent Changes (Temporal Power)
```bash
# Last 24 hours
graphiti search temporal "" --created-after "$(date -d '24 hours ago' -Iseconds)" --order newest

# Specific period
graphiti search temporal "authentication" --created-after "2025-01-15" --created-before "2025-01-20"
```

### High-Quality Search
```bash
# Best relevance with cross-encoder
graphiti search advanced "design patterns" --reranker cross_encoder

# Filter by quality
graphiti search advanced "solutions" --quality-threshold 0.8
```

### Entity-Specific Search
```bash
# Components only
graphiti search "authentication" --entity-types Component

# Multiple types
graphiti search "patterns" --entity-types Pattern Workflow --group-ids project_architecture
```

### Relationship Discovery
```bash
# Find dependencies
graphiti search "UserService" --edge-types DEPENDS_ON

# Graph traversal
graphiti search advanced "" --method bfs --center-node "[uuid]" --max-depth 3
```

## Adding Knowledge

### Through Episodes (Structured Data)
```bash
# Add JSON structured knowledge
graphiti episodes add "COMPONENT:ProjectX:AuthService" '{
  "type": "Component",
  "purpose": "Handle authentication",
  "patterns": ["Singleton", "Observer"],
  "dependencies": ["DatabaseLayer", "CacheService"]
}' --source json --group-id codebase_projectx_components

# Add learning
graphiti episodes add "LEARN:Debugging:AsyncTimeout" \
  "Issue: Async operations timeout in tests. Solution: Mock timers with jest.useFakeTimers()" \
  --group-id general_debugging
```

### Capture User Corrections
```bash
graphiti episodes add "PREF:Communication:DetailLevel" \
  "user: keep responses concise
assistant: [provided long explanation]
user: I said concise - under 3 lines
learning: User strongly prefers ultra-concise responses" \
  --source message --group-id user_preferences
```

## Parallel Search Patterns

```bash
# Run multiple searches simultaneously
{
  graphiti search temporal "auth changes" --created-after "2025-01-01" &
  graphiti search "dependencies" --edge-types DEPENDS_ON &
  graphiti search "patterns" --entity-types Pattern &
  wait
} | jq -s 'add'
```

## Learning & Evolution Patterns

### Track Pattern Evolution
```bash
# Find existing pattern
graphiti search "PATTERN:Template:MultiAgent" --group-ids prompting_patterns

# Store improved version
graphiti episodes add "PATTERN:Template:MultiAgentV2" '{
  "original": "single workspace",
  "improved": "timestamped workspaces", 
  "why": "prevents collisions",
  "success_rate": "100%"
}' --source json --group-id prompting_patterns
```

### Document Failures
```bash
graphiti episodes add "LIMIT:Claude:ScreenshotAnalysis" \
  "Cannot distinguish visual visibility from DOM presence. Workaround: Ask for explicit visual confirmation" \
  --group-id claude_limitations
```

## Analytics & Maintenance

```bash
# Graph statistics
graphiti maintenance stats --detailed

# Export project knowledge
graphiti maintenance export --group-ids project_x > project_backup.json

# Find knowledge gaps
graphiti search temporal "" --created-before "$(date -d '30 days ago' -Iseconds)" --order oldest
```

## Natural Language Interface

```bash
# When syntax is complex, just ask
graphiti query "show me what changed in authentication last week"
graphiti query "find all components that implement repository pattern"
graphiti query "what debugging patterns exist for async issues?"
```

## Critical Limitations & Workarounds

### Group Filtering
- ✅ Node searches respect group_ids
- ❌ Fact searches are GLOBAL (include project name in queries)

### Temporal Queries
- Always use ISO-8601 dates: "2025-01-15" or "2025-01-15T10:00:00"
- Never use relative dates like "24 hours ago" in direct commands

### Performance
- Default 10-20 results, increase only when needed
- Use entity/edge filters to reduce search space
- Temporal constraints speed up queries dramatically

## Quick Decision Tree

**Need recent changes?** → Use temporal search  
**Need high quality?** → Use advanced with cross_encoder  
**Need relationships?** → Use edge-type filters or BFS  
**Complex query?** → Use natural language interface  
**Multiple queries?** → Run in parallel  

## Building Collective Intelligence

Every interaction builds persistent knowledge:
- **Project patterns** → Store in `codebase_*` groups
- **Tool failures** → Store in `general_debugging`
- **Your limitations** → Store in `claude_limitations`
- **User preferences** → Store in `user_preferences`
- **Prompt successes** → Store in `prompting_patterns`

Remember: You're not just completing tasks - you're building a comprehensive intelligence system that learns from every interaction. The CLI gives you temporal superpowers that MCP doesn't have. Use them.