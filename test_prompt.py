import json
from openai import OpenAI

# System prompt from config.py
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
- spatial_direction: "Front", "Left", "Right", "Back" (Use if direction is implied)
- priority: "low", "normal", "high", "critical"

COMMAND STRUCTURE:
{
  "command_id": "cmd_001",
  "actions": [{
    "action_id": "act_001",
    "type": "engage",
    "target": {"descriptors": ["enemy", "sniper"], "category_hint": "enemy"},
    "parameters": {
        "fire_mode": "auto",
        "spatial_direction": "Front" 
    },
    "assigned_to": "companion_01",
    "priority": "high",
    "depends_on": null
  }],
  "dialogue_context": "kill that sniper",
  "requires_clarification": false
}
"""

def create_prompt(text_input):
    return f"""Player input: "{text_input}"

Generate the JSON command following the schema exactly. Output ONLY the JSON, no explanations."""

client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)

text_input = "Move to the left"

try:
    response = client.chat.completions.create(
        model="llama3:latest",
        messages=[
            {"role": "system", "content": INTENT_COMPILER_SYSTEM_PROMPT},
            {"role": "user", "content": create_prompt(text_input)}
        ],
        temperature=0.0
    )
    print("Raw output:")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"Error: {e}")
