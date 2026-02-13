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

INTENT_COMPILER_SYSTEM_PROMPT = """You are an intent-to-JSON compiler for a game AI companion system.

Your job:
- Classify the player's intent into ONE supported action type
- Output ONLY valid JSON
- Follow the schema exactly
- Do NOT explain
- Do NOT check feasibility
- Do NOT access game state
- Do NOT invent new actions

SUPPORTED ACTIONS (closed vocabulary):
- follow → companion follows the player
- stop_follow → companion stops following
- wait → companion waits at current position
- attack → companion attacks a target
- defend → companion enters defensive mode
- assist → companion helps the player
- unknown → intent cannot be mapped safely

CLASSIFICATION RULES:
1. If intent clearly matches one action, select it
2. If intent is ambiguous or unsupported, use "unknown"
3. Never output anything except JSON
4. Never check if action is possible (that's Unreal Engine's job)

COMMAND STRUCTURE:
{
  "command_id": "cmd_001",
  "actions": [{
    "action_id": "act_001",
    "type": "follow",
    "target": {"descriptors": ["player"], "category_hint": "player"},
    "parameters": {},
    "assigned_to": "companion_01",
    "priority": "normal",
    "depends_on": null
  }],
  "dialogue_context": "follow me",
  "requires_clarification": false
}

EXAMPLES:

Input: "follow me"
Output: {"command_id": "cmd_001", "actions": [{"action_id": "act_001", "type": "follow", "target": {"descriptors": ["player"], "category_hint": "player"}, "parameters": {"distance_preference_m": 2.0}, "assigned_to": "companion_01", "priority": "normal", "depends_on": null}], "dialogue_context": "follow me", "requires_clarification": false}

Input: "stop following"
Output: {"command_id": "cmd_001", "actions": [{"action_id": "act_001", "type": "stop_follow", "target": {"descriptors": [], "category_hint": "none"}, "parameters": {}, "assigned_to": "companion_01", "priority": "normal", "depends_on": null}], "dialogue_context": "stop following", "requires_clarification": false}

Input: "attack that enemy"
Output: {"command_id": "cmd_001", "actions": [{"action_id": "act_001", "type": "attack", "target": {"descriptors": ["enemy"], "category_hint": "enemy"}, "parameters": {}, "assigned_to": "companion_01", "priority": "normal", "depends_on": null}], "dialogue_context": "attack that enemy", "requires_clarification": false}

Input: "do a backflip"
Output: {"command_id": "cmd_001", "actions": [{"action_id": "act_001", "type": "unknown", "target": {"descriptors": [], "category_hint": "none"}, "parameters": {}, "assigned_to": "companion_01", "priority": "normal", "depends_on": null}], "dialogue_context": "do a backflip", "requires_clarification": false}

REMEMBER: Never explain, never check feasibility, only classify intent.
"""


# ============================================================================
# Response ID to Dialogue Mapping
# ============================================================================

DIALOGUE_MAP = {
    # Follow responses
    "RESP_FOLLOW_ACCEPT": "Alright, I'm right behind you.",
    "RESP_ALREADY_FOLLOWING": "I'm already following you.",
    
    # Stop follow responses
    "RESP_STOP_ACCEPT": "Stopping now.",
    "RESP_NOT_FOLLOWING": "I'm not following you.",
    
    # Wait responses
    "RESP_WAIT_ACCEPT": "I'll wait here.",
    
    # Attack responses
    "RESP_ATTACK_ACCEPT": "Engaging the target!",
    "RESP_NO_TARGET": "I don't see any enemies.",
    
    # Defend responses
    "RESP_DEFEND_ACCEPT": "Defending this position.",
    
    # Assist responses
    "RESP_ASSIST_ACCEPT": "I'm helping you.",
    
    # Unknown command
    "RESP_UNKNOWN_COMMAND": "I'm not sure what you want me to do."
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
