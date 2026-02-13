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
    Maintains simple state and validates commands.
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
                "current_target": None
            }
        }
        logger.info("Mock Unreal Engine initialized")
    
    def execute_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a command and return the result.
        
        This is where ALL game logic lives. The LLM has no say here.
        
        Args:
            command: Validated command JSON from LLM
            
        Returns:
            Response JSON with status and response_id
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
        Execute a single action.
        
        Args:
            action: Action dictionary from command
            
        Returns:
            Action result dictionary
        """
        action_id = action["action_id"]
        action_type = action["type"]
        assigned_to = action["assigned_to"]
        
        logger.debug(f"Executing action {action_id} (type: {action_type})")
        
        # Command routing: dispatch to appropriate handler
        if action_type == "follow":
            return self._execute_follow(action_id, assigned_to, action["target"])
        elif action_type == "stop_follow":
            return self._execute_stop_follow(action_id, assigned_to)
        elif action_type == "wait":
            return self._execute_wait(action_id, assigned_to)
        elif action_type == "attack":
            return self._execute_attack(action_id, assigned_to, action["target"])
        elif action_type == "defend":
            return self._execute_defend(action_id, assigned_to)
        elif action_type == "assist":
            return self._execute_assist(action_id, assigned_to)
        elif action_type == "unknown":
            return self._execute_unknown(action_id, assigned_to)
        else:
            # Fallback for truly unknown types (shouldn't happen)
            logger.error(f"Unhandled action type: {action_type}")
            return {
                "action_id": action_id,
                "status": False,
                "reason": f"Unhandled action type: {action_type}",
                "companion_id": assigned_to,
                "response_id": "RESP_UNKNOWN_COMMAND"
            }
    
    def _execute_follow(self, action_id: str, companion_id: str, target: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a 'follow' action.
        
        Game Logic:
        - If companion is already following → FAIL (RESP_ALREADY_FOLLOWING)
        - Otherwise → SUCCESS (RESP_FOLLOW_ACCEPT)
        
        Args:
            action_id: Action identifier
            companion_id: Companion to execute action
            target: Target information
            
        Returns:
            Action result dictionary
        """
        # Get companion state
        if companion_id not in self.companion_state:
            # Unknown companion
            logger.warning(f"Unknown companion: {companion_id}")
            return {
                "action_id": action_id,
                "status": False,
                "reason": "Unknown companion",
                "companion_id": companion_id,
                "response_id": "RESP_CANNOT_FOLLOW"
            }
        
        state = self.companion_state[companion_id]
        
        # Check if already following
        if state["is_following"]:
            logger.info(f"Companion {companion_id} is already following")
            return {
                "action_id": action_id,
                "status": False,
                "reason": "Already following",
                "companion_id": companion_id,
                "response_id": "RESP_ALREADY_FOLLOWING"
            }
        
        # Execute follow action
        target_category = target.get("category_hint", "unknown")
        logger.info(f"Companion {companion_id} now following {target_category}")
        
        # Update state
        state["is_following"] = True
        state["following_target"] = target_category
        
        return {
            "action_id": action_id,
            "status": True,
            "reason": None,
            "companion_id": companion_id,
            "response_id": "RESP_FOLLOW_ACCEPT"
        }
    
    def _execute_stop_follow(self, action_id: str, companion_id: str) -> Dict[str, Any]:
        """
        Execute a 'stop_follow' action.
        
        Game Logic:
        - If companion is not following → FAIL (RESP_NOT_FOLLOWING)
        - Otherwise → SUCCESS (RESP_STOP_ACCEPT)
        """
        if companion_id not in self.companion_state:
            return {
                "action_id": action_id,
                "status": False,
                "reason": "Unknown companion",
                "companion_id": companion_id,
                "response_id": "RESP_UNKNOWN_COMMAND"
            }
        
        state = self.companion_state[companion_id]
        
        if not state["is_following"]:
            logger.info(f"Companion {companion_id} is not following")
            return {
                "action_id": action_id,
                "status": False,
                "reason": "Not following",
                "companion_id": companion_id,
                "response_id": "RESP_NOT_FOLLOWING"
            }
        
        # Stop following
        logger.info(f"Companion {companion_id} stopped following")
        state["is_following"] = False
        state["following_target"] = None
        
        return {
            "action_id": action_id,
            "status": True,
            "reason": None,
            "companion_id": companion_id,
            "response_id": "RESP_STOP_ACCEPT"
        }
    
    def _execute_wait(self, action_id: str, companion_id: str) -> Dict[str, Any]:
        """
        Execute a 'wait' action.
        
        Game Logic:
        - Companion enters waiting state
        - Always succeeds
        """
        if companion_id not in self.companion_state:
            return {
                "action_id": action_id,
                "status": False,
                "reason": "Unknown companion",
                "companion_id": companion_id,
                "response_id": "RESP_UNKNOWN_COMMAND"
            }
        
        state = self.companion_state[companion_id]
        
        # Enter waiting state
        logger.info(f"Companion {companion_id} is now waiting")
        state["is_waiting"] = True
        state["is_following"] = False  # Can't wait and follow
        state["following_target"] = None
        
        return {
            "action_id": action_id,
            "status": True,
            "reason": None,
            "companion_id": companion_id,
            "response_id": "RESP_WAIT_ACCEPT"
        }
    
    def _execute_attack(self, action_id: str, companion_id: str, target: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an 'attack' action.
        
        Game Logic:
        - Check if target exists (simplified: check if descriptors provided)
        - If no target → FAIL (RESP_NO_TARGET)
        - Otherwise → SUCCESS (RESP_ATTACK_ACCEPT)
        """
        if companion_id not in self.companion_state:
            return {
                "action_id": action_id,
                "status": False,
                "reason": "Unknown companion",
                "companion_id": companion_id,
                "response_id": "RESP_UNKNOWN_COMMAND"
            }
        
        state = self.companion_state[companion_id]
        
        # Check if target is specified
        descriptors = target.get("descriptors", [])
        if not descriptors or descriptors == []:
            logger.info(f"Companion {companion_id} has no attack target")
            return {
                "action_id": action_id,
                "status": False,
                "reason": "No target specified",
                "companion_id": companion_id,
                "response_id": "RESP_NO_TARGET"
            }
        
        # Execute attack
        target_desc = ", ".join(descriptors)
        logger.info(f"Companion {companion_id} attacking {target_desc}")
        state["current_target"] = target_desc
        state["is_waiting"] = False
        
        return {
            "action_id": action_id,
            "status": True,
            "reason": None,
            "companion_id": companion_id,
            "response_id": "RESP_ATTACK_ACCEPT"
        }
    
    def _execute_defend(self, action_id: str, companion_id: str) -> Dict[str, Any]:
        """
        Execute a 'defend' action.
        
        Game Logic:
        - Companion enters defensive mode
        - Always succeeds
        """
        if companion_id not in self.companion_state:
            return {
                "action_id": action_id,
                "status": False,
                "reason": "Unknown companion",
                "companion_id": companion_id,
                "response_id": "RESP_UNKNOWN_COMMAND"
            }
        
        state = self.companion_state[companion_id]
        
        # Enter defensive mode
        logger.info(f"Companion {companion_id} is now defending")
        state["is_defending"] = True
        state["is_waiting"] = False
        
        return {
            "action_id": action_id,
            "status": True,
            "reason": None,
            "companion_id": companion_id,
            "response_id": "RESP_DEFEND_ACCEPT"
        }
    
    def _execute_assist(self, action_id: str, companion_id: str) -> Dict[str, Any]:
        """
        Execute an 'assist' action.
        
        Game Logic:
        - Companion helps the player
        - Always succeeds
        """
        if companion_id not in self.companion_state:
            return {
                "action_id": action_id,
                "status": False,
                "reason": "Unknown companion",
                "companion_id": companion_id,
                "response_id": "RESP_UNKNOWN_COMMAND"
            }
        
        logger.info(f"Companion {companion_id} is assisting")
        
        return {
            "action_id": action_id,
            "status": True,
            "reason": None,
            "companion_id": companion_id,
            "response_id": "RESP_ASSIST_ACCEPT"
        }
    
    def _execute_unknown(self, action_id: str, companion_id: str) -> Dict[str, Any]:
        """
        Execute an 'unknown' action.
        
        Game Logic:
        - LLM classified intent as unknown/unsupported
        - Always fails with RESP_UNKNOWN_COMMAND
        """
        logger.info(f"Unknown command for companion {companion_id}")
        
        return {
            "action_id": action_id,
            "status": False,
            "reason": "Unknown or unsupported command",
            "companion_id": companion_id,
            "response_id": "RESP_UNKNOWN_COMMAND"
        }
    
    def reset(self):
        """Reset the UE state (for testing)."""
        logger.info("Resetting Mock Unreal Engine state")
        for companion_id in self.companion_state:
            self.companion_state[companion_id]["is_following"] = False
            self.companion_state[companion_id]["is_waiting"] = False
            self.companion_state[companion_id]["is_defending"] = False
            self.companion_state[companion_id]["following_target"] = None
            self.companion_state[companion_id]["current_target"] = None


# ============================================================================
# Singleton instance for convenience
# ============================================================================

_ue_instance = None

def get_unreal_engine() -> MockUnrealEngine:
    """Get the singleton Mock UE instance."""
    global _ue_instance
    if _ue_instance is None:
        _ue_instance = MockUnrealEngine()
    return _ue_instance
