"""Query session management."""
from typing import List, Optional
from pathlib import Path
import json
from datetime import datetime
from claude_code_sdk import Message, UserMessage, AssistantMessage

from .interpreter import QueryInterpreter
from .executor import CommandExecutor


class QuerySession:
    """Manages a query session with conversation history."""
    
    def __init__(self, temperature: float = 0.2):
        """Initialize session."""
        self.interpreter = QueryInterpreter(temperature)
        self.executor = CommandExecutor()
        self.messages: List[Message] = []
        self.history_file = Path.home() / '.graphiti' / 'query_history.json'
        
    async def process_query(self, query: str, dry_run: bool = False) -> tuple[str, bool, str]:
        """
        Process a natural language query.
        
        Returns:
            Tuple of (command, success, output)
        """
        # Add query to conversation
        self.messages.append(UserMessage(content=query))
        
        # Get CLI command from interpreter
        command = await self.interpreter.interpret_query(query, self.messages[:-1])
        
        # Add command to conversation
        self.messages.append(AssistantMessage(content=command))
        
        # Execute command
        success, output = await self.executor.execute(command, dry_run)
        
        # Save to history
        self._save_to_history(query, command, success)
        
        return command, success, output
    
    def _save_to_history(self, query: str, command: str, success: bool):
        """Save query to history file."""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        
        history = []
        if self.history_file.exists():
            try:
                history = json.loads(self.history_file.read_text())
            except:
                pass
        
        history.append({
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'command': command,
            'success': success
        })
        
        # Keep last 500 entries
        history = history[-500:]
        
        self.history_file.write_text(json.dumps(history, indent=2))
    
    def show_history(self):
        """Display recent query history."""
        if not self.history_file.exists():
            return "No query history found."
        
        try:
            history = json.loads(self.history_file.read_text())
            if not history:
                return "No query history found."
            
            output = []
            for entry in history[-10:]:  # Last 10 entries
                timestamp = datetime.fromisoformat(entry['timestamp'])
                output.append(f"{timestamp.strftime('%Y-%m-%d %H:%M')} - {entry['query']}")
                output.append(f"  → {entry['command']}")
                if not entry.get('success', True):
                    output.append("  ✗ Failed")
                output.append("")
            
            return "\n".join(output)
        except:
            return "Error reading query history."
    
    def clear_history(self):
        """Clear query history."""
        if self.history_file.exists():
            self.history_file.unlink()