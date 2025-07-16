"""Output formatting utilities for Graphiti CLI"""
import json
import csv
import io
from typing import Any, List, Dict, Union
from datetime import datetime

def format_output(data: Any, format: str = 'json') -> str:
    """Format output based on requested format"""
    if format == 'json':
        return format_json(data)
    elif format == 'pretty':
        return format_pretty(data)
    elif format == 'csv':
        return format_csv(data)
    else:
        raise ValueError(f"Unknown format: {format}")

def format_json(data: Any) -> str:
    """Format as JSON with datetime handling"""
    def json_serial(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
    
    return json.dumps(data, indent=2, default=json_serial)

def format_pretty(data: Any) -> str:
    """Human-readable format for terminal display"""
    if isinstance(data, list):
        if not data:
            return "No results found."
        
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
        if key == 'embedding':  # Skip large embeddings
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
                if key == 'embedding':  # Skip embeddings
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