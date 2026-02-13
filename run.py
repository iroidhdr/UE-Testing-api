"""
Main Runner - AI Game Companion Prototype

Orchestrates the full pipeline:
1. Text Input
2. LLM (Ollama/llama3) → JSON
3. Mock Unreal Engine → Response
4. Dialogue Resolver → Text Output

Usage:
    python run.py "follow me"
    python run.py "attack that enemy"
    python run.py "wait here"
"""

import sys
import logging
from typing import Optional
from app.intent_compiler import compile_intent
from app.mock_unreal import get_unreal_engine
from app.dialogue_resolver import resolve_dialogue
from app.schema import pretty_print_json
from app.config import LOG_LEVEL, LOG_FORMAT

# Configure logging
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


def run_pipeline(text_input: str) -> bool:
    """
    Run the full AI companion pipeline.
    
    Args:
        text_input: Natural language command from player
        
    Returns:
        True if pipeline succeeded, False otherwise
    """
    print("\n" + "="*80)
    print("AI GAME COMPANION PROTOTYPE - PIPELINE EXECUTION")
    print("="*80)
    
    # ========================================================================
    # STAGE 1: Text Input
    # ========================================================================
    print(f"\n📥 INPUT: {text_input}")
    
    # ========================================================================
    # STAGE 2: LLM → JSON
    # ========================================================================
    print("\n🧠 LLM PROCESSING (Ollama/llama3)...")
    command = compile_intent(text_input)
    
    if command is None:
        print("❌ FAILED: LLM could not generate valid JSON")
        return False
    
    print(f"\n📋 LLM JSON:")
    print(pretty_print_json(command))
    
    # ========================================================================
    # STAGE 3: Unreal Engine Execution
    # ========================================================================
    print("\n🎮 UNREAL ENGINE PROCESSING...")
    ue = get_unreal_engine()
    
    try:
        response = ue.execute_command(command)
    except Exception as e:
        print(f"❌ FAILED: UE execution error: {str(e)}")
        return False
    
    # Extract response_id for display
    response_ids = [action["response_id"] for action in response["actions"]]
    print(f"\n📤 UE RESPONSE: {', '.join(response_ids)}")
    print(f"   Status: {response['actions'][0]['status']}")
    if response['actions'][0]['reason']:
        print(f"   Reason: {response['actions'][0]['reason']}")
    
    # ========================================================================
    # STAGE 4: Dialogue Resolution
    # ========================================================================
    print("\n💬 DIALOGUE RESOLUTION...")
    dialogues = resolve_dialogue(response)
    
    print(f"\n🗣️  DIALOGUE: {dialogues[0]}")
    
    # ========================================================================
    # Success!
    # ========================================================================
    print("\n" + "="*80)
    print("✅ PIPELINE COMPLETED SUCCESSFULLY")
    print("="*80 + "\n")
    
    return True


def main():
    """Main entry point for CLI usage."""
    if len(sys.argv) < 2:
        print("Usage: python run.py \"<command>\"")
        print("\nSupported commands:")
        print("  python run.py \"follow me\"")
        print("  python run.py \"stop following\"")
        print("  python run.py \"wait here\"")
        print("  python run.py \"attack that enemy\"")
        print("  python run.py \"defend this area\"")
        print("  python run.py \"help me\"")
        print("  python run.py \"do a backflip\"      (unknown command)")
        sys.exit(1)
    
    # Get text input from command line
    text_input = " ".join(sys.argv[1:])
    
    # Run pipeline
    success = run_pipeline(text_input)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
