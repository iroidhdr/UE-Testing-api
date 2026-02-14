"""
Configuration for AI Game Companion Prototype

Contains:
- Local LLM settings (Ollama)
- System prompts
- Response ID to dialogue mappings
- Logging configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# Local LLM Configuration (Ollama)
# ============================================================================

OLLAMA_BASE_URL = "http://localhost:11434/v1"  # Ollama's OpenAI-compatible endpoint
OLLAMA_MODEL = "llama3:latest"  # Local model
LLM_TEMPERATURE = 0.0  # Deterministic output
LLM_MAX_RETRIES = 3  # Max retries for invalid JSON


# ============================================================================
# System Prompt for Intent Compiler (LLM #1)
# ============================================================================

INTENT_COMPILER_SYSTEM_PROMPT = """You are an intent-to-JSON compiler for a game AI companion.

Your job:
- Classify the player's intent into ONE supported action type
- Output ONLY valid JSON
- Follow the schema exactly
- Do NOT explain, check feasibility, or access game state

SUPPORTED ACTIONS (closed vocabulary):
- move_to           → Move to target (Params: movement_speed, formation, stance)
- follow            → Follow leader (Params: distance, formation)
- hold_position     → Stay (Params: stance, face_direction, duration)
- take_cover        → Move to cover (Params: stance, face_direction)
- engage            → Attack target (Params: engagement_style, fire_mode)
- suppress          → Suppressive fire (Params: duration, fire_mode, ammo_conservation)
- overwatch         → Watch area (Params: engagement_rules, report_events)
- clear_area        → Clear room (Params: engagement_rules, formation)
- pick_up           → Pick up loot (Target descriptors identify item)
- interact          → Use object (Params: interaction [open/close/activate])
- use_item_on       → Use item on target (Params: item_type)
- throw_equipment   → Throw grenade/utility (Params: equipment_type)
- retreat           → Fall back (Params: retreat_direction, movement_speed)
- regroup           → Return to squad (Params: formation)
- cancel            → Cancel current task

COMMON PARAMETERS:
- spatial_direction: "Front", "Left", "Right", "Back" (REQUIRED if direction is mentioned)
- priority: "low", "normal", "high", "critical"

COMMAND STRUCTURE:
{
  "command_id": "cmd_001",
  "actions": [{
    "action_id": "act_001",
    "type": "move_to",
    "target": {"descriptors": ["left"], "category_hint": "location"},
    "parameters": {
        "spatial_direction": "Left" 
    },
    "assigned_to": "companion_01",
    "priority": "normal",
    "depends_on": null
  }],
  "dialogue_context": "move left",
  "requires_clarification": false
}
"""


# ============================================================================
# Response ID to Dialogue Mapping
# ============================================================================

DIALOGUE_MAP = {
    # Movement
    "RESP_FOLLOW_ACCEPT": "Right behind you.",
    "RESP_ALREADY_FOLLOWING": "I'm already following you.",
    "RESP_STOP_ACCEPT": "Stopping here.",
    "RESP_NOT_FOLLOWING": "I'm not moving.",
    "RESP_MOVE_ACCEPT": "Moving to position.",
    "RESP_HOLD_ACCEPT": "Holding position.",
    "RESP_RETREAT_ACCEPT": "Falling back!",
    "RESP_REGROUP_ACCEPT": "On me, regroup!",
    
    # Combat
    "RESP_ENGAGE_ACCEPT": "Engaging target!",
    "RESP_NO_TARGET": "I don't see a target.",
    "RESP_SUPPRESS_ACCEPT": "Laying down suppressing fire!",
    "RESP_OVERWATCH_ACCEPT": "Eyes on the area.",
    "RESP_COVER_ACCEPT": "Taking cover.",
    "RESP_CLEAR_ACCEPT": "Clearing the area.",
    
    # Interaction
    "RESP_PICKUP_ACCEPT": "Got it.",
    "RESP_INTERACT_ACCEPT": "Interacting.",
    "RESP_USE_ITEM_ACCEPT": "Using item.",
    "RESP_THROW_ACCEPT": "Throwing!",
    
    # General
    "RESP_CANCEL_ACCEPT": "Cancelled.",
    "RESP_UNKNOWN_COMMAND": "I didn't understand that command.",
    "RESP_UNSUPPORTED_ACTION": "I don't know how to do that yet."
}


# ============================================================================
# Mock Unreal Engine Configuration
# ============================================================================

DEFAULT_COMPANION_ID = "companion_01"


# ============================================================================
# Logging Configuration
# ============================================================================

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(levelname)s: %(message)s"
