"""Input validation utilities for Graphiti CLI"""
from datetime import datetime, timezone
from typing import Optional
import click

def validate_date_range(start: Optional[datetime], end: Optional[datetime], range_name: str):
    """Validate that start date is before end date"""
    if start and end and start > end:
        raise click.ClickException(
            f"Invalid {range_name} date range: start date ({start.isoformat()}) "
            f"must be before end date ({end.isoformat()})"
        )

def validate_threshold(value: float, name: str = "threshold") -> float:
    """Validate threshold is between 0 and 1"""
    if not 0.0 <= value <= 1.0:
        raise click.ClickException(f"{name} must be between 0.0 and 1.0, got {value}")
    return value

def validate_group_ids(group_ids: tuple) -> list:
    if not group_ids:
        return None
    return [str(g).strip() for g in list(group_ids)]

# Accepted datetime formats for CLI parameters (includes 'Z' suffix)
DATETIME_FORMATS = (
    '%Y-%m-%d',
    '%Y-%m-%dT%H:%M:%S',
    '%Y-%m-%d %H:%M:%S',
    '%Y-%m-%dT%H:%M:%SZ',
)

def to_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """Return timezone-aware UTC datetime; treat naive values as UTC."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def validate_entity_types(entity_types: tuple) -> list:
    if not entity_types:
        return None
    valid_types = [
        'Requirement', 'Preference', 'Procedure', 'Project',
        'Component', 'Pattern', 'Insight', 'Workflow', 'Agent',
        'ValidationPoint', 'LimitationPattern', 'PromptTemplate',
        'DomainConcept'
    ]
    lookup = {t.lower(): t for t in valid_types}
    normalized = []
    invalid = []
    for t in list(entity_types):
        key = str(t).strip().lower()
        if key in lookup:
            normalized.append(lookup[key])
        else:
            invalid.append(str(t))
    if invalid:
        raise click.ClickException(
            f"Invalid entity types: {', '.join(invalid)}. "
            f"Valid types: {', '.join(valid_types)}"
        )
    return normalized

def validate_edge_types(edge_types: tuple) -> list:
    if not edge_types:
        return None
    valid_types = [
        'BELONGS_TO_PROJECT', 'DEPENDS_ON', 'ImplementsPattern',
        'LEADS_TO_INSIGHT', 'VALIDATES', 'TRIGGERS_LIMITATION',
        'COORDINATES_WITH', 'ANALYZES_COMPONENT', 'EVOLVES_FROM',
        'APPLIES_TO', 'FOLLOWS_WORKFLOW', 'PRECEDES_IN_WORKFLOW',
        'DOCUMENTS', 'REFERENCES'
    ]
    # Case-insensitive lookup, preserving canonical casing
    lookup = {t.lower(): t for t in valid_types}
    normalized = []
    invalid = []
    for t in list(edge_types):
        key = str(t).strip().lower()
        if key in lookup:
            normalized.append(lookup[key])
        else:
            invalid.append(str(t))
    if invalid:
        raise click.ClickException(
            f"Invalid edge types: {', '.join(invalid)}. "
            f"Valid types: {', '.join(valid_types)}"
        )
    return normalized
