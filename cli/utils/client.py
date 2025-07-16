"""Client management utilities for Graphiti CLI"""
import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
from graphiti_core import Graphiti

@dataclass
class ClientContext:
    """Context object for CLI commands"""
    debug: bool = False
    _client: Optional[Graphiti] = None

    def get_client(self) -> Graphiti:
        """Get or create a Graphiti client instance using environment variables"""
        if self._client is None:
            uri = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
            user = os.environ.get('NEO4J_USER', 'neo4j')
            password = os.environ.get('NEO4J_PASSWORD')
            
            if not password:
                raise ValueError("NEO4J_PASSWORD environment variable is required")
                
            self._client = Graphiti(
                uri=uri,
                user=user,
                password=password
            )
        return self._client

    async def close(self):
        """Close the client connection"""
        if self._client:
            await self._client.close()
            self._client = None