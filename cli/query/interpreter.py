"""Natural language query interpreter using Claude SDK."""
from typing import List, Optional
from claude_code_sdk import query, ClaudeCodeOptions, Message
from .prompts import GRAPHITI_CLI_EXPERT_PROMPT_WITH_EXAMPLES


class QueryInterpreter:
    """Simple interpreter that uses Claude to translate natural language to CLI commands."""
    
    def __init__(self, temperature: float = 0.2):
        """Initialize with Sonnet model for fast responses."""
        self.temperature = temperature
        self.system_prompt = GRAPHITI_CLI_EXPERT_PROMPT_WITH_EXAMPLES
        
    async def interpret_query(self, user_query: str, context: List[Message] = None) -> str:
        """Get CLI command from natural language query."""
        prompt = self._build_prompt(user_query, context)
        
        messages = []
        async for message in query(
            prompt=prompt,
            options=ClaudeCodeOptions(
                model="claude-3-5-sonnet-20241022",  # Use Sonnet for speed
                system_prompt=self.system_prompt,
                temperature=self.temperature,
                max_turns=1,
                timeout_ms=5000  # 5 second timeout
            )
        ):
            messages.append(message)
        
        if not messages:
            # Fallback to basic search if no response
            return f'graphiti search "{user_query}"'
            
        # Return the command directly from Claude's response
        return messages[-1].content.strip()
    
    def _build_prompt(self, user_query: str, context: List[Message] = None) -> str:
        """Build prompt with query and optional context."""
        prompt = f"Natural language query: {user_query}"
        
        if context and len(context) > 0:
            # Add last command for context
            for msg in reversed(context):
                if msg.role == "assistant" and msg.content.startswith("graphiti"):
                    prompt = f"Previous command: {msg.content}\n\n{prompt}"
                    break
        
        return prompt