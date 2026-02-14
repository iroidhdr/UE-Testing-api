"""
Flask Web Server for AI Game Companion
Converts the prototype into a production-ready REST API for Unreal Engine integration
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import time
from app.intent_compiler import compile_intent
from app.mock_unreal import get_unreal_engine
from app.dialogue_resolver import resolve_dialogue
from app.schema import pretty_print_json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for Unreal Engine requests

# Initialize UE instance
ue = get_unreal_engine()

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring
    """
    return jsonify({
        'status': 'healthy',
        'service': 'AI Game Companion',
        'version': '1.0.0'
    })

@app.route('/api/command', methods=['POST'])
def process_command():
    """
    Main endpoint for processing text commands from Unreal Engine
    
    Request Body:
    {
        "text": "follow me",
        "companion_id": "companion_01",  // optional
        "player_id": "player_01"         // optional
    }
    
    Response:
    {
        "success": true,
        "dialogue": "Alright, I'm right behind you.",
        "response_id": "RESP_FOLLOW_ACCEPT",
        "command_id": "cmd_001",
        "processing_time_ms": 1523
    }
    """
    start_time = time.time()
    
    try:
        # Parse request
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        text_input = data.get('text', '').strip()
        if not text_input:
            return jsonify({
                'success': False,
                'error': 'Text field is required'
            }), 400
        
        companion_id = data.get('companion_id', 'companion_01')
        player_id = data.get('player_id', 'player_01')
        
        logger.info(f"Processing command: '{text_input}' for companion: {companion_id}")
        
        # Step 1: Compile intent with LLM
        logger.info("Step 1: Compiling intent with Ollama...")
        compile_start = time.time()
        command = compile_intent(text_input)
        compile_time = (time.time() - compile_start) * 1000
        
        if not command:
            logger.error("Failed to compile intent")
            return jsonify({
                'success': False,
                'error': 'Failed to understand command. Please try rephrasing.',
                'processing_time_ms': int((time.time() - start_time) * 1000)
            }), 400
        
        logger.info(f"Intent compiled in {compile_time:.0f}ms")
        logger.debug(f"Command JSON:\n{pretty_print_json(command)}")
        
        # Step 2: Execute in Unreal Engine
        logger.info("Step 2: Executing command in UE...")
        ue_start = time.time()
        response = ue.execute_command(command)
        ue_time = (time.time() - ue_start) * 1000
        logger.info(f"UE execution completed in {ue_time:.0f}ms")
        
        # Step 3: Resolve dialogue
        logger.info("Step 3: Resolving dialogue...")
        dialogue_start = time.time()
        dialogues = resolve_dialogue(response)
        dialogue_time = (time.time() - dialogue_start) * 1000
        logger.info(f"Dialogue resolved in {dialogue_time:.0f}ms")
        
        # Calculate total time
        total_time = (time.time() - start_time) * 1000
        
        # Build strict response
        action_result = response['actions'][0]
        result = {
            'success': action_result['status'],
            'dialogue': dialogues[0],
            'response_id': action_result['response_id'],
            'command_id': response['command_id'],
            'action_type_executed': action_result['action_type_executed'],
            'spatial_direction': action_result.get('spatial_direction'),
            'action_status': action_result['status'],
            'action_reason': action_result.get('reason'),
            'processing_time_ms': int(total_time),
            'timing_breakdown': {
                'llm_ms': int(compile_time),
                'ue_ms': int(ue_time),
                'dialogue_ms': int(dialogue_time)
            }
        }
        
        # 5️⃣ Add Structured Logging (Farcana Requirement)
        log_msg = f"""
        \n==================================================
        UE EXECUTION REPORT
        ==================================================
        INPUT: "{text_input}"
        --------------------------------------------------
        LLM OUTPUT:
        {command['actions'][0]['type']} (Target: {command['actions'][0].get('target', {}).get('category_hint')})
        --------------------------------------------------
        UE EXECUTION:
        Action Type: {action_result['action_type_executed']}
        Status: {action_result['status']}
        Reason: {action_result['reason']}
        Response ID: {action_result['response_id']}
        --------------------------------------------------
        DIALOGUE:
        "{dialogues[0]}"
        ==================================================\n"""
        logger.info(log_msg)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing command: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}',
            'processing_time_ms': int((time.time() - start_time) * 1000)
        }), 500

@app.route('/api/reset', methods=['POST'])
def reset_state():
    """
    Reset the UE state (for testing/debugging)
    """
    try:
        ue.reset()
        logger.info("UE state reset")
        return jsonify({
            'success': True,
            'message': 'State reset successfully'
        })
    except Exception as e:
        logger.error(f"Error resetting state: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    logger.info("="*80)
    logger.info("AI GAME COMPANION SERVER")
    logger.info("="*80)
    logger.info("Server starting on http://0.0.0.0:5000")
    logger.info("Endpoints:")
    logger.info("  GET  /health          - Health check")
    logger.info("  POST /api/command     - Process text command")
    logger.info("  POST /api/reset       - Reset UE state")
    logger.info("="*80)
    
    # Run server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
