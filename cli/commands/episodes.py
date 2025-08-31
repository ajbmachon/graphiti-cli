"""Episode management commands for Graphiti CLI"""
import click
import asyncio
import sys
import json
from datetime import datetime, timezone
from pathlib import Path

from graphiti_core.nodes import EpisodeType

from ..utils.formatters import format_output
from ..utils.validators import validate_group_ids, validate_date_range

@click.group(name='episodes')
def episode_group():
    """Episode management operations"""
    pass

@episode_group.command(name='add')
@click.argument('name')
@click.argument('content')
@click.option('--source', '-s', type=click.Choice(['text', 'json', 'message']), default='text', help='Content source type')
@click.option('--group-id', '-g', help='Target group ID')
@click.option('--entity-types', help='Custom entity types as JSON')
@click.option('--timestamp', type=click.DateTime(), help='Override timestamp')
@click.option('--from-file', '-f', is_flag=True, help='Read content from file')
@click.pass_obj
def add_episode(ctx, name, content, source, group_id, entity_types, timestamp, from_file):
    """
    Add an episode to the knowledge graph.
    
    Examples:
    
        graphiti episodes add "User feedback" "The auth system is working well"
        
        graphiti episodes add "Config update" config.json -f --source json
        
        graphiti episodes add "Chat log" @chat.txt --source message
    """
    # Handle file input
    if from_file or content.startswith('@'):
        if content.startswith('@'):
            file_path = content[1:]
        else:
            file_path = content
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except Exception as e:
            click.echo(f"Error reading file: {str(e)}", err=True)
            sys.exit(1)
    
    # Parse entity types if provided
    entity_types_dict = None
    if entity_types:
        try:
            entity_types_dict = json.loads(entity_types)
        except json.JSONDecodeError as e:
            click.echo(f"Error parsing entity types JSON: {str(e)}", err=True)
            sys.exit(1)
    
    async def run_add_episode():
        client = ctx.get_client()
        
        # Map source string to EpisodeType
        episode_type = EpisodeType.message if source == 'message' else EpisodeType[source]
        
        result = await client.add_episode(
            name=name,
            episode_body=content,
            source_description=source,
            reference_time=timestamp or datetime.now(timezone.utc),
            group_id=group_id,
            source=episode_type,
            entity_types=entity_types_dict
        )
        
        return {
            'episode': result.episode.model_dump(mode='json'),
            'nodes_created': len(result.nodes),
            'edges_created': len(result.edges)
        }
    
    try:
        result = asyncio.run(run_add_episode())
        click.echo(format_output(result, 'json', full_output=True))
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@episode_group.command(name='get')
@click.option('--group-id', '-g', help='Filter by group ID')
@click.option('--last-n', '-n', default=10, help='Number of recent episodes')
@click.option('--after', type=click.DateTime(), help='Episodes after date')
@click.option('--before', type=click.DateTime(), help='Episodes before date')
@click.option('--output', '-o', type=click.Choice(['json', 'jsonc', 'jsonl', 'ndjson', 'pretty']), default='json')
@click.pass_obj
def get_episodes(ctx, group_id, last_n, after, before, output):
    """
    Retrieve episodes with filtering.
    
    Examples:
    
        graphiti episodes get --last-n 20
        
        graphiti episodes get --group-id project_x --after "2024-01-01"
        
        graphiti episodes get --last-n 100 --output pretty
    """
    validate_date_range(after, before, "date range")
    
    async def run_get_episodes():
        client = ctx.get_client()
        
        # Get reference time (use before date if specified, otherwise now)
        reference_time = before or datetime.now(timezone.utc)
        
        # Retrieve episodes
        from graphiti_core.utils.maintenance.graph_data_operations import retrieve_episodes
        
        episodes = await retrieve_episodes(
            driver=client.driver,
            reference_time=reference_time,
            last_n=last_n,
            group_ids=[group_id] if group_id else None
        )
        
        # Convert to dicts with proper serialization
        episode_dicts = [ep.model_dump(mode='json') for ep in episodes]
        
        # Filter by after date if specified
        if after:
            episode_dicts = [
                ep for ep in episode_dicts 
                if ep.get('valid_at') and 
                datetime.fromisoformat(ep['valid_at'].replace('Z', '+00:00')) > after
            ]
        
        return episode_dicts
    
    try:
        results = asyncio.run(run_get_episodes())
        click.echo(format_output(results, output, full_output=True))
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@episode_group.command(name='process-bulk')
@click.argument('file', type=click.Path(exists=True))
@click.option('--group-id', '-g', help='Target group ID for all episodes')
@click.option('--batch-size', '-b', default=10, help='Processing batch size')
@click.option('--dry-run', is_flag=True, help='Validate without importing')
@click.pass_obj
def process_bulk(ctx, file, group_id, batch_size, dry_run):
    """
    Process multiple episodes from a JSON file.
    
    Expected format:
    [
      {"name": "Episode 1", "content": "...", "source": "text"},
      {"name": "Episode 2", "content": "...", "source": "json"}
    ]
    
    Examples:
    
        graphiti episodes process-bulk episodes.json --group-id project_x
        
        graphiti episodes process-bulk data.json --dry-run
    """
    try:
        with open(file, 'r') as f:
            episodes_data = json.load(f)
    except Exception as e:
        click.echo(f"Error reading file: {str(e)}", err=True)
        sys.exit(1)
    
    if not isinstance(episodes_data, list):
        click.echo("Error: File must contain a JSON array of episodes", err=True)
        sys.exit(1)
    
    async def run_process_bulk():
        if dry_run:
            click.echo(f"Dry run: Would process {len(episodes_data)} episodes")
            for i, ep in enumerate(episodes_data):
                if 'name' not in ep or 'content' not in ep:
                    click.echo(f"Warning: Episode {i} missing required fields", err=True)
            return {'status': 'dry_run', 'episodes': len(episodes_data)}
        
        client = ctx.get_client()
        results = {'processed': 0, 'failed': 0, 'errors': []}
        
        # Process in batches
        for i in range(0, len(episodes_data), batch_size):
            batch = episodes_data[i:i+batch_size]
            click.echo(f"Processing batch {i//batch_size + 1}...", err=True)
            
            for j, ep_data in enumerate(batch):
                try:
                    source_str = ep_data.get('source', 'text')
                    episode_type = EpisodeType.message if source_str == 'message' else EpisodeType[source_str]
                    
                    await client.add_episode(
                        name=ep_data['name'],
                        episode_body=ep_data['content'],
                        source_description=ep_data.get('source', 'text'),
                        reference_time=datetime.now(timezone.utc),
                        group_id=group_id or ep_data.get('group_id'),
                        source=episode_type
                    )
                    results['processed'] += 1
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append({
                        'index': i + j,
                        'name': ep_data.get('name', 'Unknown'),
                        'error': str(e)
                    })
        
        return results
    
    try:
        results = asyncio.run(run_process_bulk())
        click.echo(format_output(results, 'json', full_output=True))
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)