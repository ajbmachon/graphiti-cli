"""Maintenance and bulk operation commands for Graphiti CLI"""
import click
import asyncio
import sys
import json
from datetime import datetime

from ..utils.formatters import format_output, remove_embeddings
from ..utils.validators import validate_group_ids

@click.group(name='maintenance')
def maintenance_group():
    """Graph maintenance and bulk operations"""
    pass

@maintenance_group.command(name='build-communities')
@click.option('--group-ids', '-g', multiple=True, help='Groups to process')
@click.option('--algorithm', '-a', type=click.Choice(['label_propagation']), default='label_propagation')
@click.option('--output', '-o', type=click.Choice(['json', 'jsonc', 'jsonl', 'ndjson', 'pretty']), default='json')
@click.pass_obj
def build_communities(ctx, group_ids, algorithm, output):
    """
    Build communities for knowledge organization.
    
    Examples:
    
        graphiti maintenance build-communities
        
        graphiti maintenance build-communities --group-ids project_x
    """
    async def run_build_communities():
        client = ctx.get_client()
        
        # Import community operations
        from graphiti_core.utils.maintenance.community_operations import build_communities
        
        # Build communities
        await build_communities(
            driver=client.driver,
            llm_client=client.llm_client,
            embedder=client.embedder,
            community_reranker=client.reranker,
            group_ids=validate_group_ids(group_ids)
        )
        
        # Get community count
        result = await client.driver.execute_query(
            """
            MATCH (c:Community)
            RETURN count(c) as community_count
            """
        )
        
        return {
            'status': 'success',
            'communities_created': result.records[0]['community_count'] if result.records else 0,
            'group_ids': list(group_ids) if group_ids else 'all'
        }
    
    try:
        result = asyncio.run(run_build_communities())
        click.echo(format_output(result, output))
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@maintenance_group.command(name='export')
@click.option('--group-ids', '-g', multiple=True, help='Groups to export')
@click.option('--format', '-f', type=click.Choice(['json', 'graphml']), default='json')
@click.option('--include-embeddings', is_flag=True, help='Include embedding vectors')
@click.option('--output-file', '-o', type=click.Path(), help='Output file (default: stdout)')
@click.pass_obj
def export_graph(ctx, group_ids, format, include_embeddings, output_file):
    """
    Export knowledge graph data.
    
    Examples:
    
        graphiti maintenance export > backup.json
        
        graphiti maintenance export --group-ids project_x -o project_x.json
        
        graphiti maintenance export --format graphml -o graph.graphml
    """
    async def run_export():
        client = ctx.get_client()
        groups = validate_group_ids(group_ids)
        
        # Build group filter for queries
        group_filter = ""
        if groups:
            group_filter = "WHERE n.group_id IN $group_ids"
            
        # Export nodes
        nodes_query = f"""
        MATCH (n)
        {group_filter}
        RETURN n
        """
        
        # Export edges
        edges_query = f"""
        MATCH (a)-[r]->(b)
        WHERE a.group_id IN $group_ids OR b.group_id IN $group_ids
        RETURN a.uuid as source, b.uuid as target, r
        """ if groups else """
        MATCH (a)-[r]->(b)
        RETURN a.uuid as source, b.uuid as target, r
        """
        
        params = {'group_ids': groups} if groups else {}
        
        nodes_result = await client.driver.execute_query(nodes_query, **params)
        edges_result = await client.driver.execute_query(edges_query, **params)
        
        # Process nodes
        nodes = []
        for record in nodes_result.records:
            node = dict(record['n'])
            if not include_embeddings:
                node = remove_embeddings(node)
            nodes.append(node)
        
        # Process edges
        edges = []
        for record in edges_result.records:
            edge = dict(record['r'])
            edge['source'] = record['source']
            edge['target'] = record['target']
            if not include_embeddings:
                edge = remove_embeddings(edge)
            edges.append(edge)
        
        return {
            'export_date': datetime.utcnow().isoformat(),
            'format_version': '1.0',
            'statistics': {
                'nodes': len(nodes),
                'edges': len(edges),
                'groups': list(groups) if groups else 'all'
            },
            'nodes': nodes,
            'edges': edges
        }
    
    try:
        result = asyncio.run(run_export())
        output_data = format_output(result, 'json')
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(output_data)
            click.echo(f"Exported to {output_file}", err=True)
        else:
            click.echo(output_data)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@maintenance_group.command(name='stats')
@click.option('--group-ids', '-g', multiple=True, help='Groups to analyze')
@click.option('--detailed', '-d', is_flag=True, help='Show detailed statistics')
@click.option('--output', '-o', type=click.Choice(['json', 'jsonc', 'jsonl', 'ndjson', 'pretty']), default='json')
@click.pass_obj
def graph_stats(ctx, group_ids, detailed, output):
    """
    Analyze graph structure and statistics.
    
    Examples:
    
        graphiti maintenance stats
        
        graphiti maintenance stats --group-ids project_x --detailed
    """
    async def run_stats():
        client = ctx.get_client()
        groups = validate_group_ids(group_ids)
        
        # Basic statistics
        stats = {}
        
        # Node counts by type
        node_types_query = """
        MATCH (n)
        WHERE $group_ids IS NULL OR n.group_id IN $group_ids
        RETURN labels(n) as labels, count(n) as count
        """
        
        # Edge counts by type
        edge_types_query = """
        MATCH ()-[r]->()
        WHERE $group_ids IS NULL OR 
              (startNode(r).group_id IN $group_ids OR endNode(r).group_id IN $group_ids)
        RETURN type(r) as type, count(r) as count
        """
        
        # Group statistics
        groups_query = """
        MATCH (n)
        WHERE n.group_id IS NOT NULL
        RETURN DISTINCT n.group_id as group_id, count(n) as node_count
        ORDER BY node_count DESC
        """
        
        params = {'group_ids': groups}
        
        node_types = await client.driver.execute_query(node_types_query, **params)
        edge_types = await client.driver.execute_query(edge_types_query, **params)
        group_stats = await client.driver.execute_query(groups_query)
        
        # Process results
        # execute_query returns EagerResult with records attribute
        stats['node_types'] = {
            record['labels'][0]: record['count'] 
            for record in node_types.records if record['labels']
        }
        
        stats['edge_types'] = {
            record['type']: record['count'] 
            for record in edge_types.records
        }
        
        stats['groups'] = {
            record['group_id']: record['node_count'] 
            for record in group_stats.records
        }
        
        stats['totals'] = {
            'nodes': sum(stats['node_types'].values()),
            'edges': sum(stats['edge_types'].values()),
            'groups': len(stats['groups'])
        }
        
        if detailed:
            # Additional detailed statistics
            # Degree distribution
            degree_query = """
            MATCH (n)
            WHERE $group_ids IS NULL OR n.group_id IN $group_ids
            WITH n, size((n)--()) as degree
            RETURN degree, count(n) as count
            ORDER BY degree DESC
            LIMIT 20
            """
            
            degree_dist = await client.driver.execute_query(degree_query, **params)
            stats['degree_distribution'] = {
                record['degree']: record['count'] 
                for record in degree_dist.records
            }
            
            # Recent activity
            recent_query = """
            MATCH (n)
            WHERE n.created_at IS NOT NULL AND
                  ($group_ids IS NULL OR n.group_id IN $group_ids)
            RETURN date(n.created_at) as date, count(n) as count
            ORDER BY date DESC
            LIMIT 7
            """
            
            recent = await client.driver.execute_query(recent_query, params)
            stats['recent_activity'] = {
                record['date']: record['count'] 
                for record in recent
            }
        
        return stats
    
    try:
        result = asyncio.run(run_stats())
        click.echo(format_output(result, output))
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@maintenance_group.command(name='clear')
@click.option('--group-ids', '-g', multiple=True, help='Groups to clear (WARNING: destructive)')
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
@click.pass_obj
def clear_graph(ctx, group_ids, confirm):
    """
    Clear graph data (WARNING: destructive operation).
    
    Examples:
    
        graphiti maintenance clear --group-ids test_data --confirm
        
        graphiti maintenance clear --confirm  # Clears entire graph!
    """
    groups = validate_group_ids(group_ids)
    
    if not confirm:
        if groups:
            click.echo(f"This will DELETE all data in groups: {', '.join(groups)}")
        else:
            click.echo("This will DELETE THE ENTIRE GRAPH!")
        
        if not click.confirm("Are you sure you want to continue?"):
            click.echo("Aborted")
            return
    
    async def run_clear():
        client = ctx.get_client()
        
        if groups:
            # Clear specific groups
            delete_query = """
            MATCH (n)
            WHERE n.group_id IN $group_ids
            DETACH DELETE n
            """
            await client.driver.execute_query(delete_query, {'group_ids': groups})
            return {'cleared_groups': list(groups)}
        else:
            # Clear entire graph
            await client.driver.execute_query("MATCH (n) DETACH DELETE n")
            return {'status': 'entire graph cleared'}
    
    try:
        result = asyncio.run(run_clear())
        click.echo(format_output(result, 'json'))
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)