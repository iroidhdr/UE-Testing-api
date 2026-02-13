"""
Intent Compiler - LLM Integration

Converts natural language text input into structured JSON commands
using a local LLM via Ollama (OpenAI-compatible endpoint).
This module is responsible ONLY for:
1. Converting text → JSON
2. Validating JSON against schema
3. Retrying on invalid JSON

It does NOT:
- Check feasibility
- Access game state
- Make decisions about success/failure
"""

from openai import OpenAI
import json
import logging
from typing import Dict, Any, Optional
from schema import validate_command, pretty_print_json
from config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    LLM_TEMPERATURE,
    LLM_MAX_RETRIES,
    INTENT_COMPILER_SYSTEM_PROMPT
)

# Configure logging
logger = logging.getLogger(__name__)


class IntentCompiler:
    """
    Compiles natural language intent into structured JSON commands.
    Uses local Ollama LLM with strict schema validation.
    """
    
    def __init__(self):
        """Initialize the Ollama client via OpenAI-compatible API."""
        self.client = OpenAI(
            api_key="ollama",  # Ollama doesn't need a real key
            base_url=OLLAMA_BASE_URL
        )
        self.model = OLLAMA_MODEL
        logger.info(f"Intent Compiler initialized with local model: {self.model}")
    
    def compile(self, text_input: str) -> Optional[Dict[str, Any]]:
        """
        Compile text input into structured JSON command.
        
        Args:
            text_input: Natural language command from player
            
        Returns:
            Dictionary containing the structured command, or None if failed
        """
        logger.info(f"Compiling intent from input: '{text_input}'")
        
        for attempt in range(1, LLM_MAX_RETRIES + 1):
            try:
                # Create the prompt
                user_prompt = self._create_prompt(text_input)
                
                # Call Ollama via OpenAI-compatible API
                logger.debug(f"Attempt {attempt}/{LLM_MAX_RETRIES}: Calling Ollama ({self.model})...")
                response = self.client.chat.completions.create(
                    model=self.model,
                    temperature=LLM_TEMPERATURE,
                    max_tokens=1024,
                    messages=[
                        {"role": "system", "content": INTENT_COMPILER_SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                
                # Extract text response
                raw_output = response.choices[0].message.content.strip()
                logger.debug(f"Raw LLM output:\n{raw_output}")
                
                if not raw_output:
                    logger.warning(f"Attempt {attempt}: Empty response from Ollama")
                    continue
                
                # Parse JSON
                command = self._parse_json(raw_output)
                if command is None:
                    logger.warning(f"Attempt {attempt}: Failed to parse JSON")
                    logger.debug(f"Raw output was: {raw_output[:200]}...")
                    continue
                
                # Validate against schema
                is_valid, error_msg = validate_command(command)
                if not is_valid:
                    logger.warning(f"Attempt {attempt}: Schema validation failed: {error_msg}")
                    continue
                
                # Success!
                logger.info("✓ Successfully compiled valid JSON command")
                logger.debug(f"Validated command:\n{pretty_print_json(command)}")
                return command
                
            except Exception as e:
                logger.error(f"Attempt {attempt}: Unexpected error: {str(e)}")
                logger.debug(f"Exception details:", exc_info=True)
                continue
        
        # All retries exhausted
        logger.error(f"Failed to compile valid JSON after {LLM_MAX_RETRIES} attempts")
        return None
    
    def _create_prompt(self, text_input: str) -> str:
        """
        Create the user prompt for the LLM.
        
        Args:
            text_input: User's natural language input
            
        Returns:
            Complete prompt string
        """
        return f"""Player input: "{text_input}"

Generate the JSON command following the schema exactly. Output ONLY the JSON, no explanations."""
    
    def _parse_json(self, raw_output: str) -> Optional[Dict[str, Any]]:
        """
        Parse JSON from LLM output, handling common formatting issues.
        
        Args:
            raw_output: Raw text from LLM
            
        Returns:
            Parsed dictionary or None if parsing failed
        """
        # Try to extract JSON from markdown code blocks
        if "```json" in raw_output:
            try:
                start = raw_output.index("```json") + 7
                end = raw_output.index("```", start)
                raw_output = raw_output[start:end].strip()
            except ValueError:
                pass
        elif "```" in raw_output:
            try:
                start = raw_output.index("```") + 3
                end = raw_output.index("```", start)
                raw_output = raw_output[start:end].strip()
            except ValueError:
                pass
        
        # Try to parse JSON
        try:
            return json.loads(raw_output)
        except json.JSONDecodeError as e:
            logger.debug(f"JSON parse error: {str(e)}")
            return None


# ============================================================================
# Convenience function for direct usage
# ============================================================================

def compile_intent(text_input: str) -> Optional[Dict[str, Any]]:
    """
    Compile text input into structured JSON command.
    
    Args:
        text_input: Natural language command from player
        
    Returns:
        Dictionary containing the structured command, or None if failed
    """
    compiler = IntentCompiler()
    return compiler.compile(text_input)
