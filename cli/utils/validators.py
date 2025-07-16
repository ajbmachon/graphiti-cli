"""Input validation utilities for Graphiti CLI"""
from datetime import datetime
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
    """Convert and validate group IDs"""
    if not group_ids:
        return None
    return list(group_ids)

def validate_entity_types(entity_types: tuple) -> list:
    """Convert and validate entity types"""
    if not entity_types:
        return None
    
    # Known entity types from MCP implementation
    valid_types = {
        'Requirement', 'Preference', 'Procedure', 'Project', 
        'Component', 'Pattern', 'Insight', 'Workflow', 'Agent',
        'ValidationPoint', 'LimitationPattern', 'PromptTemplate', 
        'DomainConcept'
    }
    
    types = list(entity_types)
    invalid = [t for t in types if t not in valid_types]
    if invalid:
        raise click.ClickException(
            f"Invalid entity types: {', '.join(invalid)}. "
            f"Valid types: {', '.join(sorted(valid_types))}"
        )
    return types

def validate_edge_types(edge_types: tuple) -> list:
    """Convert and validate edge types"""
    if not edge_types:
        return None
    
    # Known edge types from MCP implementation
    valid_types = {
        'BELONGS_TO_PROJECT', 'DEPENDS_ON', 'ImplementsPattern',
        'LEADS_TO_INSIGHT', 'VALIDATES', 'TRIGGERS_LIMITATION',
        'COORDINATES_WITH', 'ANALYZES_COMPONENT', 'EVOLVES_FROM',
        'APPLIES_TO', 'FOLLOWS_WORKFLOW', 'PRECEDES_IN_WORKFLOW',
        'DOCUMENTS', 'REFERENCES'
    }
    
    types = list(edge_types)
    invalid = [t for t in types if t not in valid_types]
    if invalid:
        raise click.ClickException(
            f"Invalid edge types: {', '.join(invalid)}. "
            f"Valid types: {', '.join(sorted(valid_types))}"
        )
    return types