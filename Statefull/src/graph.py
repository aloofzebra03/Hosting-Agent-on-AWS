"""Simple workflow for joke generation."""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from .models import JokeState
from .core import generate_joke, generate_explanation

# Create simple workflow
def create_workflow():
    """Create and return the joke workflow."""
    print("Setting up joke generation workflow")
    
    # Create the state graph
    graph = StateGraph(JokeState)
    
    # Add nodes
    graph.add_node('generate_joke', generate_joke)
    graph.add_node('generate_explanation', generate_explanation)
    
    # Add edges
    graph.add_edge(START, 'generate_joke')
    graph.add_edge('generate_joke', 'generate_explanation')
    graph.add_edge('generate_explanation', END)
    
    # Use simple in-memory checkpointer
    checkpointer = InMemorySaver()
    
    # Compile the workflow
    workflow = graph.compile(checkpointer=checkpointer)
    print("Workflow setup completed")
    
    return workflow

# Create global workflow instance
workflow = create_workflow()

def generate_joke_with_explanation(topic, thread_id="default"):
    """Simple function to generate joke and explanation."""
    try:
        config = {"configurable": {"thread_id": thread_id}}
        print(f"Generating joke for topic: {topic}")
        result = workflow.invoke({'topic': topic}, config=config)
        print("Workflow completed successfully")
        return result
    except Exception as e:
        print(f"Error in workflow: {str(e)}")
        return {
            'topic': topic,
            'joke': f"Sorry, couldn't generate joke about {topic}",
            'explanation': "Error occurred during generation"
        }
