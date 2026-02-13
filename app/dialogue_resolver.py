"""
Dialogue Resolver

Maps response_id to dialogue text.
This is a PURE LOOKUP - no LLM involvement, no logic.
The mapping is deterministic and defined in config.py.
"""

import logging
from typing import Dict, Any, List
from .config import DIALOGUE_MAP

# Configure logging
logger = logging.getLogger(__name__)


class DialogueResolver:
    """
    Resolves response_id to dialogue text.
    Pure lookup, no AI, no logic.
    """
    
    def __init__(self):
        """Initialize the dialogue resolver."""
        self.dialogue_map = DIALOGUE_MAP
        logger.info(f"Dialogue Resolver initialized with {len(self.dialogue_map)} mappings")
    
    def resolve(self, response: Dict[str, Any]) -> List[str]:
        """
        Resolve response_id(s) to dialogue text.
        
        Args:
            response: Response JSON from Unreal Engine
            
        Returns:
            List of dialogue strings (one per action)
        """
        dialogues = []
        
        for action_result in response["actions"]:
            response_id = action_result["response_id"]
            dialogue = self._lookup_dialogue(response_id)
            dialogues.append(dialogue)
        
        return dialogues
    
    def _lookup_dialogue(self, response_id: str) -> str:
        """
        Look up dialogue text for a response_id.
        
        Args:
            response_id: Response identifier from UE
            
        Returns:
            Dialogue text string
        """
        if response_id not in self.dialogue_map:
            logger.warning(f"Unknown response_id: {response_id}")
            return f"[Unknown response: {response_id}]"
        
        dialogue = self.dialogue_map[response_id]
        logger.debug(f"Resolved {response_id} → '{dialogue}'")
        return dialogue


# ============================================================================
# Convenience function for direct usage
# ============================================================================

def resolve_dialogue(response: Dict[str, Any]) -> List[str]:
    """
    Resolve response_id(s) to dialogue text.
    
    Args:
        response: Response JSON from Unreal Engine
        
    Returns:
        List of dialogue strings (one per action)
    """
    resolver = DialogueResolver()
    return resolver.resolve(response)
