"""Output formatting utilities for Graphiti CLI"""
import json
import csv
import io
from typing import Any, List, Dict, Union
from datetime import datetime
from enum import Enum
from neo4j.time import DateTime as Neo4jDateTime

def remove_embeddings(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove embedding fields from a dictionary.
    
    Removes all fields ending with '_embedding' from the top level
    and from the attributes dictionary.
    """
    # Create a copy to avoid modifying the original
    clean_data = data.copy()
    
    # Remove top-level embedding fields
    keys_to_remove = [k for k in clean_data.keys() if k.endswith('_embedding')]
    for key in keys_to_remove:
        clean_data.pop(key, None)
    
    # Remove embeddings from attributes if present
    if 'attributes' in clean_data and isinstance(clean_data['attributes'], dict):
        clean_attrs = clean_data['attributes'].copy()
        attr_keys_to_remove = [k for k in clean_attrs.keys() if k.endswith('_embedding')]
        for key in attr_keys_to_remove:
            clean_attrs.pop(key, None)
        clean_data['attributes'] = clean_attrs
    
    return clean_data

def simplify_edge(edge_data: Dict[str, Any]) -> Dict[str, Any]:
    """Simplify edge data to essential fields for AI agent consumption.
    
    Returns only the essential fields:
    - name: The relationship type (e.g., DEPENDS_ON)
    - fact: The actual relationship information
    - group_id: Context for the relationship
    """
    simplified = {}
    
    # Essential fields for AI agents
    if 'name' in edge_data:
        simplified['name'] = edge_data['name']
    
    if 'fact' in edge_data:
        simplified['fact'] = edge_data['fact']
    
    if 'group_id' in edge_data:
        simplified['group_id'] = edge_data['group_id']
    
    # If this is a node result (has 'summary' instead of 'fact')
    if 'summary' in edge_data and 'fact' not in edge_data:
        simplified['summary'] = edge_data['summary']
        
    # Include entity_type for nodes
    if 'entity_type' in edge_data:
        simplified['entity_type'] = edge_data['entity_type']
    
    return simplified

def format_output(data: Any, format: str = 'json', full_output: bool = False) -> str:
    """Format output based on requested format
    
    Args:
        data: The data to format
        format: Output format ('json', 'pretty', 'csv')
        full_output: If True, show all fields. If False, show simplified output for AI agents.
    """
    # Apply simplified format unless full_output is requested
    if not full_output and isinstance(data, list):
        data = [simplify_edge(item) for item in data]
    
    if format == 'json':
        return format_json(data)
    elif format == 'pretty':
        return format_pretty(data)
    elif format == 'csv':
        return format_csv(data)
    else:
        raise ValueError(f"Unknown format: {format}")

def format_json(data: Any) -> str:
    """Format as JSON with datetime and enum handling"""
    def json_serial(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Neo4jDateTime):
            return obj.iso_format()
        elif isinstance(obj, Enum):
            return obj.value
        elif hasattr(obj, 'model_dump'):
            return obj.model_dump()
        raise TypeError(f"Type {type(obj)} not serializable")
    
    return json.dumps(data, indent=2, default=json_serial)

def format_pretty(data: Any) -> str:
    """Human-readable format for terminal display"""
    if isinstance(data, list):
        if not data:
            return "No results found."
        
        # Check if this is simplified data (fewer fields)
        is_simplified = data and len(data[0]) <= 4
        
        if is_simplified:
            # Ultra-compact format for AI agents
            output = []
            for item in data:
                if 'fact' in item:
                    # Edge format: [TYPE] FACT (group)
                    line = f"[{item.get('name', 'UNKNOWN')}] {item.get('fact', '')}"
                    if 'group_id' in item:
                        line += f" ({item['group_id']})"
                elif 'summary' in item:
                    # Node format: [ENTITY_TYPE] NAME: SUMMARY (group)
                    line = f"[{item.get('entity_type', 'UNKNOWN')}] {item.get('name', '')}: {item.get('summary', '')}"
                    if 'group_id' in item:
                        line += f" ({item['group_id']})"
                else:
                    line = str(item)
                output.append(line)
            return "\n".join(output)
        else:
            # Full format with separators
            output = []
            for i, item in enumerate(data):
                output.append(f"\n{'='*50}")
                output.append(f"Result {i+1}")
                output.append('='*50)
                output.append(format_item(item))
            return "\n".join(output)
    else:
        return format_item(data)

def format_item(item: Union[Dict[str, Any], Any]) -> str:
    """Format a single item for display"""
    if not isinstance(item, dict):
        return str(item)
    
    lines = []
    for key, value in item.items():
        if key.endswith('_embedding'):  # Skip all embedding fields
            lines.append(f"{key}: <embedding vector>")
        elif isinstance(value, (list, dict)):
            if isinstance(value, list) and len(value) > 10:
                lines.append(f"{key}: [{len(value)} items]")
            else:
                value_str = json.dumps(value, indent=2, default=str)
                lines.append(f"{key}: {value_str}")
        else:
            lines.append(f"{key}: {value}")
    return "\n".join(lines)

def format_csv(data: Union[List[Dict[str, Any]], Any]) -> str:
    """Format as CSV for data export"""
    if not isinstance(data, list):
        data = [data]
    
    if not data:
        return ""
    
    # Flatten nested structures for CSV
    flattened = []
    for item in data:
        if isinstance(item, dict):
            flat_item = {}
            for key, value in item.items():
                if key.endswith('_embedding'):  # Skip all embedding fields
                    continue
                elif isinstance(value, (list, dict)):
                    flat_item[key] = json.dumps(value)
                else:
                    flat_item[key] = value
            flattened.append(flat_item)
        else:
            flattened.append({'value': str(item)})
    
    if not flattened:
        return ""
    
    output = io.StringIO()
    fieldnames = list(flattened[0].keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(flattened)
    return output.getvalue()