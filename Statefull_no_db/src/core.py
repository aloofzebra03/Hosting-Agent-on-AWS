from .config import get_llm

def router_node(state):
    next_node = state.get("next_node", "generate_joke")
    print(f"Router: Routing to {next_node}")
    return state

def generate_joke(state):
    """Generate a joke based on the topic."""
    try:
        llm = get_llm()
        topic = state.get("topic", "general")
        prompt = f'Generate a funny joke about {topic}'
        
        print(f"Generating joke for topic: {topic}")
        response = llm.invoke(prompt).content
        print("Joke generated successfully")
        
        return {
            'joke': response,
            'next_node': 'generate_explanation',
            'status': 'joke_generated'
        }
        
    except Exception as e:
        print(f"Error generating joke: {str(e)}")
        return {
            'joke': f"Sorry, I couldn't generate a joke about {topic} right now.",
            'next_node': 'generate_explanation',
            'status': 'error'
        }


def generate_explanation(state):
    try:
        llm = get_llm()
        joke = state.get("joke", "")
        prompt = f'Explain why this joke is funny: {joke}'
        
        print("Generating explanation for joke")
        response = llm.invoke(prompt).content
        print("Explanation generated successfully")
        
        return {
            'explanation': response,
            'next_node': 'generate_rating',
            'status': 'explanation_generated'
        }
        
    except Exception as e:
        print(f"Error generating explanation: {str(e)}")
        return {
            'explanation': "Sorry, I couldn't generate an explanation for this joke.",
            'next_node': 'generate_rating',
            'status': 'error'
        }


def generate_rating(state):
    """Rate the joke on a scale of 1-10 with reasoning."""
    try:
        llm = get_llm()
        joke = state.get("joke", "")
        prompt = f'Rate this joke on a scale of 1-10 and provide reasoning for your rating: {joke}'
        
        print("Generating rating for joke")
        response = llm.invoke(prompt).content
        print("Rating generated successfully")
        
        return {
            'rating': response,
            'next_node': 'generate_alternative',
            'status': 'rating_generated'
        }
        
    except Exception as e:
        print(f"Error generating rating: {str(e)}")
        return {
            'rating': "Sorry, I couldn't generate a rating for this joke.",
            'next_node': 'generate_alternative',
            'status': 'error'
        }


def generate_alternative(state):
    """Generate an alternative version of the joke."""
    try:
        llm = get_llm()
        joke = state.get("joke", "")
        topic = state.get("topic", "general")
        prompt = f'Generate an alternative version of this joke about {topic}: {joke}'
        
        print("Generating alternative version of joke")
        response = llm.invoke(prompt).content
        print("Alternative generated successfully")
        
        return {
            'alternative': response,
            'next_node': 'END',
            'status': 'completed'
        }
        
    except Exception as e:
        print(f"Error generating alternative: {str(e)}")
        return {
            'alternative': "Sorry, I couldn't generate an alternative joke.",
            'next_node': 'END',
            'status': 'error'
        }
