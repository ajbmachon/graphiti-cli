#!/usr/bin/env python3
"""
Graphiti CLI - Direct API access to knowledge graph operations
"""
import click
import sys
import os
from dotenv import load_dotenv

from .commands import search, episodes, maintenance, query
from .utils.client import ClientContext

load_dotenv()

@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.option('--neo4j-uri', envvar='NEO4J_URI', default='bolt://localhost:7687', help='Neo4j connection URI')
@click.option('--neo4j-user', envvar='NEO4J_USER', default='neo4j', help='Neo4j username')
@click.option('--neo4j-password', envvar='NEO4J_PASSWORD', help='Neo4j password (required)')
@click.option('--debug/--no-debug', default=False, help='Enable debug output')
@click.pass_context
def cli(ctx, neo4j_uri, neo4j_user, neo4j_password, debug):
    """
    Graphiti CLI provides direct access to knowledge graph operations.
    
    Set NEO4J_PASSWORD and OPENAI_API_KEY environment variables before use.
    """
    if not neo4j_password:
        click.echo("Error: NEO4J_PASSWORD environment variable or --neo4j-password required", err=True)
        sys.exit(1)
    
    if not os.environ.get('OPENAI_API_KEY'):
        click.echo("Warning: OPENAI_API_KEY not set, some operations may fail", err=True)
    
    ctx.obj = ClientContext(
        uri=neo4j_uri,
        user=neo4j_user,
        password=neo4j_password,
        debug=debug
    )

# Register command groups
cli.add_command(search.search_group)
cli.add_command(episodes.episode_group)
cli.add_command(maintenance.maintenance_group)
cli.add_command(query.query_command)

if __name__ == '__main__':
    cli()