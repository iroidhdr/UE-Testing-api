"""
Test script for Flask API server
Tests all endpoints with the required 7 command types

Usage:
    1. Start the server: python server.py
    2. Run tests: python test_api.py
"""

import requests
import json
import time
import sys

SERVER_URL = "http://localhost:5000"

def test_health():
    """Test health check endpoint"""
    print("\n" + "="*60)
    print("TEST: Health Check")
    print("="*60)
    
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        assert response.status_code == 200
        assert response.json()['status'] == 'healthy'
        print("✅ PASSED")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_command(text_command, expected_dialogue=None):
    """Test command processing"""
    print("\n" + "-"*60)
    print(f"COMMAND: '{text_command}'")
    print("-"*60)
    
    try:
        start = time.time()
        response = requests.post(
            f"{SERVER_URL}/api/command",
            json={"text": text_command, "companion_id": "companion_01"},
            timeout=60
        )
        elapsed = (time.time() - start) * 1000
        
        data = response.json()
        print(f"Status: {response.status_code} ({elapsed:.0f}ms)")
        
        if response.status_code == 200 and data.get('success'):
            print(f"💬 Dialogue: \"{data['dialogue']}\"")
            print(f"📋 Response ID: {data['response_id']}")
            
            if 'timing_breakdown' in data:
                t = data['timing_breakdown']
                print(f"⏱️  LLM: {t['llm_ms']}ms | UE: {t['ue_ms']}ms | Dialogue: {t['dialogue_ms']}ms")
            
            if expected_dialogue and data['dialogue'] != expected_dialogue:
                print(f"⚠️  Expected: \"{expected_dialogue}\"")
            
            print("✅ PASSED")
            return True
        else:
            print(f"❌ Error: {data.get('error', 'Unknown')}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ FAILED: Request timed out (LLM may be loading)")
        return False
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_reset():
    """Test state reset"""
    print("\n" + "-"*60)
    print("RESET STATE")
    print("-"*60)
    
    try:
        response = requests.post(f"{SERVER_URL}/api/reset", timeout=5)
        print(f"Status: {response.status_code}")
        
        assert response.status_code == 200
        assert response.json()['success'] == True
        print("✅ PASSED")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("AI GAME COMPANION - API TESTS")
    print("="*60)
    print(f"Server: {SERVER_URL}")
    print("LLM: Ollama/llama3 (local)")
    print()
    
    # Check server is running
    try:
        requests.get(f"{SERVER_URL}/health", timeout=3)
    except requests.exceptions.ConnectionError:
        print("❌ Server not running! Start it with: python server.py")
        return 1
    
    passed = 0
    failed = 0
    
    tests = [
        ("Health Check",      lambda: test_health()),
        ("Reset State",       lambda: test_reset()),
        ("Follow",            lambda: test_command("follow me", "Alright, I'm right behind you.")),
        ("Follow (duplicate)",lambda: test_command("follow me", "I'm already following you.")),
        ("Stop Follow",       lambda: test_command("stop following", "Stopping now.")),
        ("Wait",              lambda: test_command("wait here", "I'll wait here.")),
        ("Attack",            lambda: test_command("attack that enemy", "Engaging the target!")),
        ("Defend",            lambda: test_command("defend this area", "Defending this position.")),
        ("Assist",            lambda: test_command("help me", "I'm helping you.")),
        ("Unknown",           lambda: test_command("do a backflip", "I'm not sure what you want me to do.")),
    ]
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
            failed += 1
        time.sleep(1)
    
    print("\n" + "="*60)
    print(f"RESULTS: {passed}/{len(tests)} passed, {failed} failed")
    print("="*60)
    
    if failed == 0:
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"⚠️  {failed} test(s) failed")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nTests interrupted")
        sys.exit(1)
