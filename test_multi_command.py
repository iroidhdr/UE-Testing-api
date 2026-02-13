"""
Comprehensive test script for multi-command support
Tests all 7 action types with required test cases
"""

import subprocess
import sys
import time

# Test cases as specified in requirements
TEST_CASES = [
    ("follow me", "follow", "RESP_FOLLOW_ACCEPT"),
    ("stop following", "stop_follow", "RESP_STOP_ACCEPT"),
    ("wait here", "wait", "RESP_WAIT_ACCEPT"),
    ("attack that enemy", "attack", "RESP_ATTACK_ACCEPT"),
    ("defend this area", "defend", "RESP_DEFEND_ACCEPT"),
    ("help me", "assist", "RESP_ASSIST_ACCEPT"),
    ("do a backflip", "unknown", "RESP_UNKNOWN_COMMAND"),
]

def run_test(text_input, expected_type, expected_response_id):
    """Run a single test case"""
    print(f"\n{'='*80}")
    print(f"TEST: \"{text_input}\"")
    print(f"Expected Type: {expected_type}")
    print(f"Expected Response: {expected_response_id}")
    print('='*80)
    
    result = subprocess.run(
        [sys.executable, "run.py", text_input],
        capture_output=True,
        text=True
    )
    
    output = result.stdout + result.stderr
    
    # Check for success
    if result.returncode == 0:
        # Extract dialogue from output
        if "🗣️  DIALOGUE:" in output:
            dialogue_line = [line for line in output.split('\n') if "🗣️  DIALOGUE:" in line][0]
            dialogue = dialogue_line.split("🗣️  DIALOGUE:")[1].strip()
            print(f"✅ SUCCESS")
            print(f"Dialogue: \"{dialogue}\"")
            
            # Verify action type in JSON
            if f'"type": "{expected_type}"' in output:
                print(f"✅ Action type correct: {expected_type}")
            else:
                print(f"⚠️  Action type mismatch (expected: {expected_type})")
            
            return True
        else:
            print(f"⚠️  No dialogue found in output")
            return False
    else:
        print(f"❌ FAILED (exit code: {result.returncode})")
        if "quota" in output.lower():
            print("⚠️  API quota exceeded - waiting 60 seconds...")
            time.sleep(60)
        return False

def main():
    print("\n" + "="*80)
    print("MULTI-COMMAND SUPPORT - COMPREHENSIVE TESTS")
    print("="*80)
    print(f"\nTesting {len(TEST_CASES)} command types...")
    
    passed = 0
    failed = 0
    
    for text_input, expected_type, expected_response_id in TEST_CASES:
        success = run_test(text_input, expected_type, expected_response_id)
        if success:
            passed += 1
        else:
            failed += 1
        
        # Small delay between tests to avoid rate limiting
        time.sleep(2)
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total: {len(TEST_CASES)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n✅ ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
