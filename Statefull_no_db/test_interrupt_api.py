"""
Test script for the interrupt-based API.
Demonstrates how to use the new interrupt-based routing system.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_interrupt_based_workflow():
    print("=" * 60)
    print("Testing Interrupt-Based Workflow")
    print("=" * 60)
    
    # Step 1: Start the workflow
    print("\n1. Starting workflow with /start endpoint...")
    start_response = requests.post(
        f"{BASE_URL}/start",
        json={"topic": "programming"}
    )
    
    print(f"Status Code: {start_response.status_code}")
    start_data = start_response.json()
    print(f"Response: {json.dumps(start_data, indent=2)}")
    
    # Get the state from response
    state = start_data["state"]
    print(f"\n✓ Joke generated: {state['joke'][:50]}...")
    print(f"✓ Next node: {state['next_node']}")
    print(f"✓ Status: {state['status']}")
    
    # Step 2: Continue with the state - generate explanation
    print("\n2. Continuing workflow - generating explanation...")
    continue_response = requests.post(
        f"{BASE_URL}/continue",
        json=state
    )
    
    continue_data = continue_response.json()
    state = continue_data["state"]
    print(f"✓ Explanation generated: {state['explanation'][:50]}...")
    print(f"✓ Next node: {state['next_node']}")
    print(f"✓ Status: {state['status']}")
    
    # Step 3: Continue with the state - generate rating
    print("\n3. Continuing workflow - generating rating...")
    continue_response = requests.post(
        f"{BASE_URL}/continue",
        json=state
    )
    
    continue_data = continue_response.json()
    state = continue_data["state"]
    print(f"✓ Rating generated: {state['rating'][:50]}...")
    print(f"✓ Next node: {state['next_node']}")
    print(f"✓ Status: {state['status']}")
    
    # Step 4: Continue with the state - generate alternative
    print("\n4. Continuing workflow - generating alternative...")
    continue_response = requests.post(
        f"{BASE_URL}/continue",
        json=state
    )
    
    continue_data = continue_response.json()
    state = continue_data["state"]
    print(f"✓ Alternative generated: {state['alternative'][:50]}...")
    print(f"✓ Next node: {state['next_node']}")
    print(f"✓ Status: {state['status']}")
    print(f"✓ Workflow completed: {continue_data['completed']}")
    
    # Final results
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"\nTopic: {state['topic']}")
    print(f"\n1. Joke:\n{state['joke']}")
    print(f"\n2. Explanation:\n{state['explanation']}")
    print(f"\n3. Rating:\n{state['rating']}")
    print(f"\n4. Alternative:\n{state['alternative']}")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        # Check if server is running
        health = requests.get(f"{BASE_URL}/health")
        print(f"Server Health: {health.json()}")
        
        # Run the test
        test_interrupt_based_workflow()
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to the API server.")
        print("Please start the server first with: uvicorn api_server:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
