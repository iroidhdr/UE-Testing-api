"""
Mock Unreal Engine Executor

This module simulates the Unreal Engine game environment.
It is the SOLE AUTHORITY for:
- Validating commands
- Determining success/failure
- Returning response_id for dialogue

The LLM has NO say in feasibility - only UE decides.
"""

import logging
from typing import Dict, Any
from .schema import validate_response, pretty_print_json
from .config import DEFAULT_COMPANION_ID

# Configure logging
logger = logging.getLogger(__name__)


class MockUnrealEngine:
    """
    Mock Unreal Engine executor.
    Maintains simple state and validates commands using a strict Dispatcher Pattern.
    """
    
    def __init__(self):
        """Initialize the mock UE environment."""
        # Companion state: tracks all companion behaviors
        self.companion_state = {
            DEFAULT_COMPANION_ID: {
                "is_following": False,
                "is_waiting": False,
                "is_defending": False,
                "following_target": None,
                "current_target": None,
                "location": "default_spawn"
            }
        }
        logger.info("Mock Unreal Engine initialized")
    
    def execute_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a command and return the result.
        
        Args:
            command: Validated command JSON from LLM
            
        Returns:
            Response JSON with status, action_type_executed, and response_id
        """
        command_id = command["command_id"]
        actions = command["actions"]
        
        logger.info(f"Executing command: {command_id}")
        
        # Process each action
        action_results = []
        for action in actions:
            result = self._execute_action(action)
            action_results.append(result)
        
        # Build response
        response = {
            "signal_type": "validation",
            "command_id": command_id,
            "actions": action_results
        }
        
        # Validate response schema (sanity check)
        is_valid, error_msg = validate_response(response)
        if not is_valid:
            logger.error(f"Generated invalid response: {error_msg}")
            raise ValueError(f"Invalid response generated: {error_msg}")
        
        logger.info("✓ Command executed successfully")
        logger.debug(f"Response:\n{pretty_print_json(response)}")
        
        return response
    
    def _execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatcher for actions.
         Strictly maps action['type'] to a handler function.
        """
        action_type = action["type"]
        
        # Dispatch Table
        dispatch_table = {
            "follow": self._execute_follow,
            "stop_follow": self._execute_stop_follow,
            "wait": self._execute_wait,
            "attack": self._execute_engage,      # Legacy support
            "engage": self._execute_engage,
            "defend": self._execute_defend,
            "assist": self._execute_assist,
            "move_to": self._execute_move_to,
            "hold_position": self._execute_hold_position,
            "take_cover": self._execute_take_cover,
            "suppress": self._execute_suppress,
            "overwatch": self._execute_overwatch,
            "clear_area": self._execute_clear_area,
            "pick_up": self._execute_pick_up,
            "interact": self._execute_interact,
            "use_item_on": self._execute_use_item_on,
            "throw_equipment": self._execute_throw_equipment,
            "retreat": self._execute_retreat,
            "regroup": self._execute_regroup,
            "cancel": self._execute_cancel,
            "unknown": self._execute_unknown
        }
        
        if action_type not in dispatch_table:
            return {
                "action_id": action["action_id"],
                "action_type_executed": "unknown",
                "status": False,
                "reason": "unsupported_action",
                "companion_id": action.get("assigned_to", "unknown"),
                "spatial_direction": None,
                "response_id": "RESP_UNSUPPORTED_ACTION"
            }
            
        handler = dispatch_table[action_type]
        return handler(action)

    # =========================================================================
    # Action Handlers
    # =========================================================================

    def _execute_follow(self, action: Dict[str, Any]) -> Dict[str, Any]:
        companion_id = action.get("assigned_to", DEFAULT_COMPANION_ID)
        state = self.companion_state.get(companion_id, {})
        
        if state.get("is_following"):
            return self._build_result(action, "follow", False, "already_following", "RESP_ALREADY_FOLLOWING")
        
        state["is_following"] = True
        return self._build_result(action, "follow", True, None, "RESP_FOLLOW_ACCEPT")

    def _execute_stop_follow(self, action: Dict[str, Any]) -> Dict[str, Any]:
        companion_id = action.get("assigned_to", DEFAULT_COMPANION_ID)
        state = self.companion_state.get(companion_id, {})
        
        if not state.get("is_following"):
            return self._build_result(action, "stop_follow", False, "not_following", "RESP_NOT_FOLLOWING")
        
        state["is_following"] = False
        return self._build_result(action, "stop_follow", True, None, "RESP_STOP_ACCEPT")

    def _execute_wait(self, action: Dict[str, Any]) -> Dict[str, Any]:
        # Alias for Hold Position
        return self._execute_hold_position(action)

    def _execute_hold_position(self, action: Dict[str, Any]) -> Dict[str, Any]:
        companion_id = action.get("assigned_to", DEFAULT_COMPANION_ID)
        state = self.companion_state.get(companion_id, {})
        
        state["is_following"] = False
        state["is_waiting"] = True
        return self._build_result(action, "hold_position", True, None, "RESP_HOLD_ACCEPT")

    def _execute_engage(self, action: Dict[str, Any]) -> Dict[str, Any]:
        target = action.get("target", {})
        descriptors = target.get("descriptors", [])
        
        if not descriptors:
            return self._build_result(action, "engage", False, "no_target", "RESP_NO_TARGET")
            
        return self._build_result(action, "engage", True, None, "RESP_ENGAGE_ACCEPT")

    def _execute_defend(self, action: Dict[str, Any]) -> Dict[str, Any]:
        return self._build_result(action, "defend", True, None, "RESP_DEFEND_ACCEPT")

    def _execute_assist(self, action: Dict[str, Any]) -> Dict[str, Any]:
        return self._build_result(action, "assist", True, None, "RESP_ASSIST_ACCEPT")

    def _execute_move_to(self, action: Dict[str, Any]) -> Dict[str, Any]:
        return self._build_result(action, "move_to", True, None, "RESP_MOVE_ACCEPT")

    def _execute_take_cover(self, action: Dict[str, Any]) -> Dict[str, Any]:
        return self._build_result(action, "take_cover", True, None, "RESP_COVER_ACCEPT")

    def _execute_suppress(self, action: Dict[str, Any]) -> Dict[str, Any]:
        return self._build_result(action, "suppress", True, None, "RESP_SUPPRESS_ACCEPT")

    def _execute_overwatch(self, action: Dict[str, Any]) -> Dict[str, Any]:
        return self._build_result(action, "overwatch", True, None, "RESP_OVERWATCH_ACCEPT")

    def _execute_clear_area(self, action: Dict[str, Any]) -> Dict[str, Any]:
        return self._build_result(action, "clear_area", True, None, "RESP_CLEAR_ACCEPT")

    def _execute_pick_up(self, action: Dict[str, Any]) -> Dict[str, Any]:
        return self._build_result(action, "pick_up", True, None, "RESP_PICKUP_ACCEPT")

    def _execute_interact(self, action: Dict[str, Any]) -> Dict[str, Any]:
        return self._build_result(action, "interact", True, None, "RESP_INTERACT_ACCEPT")

    def _execute_use_item_on(self, action: Dict[str, Any]) -> Dict[str, Any]:
        return self._build_result(action, "use_item_on", True, None, "RESP_USE_ITEM_ACCEPT")

    def _execute_throw_equipment(self, action: Dict[str, Any]) -> Dict[str, Any]:
        return self._build_result(action, "throw_equipment", True, None, "RESP_THROW_ACCEPT")

    def _execute_retreat(self, action: Dict[str, Any]) -> Dict[str, Any]:
        return self._build_result(action, "retreat", True, None, "RESP_RETREAT_ACCEPT")

    def _execute_regroup(self, action: Dict[str, Any]) -> Dict[str, Any]:
        return self._build_result(action, "regroup", True, None, "RESP_REGROUP_ACCEPT")

    def _execute_cancel(self, action: Dict[str, Any]) -> Dict[str, Any]:
        return self._build_result(action, "cancel", True, None, "RESP_CANCEL_ACCEPT")

    def _execute_unknown(self, action: Dict[str, Any]) -> Dict[str, Any]:
        return self._build_result(action, "unknown", False, "unknown_command", "RESP_UNKNOWN_COMMAND")

    def _build_result(self, action, executed_type, status, reason, response_id):
        """Helper to build standardized response."""
        # Extract direction if present in parameters
        params = action.get("parameters", {})
        direction = params.get("spatial_direction")
        
        return {
            "action_id": action["action_id"],
            "action_type_executed": executed_type,
            "spatial_direction": direction,
            "status": status,
            "reason": reason,
            "companion_id": action.get("assigned_to", DEFAULT_COMPANION_ID),
            "response_id": response_id
        }

    def reset(self):
        """Reset the UE state (for testing)."""
        logger.info("Resetting Mock Unreal Engine state")
        for companion_id in self.companion_state:
            self.companion_state[companion_id] = {
                "is_following": False,
                "is_waiting": False,
                "is_defending": False,
                "following_target": None,
                "current_target": None
            }


# ============================================================================
# Singleton instance
# ============================================================================

_ue_instance = None

def get_unreal_engine() -> MockUnrealEngine:
    global _ue_instance
    if _ue_instance is None:
        _ue_instance = MockUnrealEngine()
    return _ue_instance
