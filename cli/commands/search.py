"""Search command implementations for Graphiti CLI"""
import click
import asyncio
import sys
from datetime import datetime
from typing import List, Optional, Dict, Any

from graphiti_core.search import SearchConfig
from graphiti_core.search.search_filters import SearchFilters, DateFilter
from graphiti_core.search.search_config_recipes import (
    EDGE_HYBRID_SEARCH_RRF,
    COMBINED_HYBRID_SEARCH_CROSS_ENCODER,
    NODE_BFS_SEARCH,
    NODE_HYBRID_SEARCH_RRF,
    EDGE_BFS_SEARCH
)

from ..utils.formatters import format_output
from ..utils.validators import (
    validate_date_range, validate_threshold, validate_group_ids,
    validate_entity_types, validate_edge_types
)

@click.group(name='search')
def search_group():
    """Search operations with advanced configuration"""
    pass

@search_group.command()
@click.argument('query')
@click.option('--group-ids', '-g', multiple=True, help='Filter by group IDs')
@click.option('--entity-types', '-e', multiple=True, help='Entity types to include')
@click.option('--edge-types', '-t', multiple=True, help='Edge types to filter')
@click.option('--max-results', '-n', default=10, help='Maximum results')
@click.option('--center-node', help='UUID for centered search')
@click.option('--output', '-o', type=click.Choice(['json', 'pretty', 'csv']), default='json')
@click.pass_obj
def search(ctx, query, group_ids, entity_types, edge_types, max_results, center_node, output):
    """
    Basic search with filtering options.
    
    Examples:
    
        graphiti search "authentication"
        
        graphiti search "payment" -g project_x -e Component -n 20
        
        graphiti search "dependencies" -t DEPENDS_ON
    """
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
        return [edge.model_dump() for edge in results]
    
    try:
        results = asyncio.run(run_search())
        click.echo(format_output(results, output))
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@search_group.command(name='temporal')
@click.argument('query')
@click.option('--valid-after', type=click.DateTime(), help='Facts valid after date')
@click.option('--valid-before', type=click.DateTime(), help='Facts valid before date')
@click.option('--created-after', type=click.DateTime(), help='Facts created after date')
@click.option('--created-before', type=click.DateTime(), help='Facts created before date')
@click.option('--include-invalid', is_flag=True, help='Include invalidated facts')
@click.option('--order', type=click.Choice(['newest', 'oldest', 'relevance']), default='relevance')
@click.option('--group-ids', '-g', multiple=True, help='Filter by group IDs')
@click.option('--entity-types', '-e', multiple=True, help='Entity types to include')
@click.option('--edge-types', '-t', multiple=True, help='Edge types to filter')
@click.option('--max-results', '-n', default=10, help='Maximum results')
@click.option('--output', '-o', type=click.Choice(['json', 'pretty']), default='json')
@click.pass_obj
def temporal_search(ctx, query, valid_after, valid_before, created_after, 
                   created_before, include_invalid, order, group_ids, 
                   entity_types, edge_types, max_results, output):
    """
    Search with temporal filtering capabilities.
    
    Examples:
    
        graphiti search temporal "recent changes" --created-after "2024-01-01"
        
        graphiti search temporal "authentication" --valid-after "2024-01-01" --order newest
        
        graphiti search temporal "config" --created-after "2024-01-01T10:00:00"
    """
    validate_date_range(valid_after, valid_before, "valid")
    validate_date_range(created_after, created_before, "created")
    
    async def run_temporal_search():
        client = ctx.get_client()
        
        # Build temporal filters
        valid_at_filters = None
        created_at_filters = None
        
        if valid_after or valid_before:
            valid_filters = []
            if valid_after:
                valid_filters.append(DateFilter(greater_than_equal=valid_after))
            if valid_before:
                valid_filters.append(DateFilter(less_than_equal=valid_before))
            valid_at_filters = [valid_filters]
        
        if created_after or created_before:
            created_filters = []
            if created_after:
                created_filters.append(DateFilter(greater_than_equal=created_after))
            if created_before:
                created_filters.append(DateFilter(less_than_equal=created_before))
            created_at_filters = [created_filters]
        
        # Build combined search filter
        search_filter = SearchFilters(
            valid_at=valid_at_filters,
            created_at=created_at_filters,
            entity_types=validate_entity_types(entity_types),
            edge_types=validate_edge_types(edge_types)
        )
        
        # Note: We'd need custom search config for temporal ordering
        # For now, use default search
        results = await client.search(
            query=query,
            group_ids=validate_group_ids(group_ids),
            num_results=max_results,
            search_filter=search_filter
        )
        
        # Convert and optionally sort results
        result_dicts = [edge.model_dump() for edge in results]
        
        if order == 'newest':
            result_dicts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        elif order == 'oldest':
            result_dicts.sort(key=lambda x: x.get('created_at', ''))
        
        return result_dicts
    
    try:
        results = asyncio.run(run_temporal_search())
        click.echo(format_output(results, output))
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@search_group.command(name='advanced')
@click.argument('query')
@click.option('--method', '-m', type=click.Choice(['bm25', 'semantic', 'hybrid', 'bfs']), default='hybrid')
@click.option('--reranker', '-r', type=click.Choice(['none', 'cross_encoder', 'mmr', 'episode_mentions']))
@click.option('--quality-threshold', '-q', type=float, default=0.0, help='Minimum score threshold')
@click.option('--diversity', '-d', type=float, default=0.5, help='MMR diversity lambda (0-1)')
@click.option('--max-depth', type=int, default=2, help='BFS traversal depth')
@click.option('--group-ids', '-g', multiple=True, help='Filter by group IDs')
@click.option('--entity-types', '-e', multiple=True, help='Entity types to include')
@click.option('--edge-types', '-t', multiple=True, help='Edge types to filter')
@click.option('--max-results', '-n', default=10, help='Maximum results')
@click.option('--output', '-o', type=click.Choice(['json', 'pretty']), default='json')
@click.pass_obj
def advanced_search(ctx, query, method, reranker, quality_threshold, diversity, 
                   max_depth, group_ids, entity_types, edge_types, max_results, output):
    """
    Advanced search with full configuration control.
    
    Examples:
    
        graphiti search advanced "patterns" --method hybrid --reranker cross_encoder
        
        graphiti search advanced "dependencies" --method bfs --max-depth 3
        
        graphiti search advanced "solutions" --reranker mmr --diversity 0.7
    """
    validate_threshold(quality_threshold, "quality-threshold")
    validate_threshold(diversity, "diversity")
    
    async def run_advanced_search():
        client = ctx.get_client()
        
        # Build search filter
        search_filter = None
        if entity_types or edge_types:
            search_filter = SearchFilters(
                entity_types=validate_entity_types(entity_types),
                edge_types=validate_edge_types(edge_types)
            )
        
        # Select appropriate search config based on method and reranker
        if method == 'bfs':
            search_config = NODE_BFS_SEARCH if not query else EDGE_BFS_SEARCH
            # TODO: Configure max_depth in search config
        elif reranker == 'cross_encoder':
            search_config = COMBINED_HYBRID_SEARCH_CROSS_ENCODER
        elif reranker == 'mmr':
            # TODO: Create MMR config with diversity parameter
            search_config = EDGE_HYBRID_SEARCH_RRF
        else:
            search_config = EDGE_HYBRID_SEARCH_RRF
        
        results = await client.search(
            query=query,
            group_ids=validate_group_ids(group_ids),
            num_results=max_results,
            search_filter=search_filter,
            search_config=search_config
        )
        
        # Filter by quality threshold if specified
        result_dicts = []
        for edge in results:
            edge_dict = edge.model_dump()
            # Note: Score might not always be available
            if quality_threshold > 0 and 'score' in edge_dict:
                if edge_dict['score'] >= quality_threshold:
                    result_dicts.append(edge_dict)
            else:
                result_dicts.append(edge_dict)
        
        return result_dicts
    
    try:
        results = asyncio.run(run_advanced_search())
        click.echo(format_output(results, output))
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)