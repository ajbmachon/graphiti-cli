"""Natural language query interface for Graphiti CLI."""
import click
import anyio
from ..query.session import QuerySession


@click.command(name='query')
@click.argument('query', required=False)
@click.option('--interactive', '-i', is_flag=True, help='Interactive mode')
@click.option('--dry-run', '-d', is_flag=True, help='Show command without executing')
@click.option('--temperature', default=0.2, help='Claude temperature (0.0-1.0)')
@click.option('--history', is_flag=True, help='Show query history')
@click.option('--clear-history', is_flag=True, help='Clear query history')
@click.pass_context
def query_command(ctx, query, interactive, dry_run, temperature, history, clear_history):
    """Natural language interface to Graphiti.
    
    Examples:
        graphiti query "find all authentication components"
        graphiti query "show me recent changes"
        graphiti query --interactive
    """
    session = QuerySession(temperature=temperature)
    
    if clear_history:
        session.clear_history()
        click.echo("✓ Query history cleared.")
        return
        
    if history:
        click.echo(session.show_history())
        return
    
    if interactive or not query:
        anyio.run(run_interactive, session, dry_run)
    else:
        anyio.run(run_single_query, session, query, dry_run)


async def run_single_query(session: QuerySession, query: str, dry_run: bool):
    """Execute a single query."""
    click.echo(f"🔍 Processing: {query}")
    
    command, success, output = await session.process_query(query, dry_run)
    
    click.echo(f"\n📋 Command: {command}")
    
    if success:
        click.echo(f"\n✓ Output:\n{output}")
    else:
        click.echo(f"\n✗ Error: {output}", err=True)


async def run_interactive(session: QuerySession, dry_run: bool):
    """Run interactive mode."""
    click.echo("🤖 Graphiti Natural Language Interface")
    click.echo("   Type 'exit' to quit, 'help' for tips\n")
    
    while True:
        try:
            query = click.prompt("❯", type=str)
            
            if query.lower() in ['exit', 'quit']:
                click.echo("👋 Goodbye!")
                break
                
            if query.lower() == 'help':
                show_help()
                continue
            
            await run_single_query(session, query, dry_run)
            click.echo()  # Add spacing between queries
            
        except (EOFError, KeyboardInterrupt):
            click.echo("\n👋 Goodbye!")
            break
        except Exception as e:
            click.echo(f"✗ Error: {e}", err=True)


def show_help():
    """Show query tips."""
    help_text = """
📚 Query Tips:

• "show me recent changes" - finds changes in last 24 hours
• "find authentication components" - searches for specific entity types  
• "what depends on UserService?" - explores relationships
• "get statistics" - shows graph statistics
• "show high quality results for security" - uses advanced search

💡 Include time words (recent, yesterday, last week) for temporal queries
💡 Mention entity types (components, patterns, workflows) for filtering
💡 Ask about relationships (depends on, implements, belongs to)
"""
    click.echo(help_text)