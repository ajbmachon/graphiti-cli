"""Command modules for Graphiti CLI

We intentionally avoid importing the optional `query` command eagerly,
so users without the AI extra can still use search/episodes/maintenance.
"""
from . import search, episodes, maintenance

try:
    from . import query as query
except Exception:
    query = None  # Optional

__all__ = ['search', 'episodes', 'maintenance', 'query']
