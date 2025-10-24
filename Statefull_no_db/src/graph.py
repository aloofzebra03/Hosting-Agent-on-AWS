"""Stateful workflow for joke generation WITHOUT persistence - interrupt-based routing."""

from langgraph.graph import StateGraph, START, END
from .models import JokeState
from .core import router_node, generate_joke, generate_explanation, generate_rating, generate_alternative

def route_from_start(state):
    next_node = state.get("next_node", "generate_joke")
    print(f"Routing from START to: {next_node}")
    return next_node

def create_workflow():
    print("Setting up interrupt-based joke generation workflow (NO DB)")
    
    # Create the state graph
    graph = StateGraph(JokeState)
    
    # Add router node
    graph.add_node('router', router_node)
    
    # Add all processing nodes
    graph.add_node('generate_joke', generate_joke)
    graph.add_node('generate_explanation', generate_explanation)
    graph.add_node('generate_rating', generate_rating)
    graph.add_node('generate_alternative', generate_alternative)
    
    # Connect START to router
    graph.add_edge(START, 'router')
    
    # Add conditional edges from router to all nodes based on next_node in state
    graph.add_conditional_edges(
        'router',
        route_from_start,
        {
            'generate_joke': 'generate_joke',
            'generate_explanation': 'generate_explanation',
            'generate_rating': 'generate_rating',
            'generate_alternative': 'generate_alternative',
            'END': END
        }
    )
    
    # All nodes go back to router for next routing decision
    graph.add_edge('generate_joke', 'router')
    graph.add_edge('generate_explanation', 'router')
    graph.add_edge('generate_rating', 'router')
    graph.add_edge('generate_alternative', 'router')
    
    # Compile the workflow with interrupt AFTER each node
    workflow = graph.compile(
        interrupt_after=['generate_joke', 'generate_explanation', 'generate_rating', 'generate_alternative']
    )
    print("Workflow setup completed WITHOUT persistence - interrupt-based routing")
    
    return workflow
# Create global workflow instance
workflow = create_workflow()

def start_joke_generation(topic: str):
    try:
        print(f"Starting joke generation for topic: {topic}")
        
        # Initial state - next_node tells router where to start
        initial_state = {
            'topic': topic,
            'joke': None,
            'explanation': None,
            'rating': None,
            'alternative': None,
            'next_node': 'generate_joke',  # Start with joke generation
            'status': 'started'
        }
        
        # Invoke workflow - it will execute first node and interrupt
        result = workflow.invoke(initial_state)
        print(f"First node completed, returning state")
        
        return {
            'topic': result.get('topic'),
            'joke': result.get('joke'),
            'explanation': result.get('explanation'),
            'rating': result.get('rating'),
            'alternative': result.get('alternative'),
            'next_node': result.get('next_node'),
            'status': result.get('status')
        }
    except Exception as e:
        print(f"Error in start_joke_generation: {str(e)}")
        raise


def continue_workflow(state: dict):
    try:
        next_node = state.get('next_node', 'END')
        print(f"Continuing workflow - routing to: {next_node}")
        
        if next_node == 'END':
            print("Workflow completed - no more nodes to execute")
            return {
                **state,
                'status': 'completed',
                'message': 'Workflow completed successfully'
            }
        
        # Continue workflow with the provided state
        result = workflow.invoke(state)
        print(f"Node {next_node} completed")
        
        return {
            'topic': result.get('topic'),
            'joke': result.get('joke'),
            'explanation': result.get('explanation'),
            'rating': result.get('rating'),
            'alternative': result.get('alternative'),
            'next_node': result.get('next_node'),
            'status': result.get('status')
        }
    except Exception as e:
        print(f"Error in continue_workflow: {str(e)}")
        raise
