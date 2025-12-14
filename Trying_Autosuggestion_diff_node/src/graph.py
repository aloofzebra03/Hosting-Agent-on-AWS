from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from .models import JokeState
from .core import generate_joke, generate_explanation, generate_autosuggestions, handle_autosuggestion

def create_workflow():
    print("Setting up stateful joke generation workflow with autosuggestions")
    
    # Create the state graph
    graph = StateGraph(JokeState)
    
    # Add nodes
    graph.add_node('generate_joke', generate_joke)
    graph.add_node('generate_explanation', generate_explanation)
    graph.add_node('generate_autosuggestions', generate_autosuggestions)
    graph.add_node('handle_autosuggestion', handle_autosuggestion)
    
    # Add edges
    graph.add_edge(START, 'generate_joke')
    graph.add_edge('generate_joke', 'generate_explanation')
    graph.add_edge('generate_explanation', 'generate_autosuggestions')
    
    # After generating autosuggestions, route to handler
    # The interrupt after 'generate_autosuggestions' will pause here
    # User calls /action which resumes and goes to handle_autosuggestion
    graph.add_conditional_edges(
        'generate_autosuggestions',
        lambda state: 'handle_autosuggestion',  # Always route to handler
        {'handle_autosuggestion': 'handle_autosuggestion'}
    )
    
    # Add conditional routing from handle_autosuggestion
    def route_after_action(state):
        """Route based on the action result"""
        status = state.get('status', '')
        
        # If joke was regenerated/enhanced, go back to explanation
        if status in ['joke_regenerated', 'joke_enhanced', 'similar_joke_generated']:
            return 'generate_explanation'
        # For all other cases (explanation_simplified, new_topic_requested, etc), end workflow
        else:
            return END
    
    graph.add_conditional_edges(
        'handle_autosuggestion',
        route_after_action,
        {
            'generate_explanation': 'generate_explanation',
            END: END
        }
    )
    
    # Create in-memory checkpointer
    checkpointer = InMemorySaver()
    print("InMemorySaver checkpointer initialized")
    
    workflow = graph.compile(
        checkpointer=checkpointer,
        interrupt_after=['generate_joke', 'generate_autosuggestions', 'handle_autosuggestion']  # Interrupt after all key nodes
    )
    print("Workflow setup completed with in-memory persistence and autosuggestions")
    
    return workflow
# Create global workflow instance
workflow = create_workflow()

def start_joke_generation(topic: str, thread_id: str):
    try:
        config = {"configurable": {"thread_id": thread_id}}
        print(f"Starting joke generation for topic: {topic}, thread: {thread_id}")
        
        # Initial state
        initial_state = {
            'topic': topic,
            'joke': None,
            'explanation': None,
            'autosuggestions': None,
            'selected_action': None,
            'status': 'started'
        }
        
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
        print(f"Explanation and autosuggestions generated for thread: {thread_id}")
        
        return {
            'topic': result.get('topic'),
            'joke': result.get('joke'),
            'explanation': result.get('explanation'),
            'autosuggestions': result.get('autosuggestions'),
            'status': result.get('status', 'awaiting_action'),
            'thread_id': thread_id
        }
    except Exception as e:
        print(f"Error in continue_with_explanation: {str(e)}")
        raise


def handle_user_action(thread_id: str, action: str):
    """
    Handle user's selected autosuggestion action.
    
    Args:
        thread_id: The thread identifier
        action: The action ID selected by user (e.g., 'another_joke', 'simpler_explanation')
    """
    try:
        config = {"configurable": {"thread_id": thread_id}}
        print(f"Handling user action '{action}' for thread: {thread_id}")
        
        # Get current state
        current_state = workflow.get_state(config)
        
        if not current_state or not current_state.values:
            raise ValueError(f"No active workflow found for thread_id: {thread_id}")
        
        # Update state with selected action
        updated_state = {
            **current_state.values,
            'selected_action': action
        }
        
        # Continue workflow with the action
        result = workflow.invoke(updated_state, config=config)
        print(f"Action '{action}' completed for thread: {thread_id}")
        
        return {
            'topic': result.get('topic'),
            'joke': result.get('joke'),
            'explanation': result.get('explanation'),
            'autosuggestions': result.get('autosuggestions'),
            'status': result.get('status'),
            'thread_id': thread_id,
            'action_performed': action
        }
    except Exception as e:
        print(f"Error in handle_user_action: {str(e)}")
        raise


def get_thread_status(thread_id: str):
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
            'has_autosuggestions': bool(state.values.get('autosuggestions')),
            'autosuggestions': state.values.get('autosuggestions'),
            'next_node': state.next[0] if state.next else None
        }
    except Exception as e:
        print(f"Error in get_thread_status: {str(e)}")
        raise
