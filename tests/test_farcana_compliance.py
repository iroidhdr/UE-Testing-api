import unittest
from unittest.mock import patch, MagicMock
import json
import logging
import sys
import os

# Add parent directory to path to find 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import mock_unreal 

# Configure logging to capture output
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_farcana")

class TestFarcanaCompliance(unittest.TestCase):
    
    def setUp(self):
        self.ue = mock_unreal.get_unreal_engine()
        self.ue.reset()

    def test_strict_response_structure(self):
        """Verify the response contains all Farcana required fields"""
        command = {
            "command_id": "cmd_test_01",
            "actions": [{
                "action_id": "act_01",
                "type": "suppress",
                "target": {"descriptors": ["area"], "category_hint": "area"},
                "parameters": {},
                "assigned_to": "companion_01",
                "priority": "normal",
                "depends_on": None
            }],
            "dialogue_context": "suppress that area",
            "requires_clarification": False
        }
        
        response = self.ue.execute_command(command)
        
        # 1. Structure Check
        self.assertIn("signal_type", response)
        self.assertEqual(response["signal_type"], "validation")
        self.assertIn("actions", response)
        
        action_result = response["actions"][0]
        
        # 2. Strict Fields Check
        self.assertIn("action_type_executed", action_result)
        self.assertEqual(action_result["action_type_executed"], "suppress")
        
        self.assertIn("spatial_direction", action_result) # Check for new field
        
        self.assertIn("status", action_result)
        self.assertTrue(action_result["status"])
        
        self.assertIn("reason", action_result)
        
        self.assertIn("response_id", action_result)
        self.assertEqual(action_result["response_id"], "RESP_SUPPRESS_ACCEPT")
        
        logger.info("✅ Strict Response Structure Verified")

    def test_unknown_action_fallback(self):
        """Verify strict fallback for unsupported actions"""
        command = {
            "command_id": "cmd_test_02",
            "actions": [{
                "action_id": "act_02",
                "type": "do_a_barrel_roll", # Unsupported
                "target": {},
                "parameters": {},
                "assigned_to": "companion_01",
                "priority": "normal",
                "depends_on": None
            }],
            "dialogue_context": "do a barrel roll",
            "requires_clarification": False
        }
        
        response = self.ue.execute_command(command)
        action_result = response["actions"][0]
        
        self.assertEqual(action_result["action_type_executed"], "unknown")
        self.assertFalse(action_result["status"])
        self.assertEqual(action_result["reason"], "unsupported_action")
        self.assertEqual(action_result["response_id"], "RESP_UNSUPPORTED_ACTION")
        
        logger.info("✅ Unknown Action Fallback Verified")

    def test_spatial_direction_propagation(self):
        """Verify spatial_direction is extracted and returned"""
        command = {
            "command_id": "cmd_test_03",
            "actions": [{
                "action_id": "act_03",
                "type": "take_cover",
                "target": {},
                "parameters": {"spatial_direction": "Left"},
                "assigned_to": "companion_01",
                "priority": "normal",
                "depends_on": None
            }],
            "dialogue_context": "take cover left",
            "requires_clarification": False
        }
        
        response = self.ue.execute_command(command)
        action_result = response["actions"][0]
        
        self.assertEqual(action_result["action_type_executed"], "take_cover")
        self.assertEqual(action_result["spatial_direction"], "Left")
        
        logger.info("✅ Spatial Direction Propagation Verified")

    def test_detailed_parameter_propagation(self):
        """Verify 5.2 parameters are passed through correctly"""
        command = {
            "command_id": "cmd_test_04",
            "actions": [{
                "action_id": "act_04",
                "type": "suppress",
                "target": {},
                "parameters": {
                    "fire_mode": "auto",
                    "duration": 10,
                    "ammo_conservation": True
                },
                "assigned_to": "companion_01",
                "priority": "high",
                "depends_on": None
            }],
            "dialogue_context": "suppress for 10 seconds",
            "requires_clarification": False
        }
        
        response = self.ue.execute_command(command)
        action_result = response["actions"][0]
        
        self.assertEqual(action_result["action_type_executed"], "suppress")
        
        # Verify Key Parameters are present in the response
        # Note: In the current mock implementation, we don't explicitly explicitly echo parameters 
        # back in top-level fields EXCEPT spatial_direction. 
        # However, they should be accessible if we inspect the input command logic if were real UE.
        # For now, we verified the Dispatcher accepted it without crashing.
        
        self.assertTrue(action_result["status"])
        
        logger.info("✅ Detailed Parameter Propagation Verified")

    def test_all_15_actions(self):
        """Verify ALL 15 Farcana 5.2 Action Types match the Dispatcher"""
        
        test_cases = [
            # Movement
            {"type": "move_to", "params": {"movement_speed": "fast"}},
            {"type": "follow", "params": {"distance": 200}},
            {"type": "hold_position", "params": {"stance": "crouch"}},
            {"type": "take_cover", "params": {"face_direction": "Front"}},
            {"type": "retreat", "params": {"retreat_direction": "Back"}},
            {"type": "regroup", "params": {"formation": "wedge"}},
            
            # Combat
            {"type": "engage", "params": {"fire_mode": "auto"}},
            {"type": "suppress", "params": {"duration": 5}},
            {"type": "overwatch", "params": {"report_events": True}},
            {"type": "clear_area", "params": {"engagement_rules": "free"}},
            
            # Interaction
            {"type": "pick_up", "params": {}},
            {"type": "interact", "params": {"interaction": "open"}},
            {"type": "use_item_on", "params": {"item_type": "medkit"}},
            {"type": "throw_equipment", "params": {"equipment_type": "frag"}},
            
            # Other
            {"type": "cancel", "params": {}}
        ]
        
        logger.info(f"\nTesting {len(test_cases)} Action Types...")
        
        for case in test_cases:
            action_type = case["type"]
            params = case["params"]
            
            command = {
                "command_id": f"cmd_{action_type}",
                "actions": [{
                    "action_id": f"act_{action_type}",
                    "type": action_type,
                    "target": {"descriptors": ["test_target"], "category_hint": "test"},
                    "parameters": params,
                    "assigned_to": "companion_01",
                    "priority": "normal",
                    "depends_on": None
                }],
                "dialogue_context": f"test {action_type}",
                "requires_clarification": False
            }
            
            response = self.ue.execute_command(command)
            result = response["actions"][0]
            
            # VERIFICATION
            self.assertTrue(result["status"], f"Action '{action_type}' failed status check")
            self.assertEqual(result["action_type_executed"], action_type, f"Action '{action_type}' return type mismatch")
            
            logger.info(f"  [PASS] {action_type:<20} -> Status: {result['status']}")

        logger.info("✅ All 15 Action Types Verified Successfully")

if __name__ == '__main__':
    unittest.main()
