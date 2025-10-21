"""Stateful workflow for joke generation with persistence."""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from .models import JokeState
from .core import generate_joke, generate_explanation
import os

# Database file for persistent storage
DB_PATH = "checkpoints.db"

def create_workflow():
    """Create and return the stateful joke workflow with SQLite persistence."""
    print("Setting up stateful joke generation workflow")
    
    # Create the state graph
    graph = StateGraph(JokeState)
    
    # Add nodes
    graph.add_node('generate_joke', generate_joke)
    graph.add_node('generate_explanation', generate_explanation)
    
    # Add edges
    graph.add_edge(START, 'generate_joke')
    graph.add_edge('generate_joke', 'generate_explanation')
    graph.add_edge('generate_explanation', END)
    
    # Use SQLite checkpointer for persistent storage
    checkpointer = SqliteSaver.from_conn_string(DB_PATH)
    
    # Compile the workflow with interrupt AFTER joke generation
    # This means the workflow will pause after generate_joke completes
    workflow = graph.compile(
        checkpointer=checkpointer,
        interrupt_after=['generate_joke']
    )
    print("Workflow setup completed with SQLite persistence")
    
    return workflow

# Create global workflow instance
workflow = create_workflow()

def start_joke_generation(topic: str, thread_id: str):
    """
    Start joke generation workflow. Returns after joke is generated.
    
    Args:
        topic: The topic for the joke
        thread_id: Unique thread identifier for this conversation
        
    Returns:
        dict with joke and status
    """
    try:
        config = {"configurable": {"thread_id": thread_id}}
        print(f"Starting joke generation for topic: {topic}, thread: {thread_id}")
        
        # Initial state
        initial_state = {
            'topic': topic,
            'joke': None,
            'explanation': None,
            'status': 'started'
        }
        
        # Invoke workflow - it will stop after generate_joke due to interrupt
        result = workflow.invoke(initial_state, config=config)
        print(f"Joke generation completed for thread: {thread_id}")
        
        return {
            'topic': result.get('topic'),
            'joke': result.get('joke'),
            'status': result.get('status', 'joke_generated'),
            'thread_id': thread_id
        }
    except Exception as e:
        print(f"Error in start_joke_generation: {str(e)}")
        raise


def continue_with_explanation(thread_id: str):
    """
    Continue workflow to generate explanation for an existing joke.
    
    Args:
        thread_id: The thread identifier to continue
        
    Returns:
        dict with explanation and status
    """
    try:
        config = {"configurable": {"thread_id": thread_id}}
        print(f"Continuing workflow for thread: {thread_id}")
        
        # Get current state to verify it exists
        current_state = workflow.get_state(config)
        
        if not current_state or not current_state.values:
            raise ValueError(f"No active workflow found for thread_id: {thread_id}")
        
        # Check if joke exists
        if not current_state.values.get('joke'):
            raise ValueError(f"No joke found for thread_id: {thread_id}. Start workflow first.")
        
        # Continue from where we left off (None means continue with no new input)
        result = workflow.invoke(None, config=config)
        print(f"Explanation generated for thread: {thread_id}")
        
        return {
            'topic': result.get('topic'),
            'joke': result.get('joke'),
            'explanation': result.get('explanation'),
            'status': result.get('status', 'completed'),
            'thread_id': thread_id
        }
    except Exception as e:
        print(f"Error in continue_with_explanation: {str(e)}")
        raise


def get_thread_status(thread_id: str):
    """
    Get current status of a thread.
    
    Args:
        thread_id: The thread identifier to check
        
    Returns:
        dict with current state information
    """
    try:
        config = {"configurable": {"thread_id": thread_id}}
        state = workflow.get_state(config)
        
        if not state or not state.values:
            return {
                'exists': False,
                'message': f"No workflow found for thread_id: {thread_id}"
            }
        
        return {
            'exists': True,
            'thread_id': thread_id,
            'status': state.values.get('status', 'unknown'),
            'topic': state.values.get('topic'),
            'has_joke': bool(state.values.get('joke')),
            'has_explanation': bool(state.values.get('explanation')),
            'next_node': state.next[0] if state.next else None
        }
    except Exception as e:
        print(f"Error in get_thread_status: {str(e)}")
        raise
