"""Client management utilities for Graphiti CLI"""
import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
from graphiti_core import Graphiti

@dataclass
class ClientContext:
    """Context object for CLI commands"""
    uri: str
    user: str
    password: str
    debug: bool = False
    _client: Optional[Graphiti] = None

    def get_client(self) -> Graphiti:
        """Get or create a Graphiti client instance"""
        if self._client is None:
            self._client = Graphiti(
                neo4j_uri=self.uri,
                neo4j_user=self.user,
                neo4j_password=self.password
            )
        return self._client

    async def close(self):
        """Close the client connection"""
        if self._client:
            await self._client.close()
            self._client = None