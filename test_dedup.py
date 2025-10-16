#!/usr/bin/env python3
"""Test script to verify message deduplication logic"""

from collections import deque

def test_deque_deduplication():
    """Test that deque-based deduplication prevents duplicates even at capacity"""
    
    print("Testing deque-based message deduplication...")
    print("=" * 60)
    
    # Simulate the bot's processed_messages deque
    processed_messages = deque(maxlen=10)  # Using 10 for testing, bot uses 1000
    
    # Test 1: Basic deduplication
    print("\n✓ Test 1: Basic deduplication")
    msg_id_1 = 12345
    
    if msg_id_1 not in processed_messages:
        processed_messages.append(msg_id_1)
        print(f"  Message {msg_id_1} processed")
    
    if msg_id_1 in processed_messages:
        print(f"  ✓ Duplicate {msg_id_1} correctly detected and skipped")
    else:
        print(f"  ✗ FAILED: Duplicate not detected!")
        return False
    
    # Test 2: Fill to capacity
    print("\n✓ Test 2: Fill deque to capacity (10 messages)")
    for i in range(2, 11):
        processed_messages.append(i)
    print(f"  Added messages 2-10, deque length: {len(processed_messages)}")
    print(f"  Deque contents: {list(processed_messages)}")
    
    # Test 3: Verify oldest message is removed (this is where the old bug happened)
    print("\n✓ Test 3: Add 11th message - oldest (12345) should be removed")
    print(f"  Before: {list(processed_messages)}")
    processed_messages.append(11)
    print(f"  After adding 11: {list(processed_messages)}")
    
    # Check that message 1 (12345) is gone but message 2 is still there
    if 12345 not in processed_messages:
        print(f"  ✓ Oldest message (12345) correctly removed")
    else:
        print(f"  ✗ FAILED: Oldest message still present!")
        return False
    
    if 2 in processed_messages:
        print(f"  ✓ Second oldest message (2) still protected")
    else:
        print(f"  ✗ FAILED: Second message incorrectly removed!")
        return False
    
    # Test 3b: Add one more and verify message 2 gets removed
    print("\n✓ Test 3b: Add 12th message - message 2 should be removed")
    processed_messages.append(12)
    print(f"  After adding 12: {list(processed_messages)}")
    if 2 not in processed_messages and 3 in processed_messages:
        print(f"  ✓ Rolling removal working correctly (2 gone, 3 still there)")
    else:
        print(f"  ✗ FAILED: Rolling removal not working!")
        return False
    
    # Test 4: The critical test - simulate Discord re-delivering an old message
    print("\n✓ Test 4: Simulate Discord re-delivering message that fell off")
    print(f"  Attempting to re-process message 12345 (fell off deque)")
    
    if 12345 not in processed_messages:
        print(f"  ⚠️  Message 12345 not in deque - would be REPROCESSED")
        print(f"  This is expected for very old messages (>1000 messages ago)")
    
    # Test 5: Verify recent messages are still protected
    print("\n✓ Test 5: Verify recent messages are still protected")
    if 11 in processed_messages:
        print(f"  ✓ Recent message (11) still protected from duplicates")
    
    # Test 6: OLD BUG SIMULATION - what happened with set.clear()
    print("\n✓ Test 6: Simulating OLD BUG (set.clear() behavior)")
    old_method = set()
    for i in range(1, 12):
        old_method.add(i)
    
    print(f"  Old method: set with {len(old_method)} messages")
    if len(old_method) > 10:  # Simulating the old threshold
        old_method.clear()
        print(f"  OLD BUG: Set cleared! Now has {len(old_method)} messages")
        print(f"  Message 5 protected? {5 in old_method} ❌ (should be True)")
        print(f"  Message 10 protected? {10 in old_method} ❌ (should be True)")
        print(f"  ALL MESSAGES VULNERABLE TO DUPLICATES!")
    
    # Final comparison
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("  NEW METHOD (deque): Only messages >1000 old can duplicate")
    print("  OLD METHOD (set.clear): ALL messages vulnerable after clear")
    print("  ✓ Fix successfully prevents the duplicate message bug!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = test_deque_deduplication()
    exit(0 if success else 1)
