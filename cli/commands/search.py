"""Search command implementation for Graphiti CLI"""
import click
import asyncio
import sys
from datetime import datetime
from typing import List, Optional, Dict, Any

from graphiti_core.search import search_config
from graphiti_core.search.search_filters import SearchFilters, DateFilter, ComparisonOperator
from graphiti_core.search.search_config_recipes import (
    EDGE_HYBRID_SEARCH_RRF,
    COMBINED_HYBRID_SEARCH_CROSS_ENCODER,
    NODE_HYBRID_SEARCH_RRF,
    EDGE_HYBRID_SEARCH_CROSS_ENCODER,
    EDGE_HYBRID_SEARCH_MMR
)

from ..utils.formatters import format_output
from ..utils.validators import (
    validate_date_range, validate_threshold, validate_group_ids,
    validate_entity_types, validate_edge_types
)

@click.command(name='search')
@click.argument('query')
# Basic filters
@click.option('--group-ids', '-g', multiple=True, help='Filter by group IDs')
@click.option('--entity-types', '-e', multiple=True, help='Entity types to include')
@click.option('--edge-types', '-t', multiple=True, help='Edge types to filter')
@click.option('--max-results', '-n', default=10, help='Maximum results')
@click.option('--center-node', help='UUID for centered search')
# Temporal filters
@click.option('--created-after', type=click.DateTime(), help='Filter by creation date')
@click.option('--created-before', type=click.DateTime(), help='Filter by creation date')
@click.option('--order', type=click.Choice(['newest', 'oldest', 'relevance']), default='relevance', help='Sort order')
# Advanced options
@click.option('--method', '-m', type=click.Choice(['bm25', 'semantic', 'hybrid', 'bfs']), help='Search method (advanced)')
@click.option('--reranker', '-r', type=click.Choice(['none', 'cross_encoder', 'mmr']), help='Reranking strategy (advanced)')
# Output
@click.option('--output', '-o', type=click.Choice(['json', 'pretty', 'csv']), default='json', help='Output format')
@click.pass_obj
def search_command(ctx, query, group_ids, entity_types, edge_types, max_results, center_node,
                  created_after, created_before, order,
                  method, reranker, output):
    """Search the knowledge graph.
    
    The search mode is automatically selected based on options:
    - Date filters (--created-after/before) → temporal search
    - Reranking options (--reranker/method) → advanced search  
    - Otherwise → basic search
    
    Examples:
    
        # Basic search
        graphiti search "authentication"
        
        # Temporal search (automatic when using date filters)
        graphiti search "changes" --created-after "2025-01-01" --order newest
        
        # Advanced search (automatic when using reranker)
        graphiti search "patterns" --reranker cross_encoder
        
        # Combined filters
        graphiti search "user service" --group-ids project_x --entity-types Component
    """
    # Determine search mode based on options
    has_temporal = created_after or created_before
    has_advanced = method or reranker
    
    if has_advanced:
        # Advanced search mode (can include temporal filters)
        advanced_search(ctx, query, group_ids, entity_types, edge_types, max_results,
                       created_after, created_before, order, method, reranker, output)
    elif has_temporal:
        # Temporal search without advanced features
        temporal_search(ctx, query, group_ids, entity_types, edge_types, max_results,
                       created_after, created_before, order, output)
    else:
        # Basic search
        basic_search(ctx, query, group_ids, entity_types, edge_types, max_results, 
                    center_node, output)

def basic_search(ctx, query, group_ids, entity_types, edge_types, max_results, center_node, output):
    """Basic search with filtering options."""
    async def run_search():
        client = ctx.get_client()
        
        # Build search filter if needed
        search_filter = None
        if entity_types or edge_types:
            search_filter = SearchFilters(
                entity_types=validate_entity_types(entity_types),
                edge_types=validate_edge_types(edge_types)
            )
        
        results = await client.search(
            query=query,
            group_ids=validate_group_ids(group_ids),
            num_results=max_results,
            center_node_uuid=center_node,
            search_filter=search_filter
        )
        
        # Convert results to dict for formatting
        return [edge.model_dump(mode='json') for edge in results]
    
    try:
        results = asyncio.run(run_search())
        click.echo(format_output(results, output))
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

def temporal_search(ctx, query, group_ids, entity_types, edge_types, max_results,
                   created_after, created_before, order, output):
    """Temporal search with date filtering."""
    validate_date_range(created_after, created_before, "created")
    
    async def run_temporal():
        client = ctx.get_client()
        
        # Build temporal filters
        created_at_filters = None
        if created_after or created_before:
            created_filters = []
            if created_after:
                created_filters.append(DateFilter(date=created_after, comparison_operator=ComparisonOperator.greater_than_equal))
            if created_before:
                created_filters.append(DateFilter(date=created_before, comparison_operator=ComparisonOperator.less_than_equal))
            created_at_filters = [created_filters]
        
        # Build search filter
        search_filter = SearchFilters(
            created_at=created_at_filters,
            entity_types=validate_entity_types(entity_types),
            edge_types=validate_edge_types(edge_types)
        )
        
        results = await client.search(
            query=query,
            group_ids=validate_group_ids(group_ids),
            num_results=max_results,
            search_filter=search_filter
        )
        
        # Convert and optionally sort results
        result_dicts = [edge.model_dump(mode='json') for edge in results]
        
        if order == 'newest':
            result_dicts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        elif order == 'oldest':
            result_dicts.sort(key=lambda x: x.get('created_at', ''))
        
        return result_dicts
    
    try:
        results = asyncio.run(run_temporal())
        click.echo(format_output(results, output))
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

def advanced_search(ctx, query, group_ids, entity_types, edge_types, max_results,
                   created_after, created_before, order, method, reranker, output):
    """Advanced search with reranking and optional temporal filters."""
    validate_date_range(created_after, created_before, "created")
    
    async def run_advanced():
        client = ctx.get_client()
        
        # Build search filter with all options
        created_at_filters = None
        if created_after or created_before:
            created_filters = []
            if created_after:
                created_filters.append(DateFilter(date=created_after, comparison_operator=ComparisonOperator.greater_than_equal))
            if created_before:
                created_filters.append(DateFilter(date=created_before, comparison_operator=ComparisonOperator.less_than_equal))
            created_at_filters = [created_filters]
        
        search_filter = SearchFilters(
            created_at=created_at_filters,
            entity_types=validate_entity_types(entity_types),
            edge_types=validate_edge_types(edge_types)
        )
        
        # Select search config
        if reranker == 'cross_encoder':
            search_config = COMBINED_HYBRID_SEARCH_CROSS_ENCODER
        elif reranker == 'mmr':
            search_config = EDGE_HYBRID_SEARCH_MMR
        else:
            search_config = EDGE_HYBRID_SEARCH_RRF
        
        # Use advanced search with config
        results = await client.search_(
            query=query,
            config=search_config,
            group_ids=validate_group_ids(group_ids),
            search_filter=search_filter
        )
        
        # Extract edges from SearchResults
        if hasattr(results, 'edges'):
            result_dicts = [edge.model_dump(mode='json') for edge in results.edges]
        else:
            result_dicts = []
        
        # Apply sorting if requested
        if order == 'newest':
            result_dicts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        elif order == 'oldest':
            result_dicts.sort(key=lambda x: x.get('created_at', ''))
        
        return result_dicts
    
    try:
        results = asyncio.run(run_advanced())
        click.echo(format_output(results, output))
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

# Export only the main search command
__all__ = ['search_command']