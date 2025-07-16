"""Command executor for interpreted queries."""
import subprocess
import shlex
from typing import Tuple


class CommandExecutor:
    """Executes CLI commands from the interpreter."""
    
    # Commands that are safe to execute
    SAFE_COMMANDS = {
        'graphiti search',
        'graphiti search temporal', 
        'graphiti search advanced',
        'graphiti episodes get',
        'graphiti maintenance stats',
        'graphiti maintenance export',
        'graphiti maintenance build-communities'
    }
    
    async def execute(self, command: str, dry_run: bool = False) -> Tuple[bool, str]:
        """
        Execute a CLI command.
        
        Returns:
            Tuple of (success: bool, output: str)
        """
        # Basic safety check
        if not self._is_safe_command(command):
            return False, f"Command not allowed: {command}"
        
        if dry_run:
            return True, f"[DRY RUN] Would execute: {command}"
        
        try:
            # Execute the command
            result = subprocess.run(
                shlex.split(command),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr or f"Command failed with exit code {result.returncode}"
                
        except subprocess.TimeoutExpired:
            return False, "Command timed out after 30 seconds"
        except Exception as e:
            return False, f"Error executing command: {str(e)}"
    
    def _is_safe_command(self, command: str) -> bool:
        """Check if command is safe to execute."""
        return any(command.startswith(safe_cmd) for safe_cmd in self.SAFE_COMMANDS)