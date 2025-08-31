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

from ..utils.formatters import format_output, remove_embeddings
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
@click.option('--output', '-o', type=click.Choice(['json', 'jsonc', 'jsonl', 'ndjson', 'pretty', 'csv']), default='json', help='Output format')
@click.option('--full-output', '-f', is_flag=True, help='Show all fields (default: simplified output for AI agents)')
@click.option('--min-score', type=float, help='Filter by minimum relevance score (0.0-1.0)')
@click.option('--fields', multiple=True, help='Restrict output to specified fields (repeatable)')
@click.option('--ids-only', is_flag=True, help='Output only UUIDs when available')
@click.option('--distinct-by', type=click.Choice(['fact', 'uuid']), help='De-duplicate results by field')
@click.option('--page', type=int, default=1, help='Page number (1-based)')
@click.option('--page-size', type=int, default=0, help='Results per page (0=all)')
@click.pass_obj
def search_command(ctx, query, group_ids, entity_types, edge_types, max_results, center_node,
                  created_after, created_before, order,
                  method, reranker, output, full_output, min_score, fields, ids_only, distinct_by, page, page_size):
    """Search the knowledge graph.
    
    By default, returns simplified output optimized for AI agents (name, fact, group_id only).
    Use --full-output to see all fields including UUIDs, timestamps, and attributes.
    
    The search mode is automatically selected based on options:
    - Date filters (--created-after/before) → temporal search
    - Reranking options (--reranker/method) → advanced search  
    - Otherwise → basic search
    
    Examples:
    
        # Basic search (simplified output)
        graphiti search "authentication"
        
        # Same search with full details
        graphiti search "authentication" --full-output
        
        # Temporal search (automatic when using date filters)
        graphiti search "changes" --created-after "2025-01-01" --order newest
        
        # Advanced search (automatic when using reranker)
        graphiti search "patterns" --reranker cross_encoder
        
        # Combined filters
        graphiti search "user service" --group-ids project_x --entity-types Component
    """
    if min_score is not None:
        validate_threshold(min_score, 'min-score')
    # Determine search mode based on options
    has_temporal = created_after or created_before
    has_advanced = method or reranker
    
    if has_advanced:
        advanced_search(ctx, query, group_ids, entity_types, edge_types, max_results,
                       created_after, created_before, order, method, reranker, output, full_output, center_node)
    elif has_temporal:
        temporal_search(ctx, query, group_ids, entity_types, edge_types, max_results,
                       created_after, created_before, order, output, full_output, center_node)
    else:
        basic_search(ctx, query, group_ids, entity_types, edge_types, max_results, 
                    center_node, output, full_output)

def basic_search(ctx, query, group_ids, entity_types, edge_types, max_results, center_node, output, full_output):
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
        
        # Convert results to dict for formatting, excluding embeddings
        return [remove_embeddings(edge.model_dump(mode='json')) for edge in results]
    
    try:
        results = asyncio.run(run_search())
        params = click.get_current_context().params
        ms = params.get('min_score')
        if ms is not None:
            results = [r for r in results if r.get('score') is not None and r['score'] >= ms]
        db = params.get('distinct_by')
        if db:
            seen = set()
            deduped = []
            for r in results:
                k = r.get(db)
                if k is None:
                    deduped.append(r)
                    continue
                if k in seen:
                    continue
                seen.add(k)
                deduped.append(r)
            results = deduped
        pg = int(params.get('page') or 1)
        ps = int(params.get('page_size') or 0)
        if ps and ps > 0 and pg > 0:
            start = (pg - 1) * ps
            results = results[start:start+ps]
        flds = list(params.get('fields') or [])
        ids_only = bool(params.get('ids_only'))
        click.echo(format_output(results, output, full_output=full_output, fields=flds or None, ids_only=ids_only))
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

def temporal_search(ctx, query, group_ids, entity_types, edge_types, max_results,
                   created_after, created_before, order, output, full_output, center_node):
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
            search_filter=search_filter,
            center_node_uuid=center_node
        )
        
        # Convert and optionally sort results, excluding embeddings
        result_dicts = [remove_embeddings(edge.model_dump(mode='json')) for edge in results]
        
        if order == 'newest':
            result_dicts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        elif order == 'oldest':
            result_dicts.sort(key=lambda x: x.get('created_at', ''))
        
        return result_dicts
    
    try:
        results = asyncio.run(run_temporal())
        params = click.get_current_context().params
        ms = params.get('min_score')
        if ms is not None:
            results = [r for r in results if r.get('score') is not None and r['score'] >= ms]
        db = params.get('distinct_by')
        if db:
            seen = set()
            deduped = []
            for r in results:
                k = r.get(db)
                if k is None:
                    deduped.append(r)
                    continue
                if k in seen:
                    continue
                seen.add(k)
                deduped.append(r)
            results = deduped
        pg = int(params.get('page') or 1)
        ps = int(params.get('page_size') or 0)
        if ps and ps > 0 and pg > 0:
            start = (pg - 1) * ps
            results = results[start:start+ps]
        flds = list(params.get('fields') or [])
        ids_only = bool(params.get('ids_only'))
        click.echo(format_output(results, output, full_output=full_output, fields=flds or None, ids_only=ids_only))
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

def advanced_search(ctx, query, group_ids, entity_types, edge_types, max_results,
                   created_after, created_before, order, method, reranker, output, full_output, center_node):
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
        
        if method == 'bfs' and center_node:
            basic = await client.search(
                query=query,
                group_ids=validate_group_ids(group_ids),
                num_results=max_results,
                center_node_uuid=center_node,
                search_filter=search_filter
            )
            return [remove_embeddings(edge.model_dump(mode='json')) for edge in basic]
        if reranker == 'cross_encoder':
            search_config = COMBINED_HYBRID_SEARCH_CROSS_ENCODER
        elif reranker == 'mmr':
            search_config = EDGE_HYBRID_SEARCH_MMR
        else:
            search_config = EDGE_HYBRID_SEARCH_RRF
        results = await client.search_(
            query=query,
            config=search_config,
            group_ids=validate_group_ids(group_ids),
            search_filter=search_filter,
            num_results=max_results
        )
        
        # Extract edges from SearchResults
        if hasattr(results, 'edges'):
            result_dicts = [remove_embeddings(edge.model_dump(mode='json')) for edge in results.edges]
        else:
            result_dicts = []
        
        # Apply sorting if requested
        if order == 'newest':
            result_dicts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        elif order == 'oldest':
            result_dicts.sort(key=lambda x: x.get('created_at', ''))
        
        if max_results and isinstance(max_results, int) and max_results > 0:
            result_dicts = result_dicts[:max_results]
        
        return result_dicts
    
    try:
        results = asyncio.run(run_advanced())
        params = click.get_current_context().params
        ms = params.get('min_score')
        if ms is not None:
            results = [r for r in results if r.get('score') is not None and r['score'] >= ms]
        db = params.get('distinct_by')
        if db:
            seen = set()
            deduped = []
            for r in results:
                k = r.get(db)
                if k is None:
                    deduped.append(r)
                    continue
                if k in seen:
                    continue
                seen.add(k)
                deduped.append(r)
            results = deduped
        pg = int(params.get('page') or 1)
        ps = int(params.get('page_size') or 0)
        if ps and ps > 0 and pg > 0:
            start = (pg - 1) * ps
            results = results[start:start+ps]
        flds = list(params.get('fields') or [])
        ids_only = bool(params.get('ids_only'))
        click.echo(format_output(results, output, full_output=full_output, fields=flds or None, ids_only=ids_only))
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

# Export only the main search command
__all__ = ['search_command']