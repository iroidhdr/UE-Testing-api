"""
Quick server test script
Tests basic server functionality with a few commands

Usage:
    1. Start the server: python server.py
    2. Run tests: python test_server.py
"""

import requests
import json
import time

SERVER_URL = "http://localhost:5000"

def test_health():
    """Test health check endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    
    response = requests.get(f"{SERVER_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    assert response.json()['status'] == 'healthy'
    print("✅ PASSED")

def test_command(text_command):
    """Test command processing"""
    print("\n" + "="*60)
    print(f"TEST: '{text_command}'")
    print("="*60)
    
    start = time.time()
    response = requests.post(
        f"{SERVER_URL}/api/command",
        json={"text": text_command, "companion_id": "companion_01"},
        timeout=60
    )
    elapsed = (time.time() - start) * 1000
    
    print(f"Status: {response.status_code} ({elapsed:.0f}ms)")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    data = response.json()
    assert data['success'] == True
    assert 'dialogue' in data
    assert 'response_id' in data
    
    print(f"💬 Dialogue: \"{data['dialogue']}\"")
    print("✅ PASSED")
    return data

def test_reset():
    """Test state reset"""
    print("\n" + "="*60)
    print("TEST: State Reset")
    print("="*60)
    
    response = requests.post(f"{SERVER_URL}/api/reset")
    print(f"Status: {response.status_code}")
    
    assert response.status_code == 200
    assert response.json()['success'] == True
    print("✅ PASSED")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("AI GAME COMPANION - SERVER TESTS")
    print("="*60)
    print(f"Server: {SERVER_URL}")
    print("LLM: Ollama/llama3 (local)")
    
    try:
        test_health()
        test_reset()
        test_command("follow me")
        test_command("attack that enemy")
        test_reset()
        test_command("wait here")
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to server")
        print("Start it with: python server.py")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
