"""Simple joke generation functions."""

from .config import get_llm

def generate_joke(state):
    """Generate a joke based on the topic."""
    try:
        llm = get_llm()
        topic = state.get("topic", "general")
        prompt = f'Generate a funny joke about {topic}'
        
        print(f"Generating joke for topic: {topic}")
        response = llm.invoke(prompt).content
        print("Joke generated successfully")
        
        return {'joke': response}
        
    except Exception as e:
        print(f"Error generating joke: {str(e)}")
        return {'joke': f"Sorry, I couldn't generate a joke about {topic} right now."}


def generate_explanation(state):
    """Generate an explanation for the joke."""
    try:
        llm = get_llm()
        joke = state.get("joke", "")
        prompt = f'Explain why this joke is funny: {joke}'
        
        print("Generating explanation for joke")
        response = llm.invoke(prompt).content
        print("Explanation generated successfully")
        
        return {'explanation': response}
        
    except Exception as e:
        print(f"Error generating explanation: {str(e)}")
        return {'explanation': "Sorry, I couldn't generate an explanation for this joke."}
