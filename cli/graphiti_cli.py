#!/usr/bin/env python3
"""
Graphiti CLI - Direct API access to knowledge graph operations
"""
import click
import sys
import os
from dotenv import load_dotenv

from .commands import search, episodes, maintenance
from .commands.search import search_command
from .utils.client import ClientContext

load_dotenv()

@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.option('--debug/--no-debug', default=False, help='Enable debug output')
@click.pass_context
def cli(ctx, debug):
    """
    Graphiti CLI provides direct access to knowledge graph operations.
    
    Required environment variables:
    - NEO4J_PASSWORD (required)
    - OPENAI_API_KEY (recommended)
    
    Optional environment variables:
    - NEO4J_URI (default: bolt://localhost:7687)
    - NEO4J_USER (default: neo4j)
    """
    if not os.environ.get('NEO4J_PASSWORD'):
        click.echo("Error: NEO4J_PASSWORD environment variable is required", err=True)
        sys.exit(1)
    
    if not os.environ.get('OPENAI_API_KEY'):
        click.echo("Warning: OPENAI_API_KEY not set, some operations may fail", err=True)
    
    ctx.obj = ClientContext(debug=debug)

# Register command groups
cli.add_command(search_command)  # Direct search command
cli.add_command(episodes.episode_group)
cli.add_command(maintenance.maintenance_group)

# Add query command only if optional dependency is available
try:
    from .commands import query as query_mod
    if getattr(query_mod, 'query_command', None):
        cli.add_command(query_mod.query_command)
except Exception:
    pass

if __name__ == '__main__':
    cli()
