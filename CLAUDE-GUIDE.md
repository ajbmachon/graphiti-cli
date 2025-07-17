# Graphiti CLI Memory System Guide for Claude

## Critical: Your Persistent Memory System

You have access to Graphiti - a temporal knowledge graph with 13 custom entity types and 14 edge types. The CLI provides advanced temporal and filtering capabilities not available through MCP. Your goal is to build up knowledge and intelligence by leveraging the power of Graphiti fully. Put high value memories in there and query specifically for them to protect your context and get high quality results that match the situation.

## 13 Custom Entity Types

| Entity Type | Prefix | Purpose | When to Use |
|-------------|--------|---------|-------------|
| **Requirement** | `requ_` | System/business requirements | User stories, functional requirements, constraints |
| **Preference** | `pref_` | User preferences and settings | User choices, configuration preferences, communication style |
| **Procedure** | `proc_` | Step-by-step processes | Installation guides, workflows, how-to instructions |
| **Project** | `proj_` | Project-level entities | Project metadata, project documentation |
| **Component** | `comp_` | Software components/modules | Classes, services, modules, libraries |
| **Pattern** | `patt_` | Design/architectural patterns | Design patterns, best practices, reusable solutions |
| **Insight** | `insi_` | Analysis findings/discoveries | Research findings, analysis results, key learnings |
| **Workflow** | `work_` | Process flows and workflows | Business processes, user journeys, data flows |
| **Agent** | `agen_` | AI agents and their roles | Subagent definitions, agent capabilities, coordination |
| **ValidationPoint** | `vali_` | Validation checkpoints | Test points, validation rules, quality checks |
| **LimitationPattern** | `limi_` | Known limitations/constraints | Claude limitations, tool constraints, known issues |
| **PromptTemplate** | `prom_` | Reusable prompt patterns | Successful prompts, prompt strategies, templates |
| **DomainConcept** | `doma_` | Domain-specific concepts | Business concepts, technical knowledge, domain expertise |

## 14 Custom Edge Types

| Edge Type | CLI Format | Purpose |
|-----------|------------|---------|
| **BelongsToProject** | `BELONGS_TO_PROJECT` | Component/entity belongs to a project |
| **DependsOn** | `DEPENDS_ON` | Technical dependencies between components |
| **ImplementsPattern** | `ImplementsPattern` | Component implements a design pattern |
| **LeadsToInsight** | `LEADS_TO_INSIGHT` | Analysis/discovery leading to insights |
| **Validates** | `VALIDATES` | Validation relationships |
| **TriggersLimitation** | `TRIGGERS_LIMITATION` | Conditions triggering limitations |
| **CoordinatesWith** | `COORDINATES_WITH` | Agent coordination relationships |
| **AnalyzesComponent** | `ANALYZES_COMPONENT` | Agent analyzes specific component |
| **EvolvesFrom** | `EVOLVES_FROM` | Evolution/improvement relationships |
| **AppliesTo** | `APPLIES_TO` | Knowledge application relationships |
| **FollowsWorkflow** | `FOLLOWS_WORKFLOW` | Entity follows specific workflow |
| **PrecedesInWorkflow** | `PRECEDES_IN_WORKFLOW` | Workflow ordering relationships |
| **Documents** | `DOCUMENTS` | Documentation relationships |
| **References** | `REFERENCES` | General reference relationships |

## Essential Startup Routine

```bash
# 1. Check user preferences (use entity type filter)
graphiti search "preferences" --entity-types Preference

# 2. Load prompting patterns and templates
graphiti search "prompting" --entity-types PromptTemplate --entity-types Pattern

# 3. Check known limitations
graphiti search "claude limitations" --entity-types LimitationPattern

# 4. For projects, check components and dependencies
graphiti search "[project-name]" --entity-types Component --entity-types Project
```

## Critical Search Strategies

### Entity Type Filtering
```bash
# Search for specific entity types
graphiti search "authentication" --entity-types Component

# Multiple entity types
graphiti search "setup guide" --entity-types Procedure --entity-types Workflow

# Find all patterns
graphiti search "" --entity-types Pattern --max-results 50
```

### Edge Type Filtering
```bash
# Find dependencies
graphiti search "PaymentService" --edge-types DEPENDS_ON

# Multiple edge types
graphiti search "checkout" --edge-types FOLLOWS_WORKFLOW --edge-types PRECEDES_IN_WORKFLOW

# What implements a pattern
graphiti search "Repository" --edge-types ImplementsPattern
```

### Finding Recent Changes (Temporal Power)
```bash
# Last 24 hours with entity filtering
graphiti search "" --created-after "$(date -d '24 hours ago' -Iseconds)" --entity-types Component --order newest

# Recent insights
graphiti search "" --created-after "2025-01-15" --entity-types Insight --order newest
```

### High-Quality Search
```bash
# Best relevance with entity filtering
graphiti search "authentication patterns" --entity-types Pattern --reranker cross_encoder

# Combine temporal, entity, and advanced search
graphiti search "security" --created-after "2025-01-01" --entity-types Component --reranker cross_encoder
```

## Adding Knowledge with Custom Types

### IMPORTANT: Processing Time Considerations

**Text format (2-3 seconds)**: Best for most use cases
**Simple JSON (5-8 seconds)**: For structured data with flat structure
**Complex JSON (15-20+ seconds)**: For deeply nested data - appears to hang but is processing
**Bulk processing**: Best for multiple complex episodes

### Text Format (Fastest - Recommended)
```bash
# Add component with description (2-3 seconds)
graphiti episodes add "COMPONENT:GraphitiCLI:SearchCommand" \
  "Unified search command at /cli/commands/search.py:24-225. Implements Command Pattern, depends on graphiti_core and click." \
  --source text --group-id default

# Add pattern efficiently
graphiti episodes add "PATTERN:CLI:UnifiedSearch" \
  "Auto-detect search mode based on options at /cli/commands/search.py. Benefits: simpler API, backward compatible." \
  --source text --group-id default

# Add limitation
graphiti episodes add "LIMITATIONPATTERN:Claude:VisualAnalysis" \
  "Claude cannot distinguish visual visibility from DOM presence in screenshots. Workaround: Ask for explicit visual confirmation." \
  --source text --group-id default
```

### Simple JSON Format (5-8 seconds)
```bash
# Keep JSON flat and simple
graphiti episodes add "COMPONENT:Payment:StripeService" '{
  "type": "Component",
  "comp_file_path": "/services/payment/stripe.py:15-200",
  "purpose": "Handle Stripe payments",
  "patterns": ["Adapter"],
  "dependencies": ["stripe-python", "PaymentInterface"]
}' --source json --group-id default
```

### Complex JSON Format (15-20+ seconds - Use When Needed)
```bash
# Complex nested structures take time but work fine
graphiti episodes add "PROJECT:ECommerce:Architecture" '{
  "type": "Project",
  "components": [
    {
      "name": "PaymentService",
      "dependencies": ["StripeAPI", "PayPalAPI"],
      "patterns": ["Strategy", "Factory"],
      "workflows": ["checkout", "refund"]
    },
    {
      "name": "InventoryService",
      "dependencies": ["Database", "Cache"],
      "validations": ["stock_check", "reorder_point"]
    }
  ],
  "workflows": {
    "checkout": {
      "steps": ["validate_cart", "check_inventory", "process_payment"],
      "error_handlers": ["payment_failed", "insufficient_stock"]
    }
  }
}' --source json --group-id default

# Note: This will process for 15-20 seconds - not hanging, just analyzing all relationships
```

### Bulk Processing for Multiple Episodes
```bash
# For many complex episodes, save to file
cat > episodes.json << 'EOF'
[
  {"name": "COMPONENT:Auth:Service", "content": "...", "source": "text"},
  {"name": "PATTERN:Security:OAuth", "content": "{...}", "source": "json"}
]
EOF

# Process in bulk (more efficient)
graphiti episodes process-bulk episodes.json --group-id default
```

### Components with File Paths
```bash
# Add component with file location
graphiti episodes add "COMPONENT:GraphitiCLI:SearchCommand" '{
  "type": "Component",
  "comp_file_path": "/cli/commands/search.py:24-225",
  "purpose": "Unified search command implementation",
  "patterns": ["Command Pattern"],
  "dependencies": ["graphiti_core", "click"]
}' --source json --group-id default

# Add pattern with implementation
graphiti episodes add "PATTERN:CLI:UnifiedSearch" '{
  "type": "Pattern",
  "patt_file_path": "/cli/commands/search.py",
  "description": "Auto-detect search mode based on options",
  "benefits": ["simpler API", "backward compatible"]
}' --source json --group-id default
```

### Procedures and Workflows
```bash
# Add procedure
graphiti episodes add "PROCEDURE:Setup:InstallGraphitiCLI" \
  "Install Graphiti CLI: 1) cd graphiti-cli 2) uv sync 3) pip install -e ." \
  --source text --group-id default

# Add workflow with steps
graphiti episodes add "WORKFLOW:Analysis:CodebaseDocumentation" '{
  "type": "Workflow",
  "steps": ["analyze structure", "identify patterns", "document components"],
  "work_file_path": "/workflows/documentation.py:15-120"
}' --source json --group-id default
```

### Capturing Limitations and Insights
```bash
# Document a limitation
graphiti episodes add "LIMITATIONPATTERN:Claude:VisualAnalysis" \
  "Claude cannot distinguish visual visibility from DOM presence in screenshots. Workaround: Ask for explicit visual confirmation." \
  --source text --group-id default

# Capture an insight
graphiti episodes add "INSIGHT:Performance:ParallelSearch" \
  "Running multiple graphiti searches in parallel with & achieves 5-10x speedup for analysis tasks" \
  --source text --group-id default
```

## Parallel Search Patterns

```bash
# Search different entity types in parallel
{
  graphiti search "auth" --entity-types Component &
  graphiti search "auth" --entity-types Pattern &
  graphiti search "auth" --entity-types Workflow &
  wait
} | jq -s 'add'

# Analyze relationships
{
  graphiti search "PaymentService" --edge-types DEPENDS_ON &
  graphiti search "PaymentService" --edge-types ImplementsPattern &
  graphiti search "PaymentService" --edge-types BELONGS_TO_PROJECT &
  wait
} | jq -s 'add'
```

## Natural Language Interface

```bash
# The query command understands entity and edge types
graphiti query "show me all authentication components"
graphiti query "what patterns does the payment service implement?"
graphiti query "find procedures for database setup"
graphiti query "what are the known claude limitations?"
```

## File Path Integration

When storing Components, Patterns, Procedures, or Workflows, include file paths:
- Format: `/path/to/file.py:start_line-end_line`
- Example: `/services/auth/auth_service.py:45-120`
- Benefits: Direct code navigation, context preservation

## Critical Limitations & Workarounds

### Entity Type Names
- Must use exact names: `Component` not `component` or `Components`
- Available via: `graphiti search --help`

### Edge Type Formats
- Most use UPPER_CASE: `DEPENDS_ON`, `BELONGS_TO_PROJECT`
- Exception: `ImplementsPattern` uses camelCase
- Check exact format when filtering

### Group Filtering
- ✅ Node searches respect group_ids
- ❌ Fact searches are GLOBAL (include context in queries)

### Temporal Queries
- Always use ISO-8601: "2025-01-15" or "2025-01-15T10:00:00"
- Never use relative dates in direct commands

## Quick Decision Tree

**What type of entity?**
- Software module → Component
- Design approach → Pattern  
- Step-by-step guide → Procedure
- Process flow → Workflow
- Analysis finding → Insight
- Known issue → LimitationPattern
- User setting → Preference

**What edge type?**
- Technical dependency → DEPENDS_ON
- Pattern usage → ImplementsPattern
- Project membership → BELONGS_TO_PROJECT
- Sequential steps → PRECEDES_IN_WORKFLOW

**Need recent changes?** → Add `--created-after`
**Need high quality?** → Add `--reranker cross_encoder`
**Need relationships?** → Use `--edge-types`
**Complex query?** → Use natural language interface

## Building Intelligence with Custom Types

Every interaction builds typed knowledge:
- **Components** → Software architecture understanding
- **Patterns** → Reusable design solutions
- **LimitationPatterns** → Claude's specific failures
- **Preferences** → User's specific needs
- **PromptTemplates** → Successful interaction patterns
- **Insights** → Cross-project learnings

The 13 entity types and 14 edge types provide semantic structure that makes knowledge retrieval precise and relationships meaningful. Use them to build a comprehensive, queryable intelligence system.