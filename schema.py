"""
JSON Schema Definitions and Validation

This module defines the authoritative JSON schemas for:
1. LLM → Unreal Engine (command structure)
2. Unreal Engine → System (response structure)

It also provides validation functions to ensure schema compliance.
"""

from jsonschema import validate, ValidationError
from typing import Dict, Any, List
import json


# ============================================================================
# SCHEMA: LLM → Unreal Engine (Command)
# ============================================================================

COMMAND_SCHEMA = {
    "type": "object",
    "required": ["command_id", "actions", "dialogue_context", "requires_clarification"],
    "properties": {
        "command_id": {
            "type": "string",
            "description": "Unique identifier for this command"
        },
        "actions": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["action_id", "type", "target", "parameters", "assigned_to", "priority"],
                "properties": {
                    "action_id": {
                        "type": "string",
                        "description": "Unique identifier for this action"
                    },
                    "type": {
                        "type": "string",
                        "enum": ["follow", "stop_follow", "wait", "attack", "defend", "assist", "unknown"],
                        "description": "Action type - closed vocabulary of supported commands"
                    },
                    "target": {
                        "type": "object",
                        "required": ["descriptors", "category_hint"],
                        "properties": {
                            "descriptors": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of target descriptors (e.g., ['player'])"
                            },
                            "category_hint": {
                                "type": "string",
                                "description": "Category hint for target (e.g., 'player')"
                            }
                        }
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Action-specific parameters (optional, varies by action type)"
                    },
                    "assigned_to": {
                        "type": "string",
                        "description": "Companion ID this action is assigned to"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "normal", "high", "critical"],
                        "description": "Action priority level"
                    },
                    "depends_on": {
                        "type": ["string", "null"],
                        "description": "Action ID this depends on (null if none)"
                    }
                }
            }
        },
        "dialogue_context": {
            "type": "string",
            "description": "Original player input for context"
        },
        "requires_clarification": {
            "type": "boolean",
            "description": "Whether the intent is unclear and needs clarification"
        }
    }
}


# ============================================================================
# SCHEMA: Unreal Engine → System (Response)
# ============================================================================

RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["signal_type", "command_id", "actions"],
    "properties": {
        "signal_type": {
            "type": "string",
            "enum": ["validation"],
            "description": "Type of signal (validation for command execution)"
        },
        "command_id": {
            "type": "string",
            "description": "Command ID this response corresponds to"
        },
        "actions": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["action_id", "status", "companion_id", "response_id"],
                "properties": {
                    "action_id": {
                        "type": "string",
                        "description": "Action ID this result corresponds to"
                    },
                    "status": {
                        "type": "boolean",
                        "description": "True if action succeeded, False if failed"
                    },
                    "reason": {
                        "type": ["string", "null"],
                        "description": "Reason for failure (null if succeeded)"
                    },
                    "companion_id": {
                        "type": "string",
                        "description": "ID of companion that executed the action"
                    },
                    "response_id": {
                        "type": "string",
                        "description": "Response ID for dialogue lookup"
                    }
                }
            }
        }
    }
}


# ============================================================================
# Validation Functions
# ============================================================================

def validate_command(command: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate a command against the COMMAND_SCHEMA.
    
    Args:
        command: Dictionary representing the command JSON
        
    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if valid, False otherwise
        - error_message: Empty string if valid, error description otherwise
    """
    try:
        validate(instance=command, schema=COMMAND_SCHEMA)
        return True, ""
    except ValidationError as e:
        return False, f"Schema validation failed: {e.message}"
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def validate_response(response: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate a response against the RESPONSE_SCHEMA.
    
    Args:
        response: Dictionary representing the response JSON
        
    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if valid, False otherwise
        - error_message: Empty string if valid, error description otherwise
    """
    try:
        validate(instance=response, schema=RESPONSE_SCHEMA)
        return True, ""
    except ValidationError as e:
        return False, f"Schema validation failed: {e.message}"
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def pretty_print_json(data: Dict[str, Any]) -> str:
    """
    Pretty print JSON data for logging.
    
    Args:
        data: Dictionary to format
        
    Returns:
        Formatted JSON string
    """
    return json.dumps(data, indent=2)
