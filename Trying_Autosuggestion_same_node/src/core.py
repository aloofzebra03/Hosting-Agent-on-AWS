from .config import get_llm
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from typing import List


# Pydantic models for structured outputs
class JokeOutput(BaseModel):
    """Model for joke generation output"""
    joke: str = Field(description="A funny joke about the given topic")


class ExplanationWithSuggestions(BaseModel):
    """Model for combined explanation and autosuggestions output"""
    explanation: str = Field(description="An explanation of why the joke is funny")
    selected_action_ids: List[str] = Field(
        description="List of 3-4 selected action IDs in order of relevance for user interaction",
        min_items=3,
        max_items=4
    )


def generate_joke(state):
    try:
        llm = get_llm()
        topic = state.get("topic", "general")
        
        # Set up output parser
        parser = PydanticOutputParser(pydantic_object=JokeOutput)
        
        prompt = f"""Generate a funny joke about {topic}.

{parser.get_format_instructions()}"""
        
        print(f"Generating joke for topic: {topic}")
        response = llm.invoke(prompt)
        parsed_output = parser.parse(response.content)
        print("Joke generated successfully")
        
        return {
            'joke': parsed_output.joke,
            'status': 'joke_generated'
        }
        
    except Exception as e:
        print(f"Error generating joke: {str(e)}")
        return {
            'joke': f"Sorry, I couldn't generate a joke about {topic} right now.",
            'status': 'error'
        }


def generate_explanation_with_suggestions(state):
    """
    Generate both explanation and autosuggestions in a single LLM call.
    This is more efficient and ensures contextual coherence between explanation and suggestions.
    """
    try:
        llm = get_llm()
        topic = state.get("topic", "general")
        joke = state.get("joke", "")
        
        # Define available actions with descriptions
        available_actions = [
            {
                "id": "another_joke",
                "label": "Tell me another joke about this topic",
                "description": "Generate a completely new joke about the same topic"
            },
            {
                "id": "simpler_explanation",
                "label": "Explain this in simpler words",
                "description": "Rephrase the explanation to be easier to understand"
            },
            {
                "id": "new_topic",
                "label": "Tell me a joke about a different topic",
                "description": "Start fresh with a new topic"
            },
            {
                "id": "make_funnier",
                "label": "Make it funnier",
                "description": "Enhance the joke to make it more humorous"
            },
            {
                "id": "similar_joke",
                "label": "Tell me a similar joke",
                "description": "Generate a joke with similar style or theme"
            }
        ]
        
        # Set up output parser for combined output
        parser = PydanticOutputParser(pydantic_object=ExplanationWithSuggestions)
        
        # Create action list string
        actions_str = "\n".join([f"- {action['id']}: {action['description']}" for action in available_actions])
        
        prompt = f"""Given this joke about "{topic}": "{joke}"

Task 1: Explain why this joke is funny in a clear and engaging way.

Task 2: From the following actions, select the 3-4 most relevant and useful suggestions for the user based on the joke and explanation:
{actions_str}

{parser.get_format_instructions()}

Provide both the explanation and the selected action IDs that would be most helpful for continued user interaction."""
        
        print("Generating explanation and autosuggestions together...")
        response = llm.invoke(prompt)
        
        try:
            parsed_output = parser.parse(response.content)
            explanation = parsed_output.explanation
            selected_ids = parsed_output.selected_action_ids
            print(f"Explanation generated, LLM selected actions: {selected_ids}")
        except Exception as parse_error:
            # Fallback: use default values if parsing fails
            print(f"Could not parse LLM response ({parse_error}), using fallback")
            explanation = "This joke is funny!"
            selected_ids = ["another_joke", "simpler_explanation", "make_funnier"]
        
        # Filter available actions based on LLM selection
        suggestions = [action for action in available_actions if action["id"] in selected_ids]
        
        # If no valid suggestions, use defaults
        if not suggestions:
            suggestions = available_actions[:3]
        
        print(f"Generated explanation and {len(suggestions)} autosuggestions")
        
        return {
            'explanation': explanation,
            'autosuggestions': suggestions,
            'status': 'awaiting_action'
        }
        
    except Exception as e:
        print(f"Error generating explanation and autosuggestions: {str(e)}")
        # Return defaults on error
        return {
            'explanation': "Sorry, I couldn't generate an explanation for this joke.",
            'autosuggestions': [
                {"id": "another_joke", "label": "Tell me another joke about this topic"},
                {"id": "simpler_explanation", "label": "Explain this in simpler words"},
                {"id": "new_topic", "label": "Tell me a joke about a different topic"}
            ],
            'status': 'awaiting_action'
        }


def handle_autosuggestion(state):
    """
    Handle the selected autosuggestion action.
    Routes to appropriate function based on user's choice.
    Uses Pydantic parsers for structured outputs.
    """
    try:
        llm = get_llm()
        action = state.get("selected_action", "")
        topic = state.get("topic", "general")
        joke = state.get("joke", "")
        explanation = state.get("explanation", "")
        
        print(f"Handling autosuggestion action: {action}")
        
        if action == "another_joke":
            # Generate a new joke on the same topic
            parser = PydanticOutputParser(pydantic_object=JokeOutput)
            prompt = f"""Generate a different funny joke about {topic}. Make it unique and different from this one: {joke}

{parser.get_format_instructions()}"""
            
            response = llm.invoke(prompt)
            parsed_output = parser.parse(response.content)
            
            return {
                'joke': parsed_output.joke,
                'explanation': None,  # Clear explanation for new joke
                'autosuggestions': None,  # Clear suggestions
                'status': 'joke_regenerated'
            }
            
        elif action == "simpler_explanation":
            # Simplify the explanation - use the combined model
            parser = PydanticOutputParser(pydantic_object=ExplanationWithSuggestions)
            
            # Get available actions again for regenerating suggestions
            available_actions = [
                {"id": "another_joke", "label": "Tell me another joke about this topic"},
                {"id": "simpler_explanation", "label": "Explain this in simpler words"},
                {"id": "new_topic", "label": "Tell me a joke about a different topic"},
                {"id": "make_funnier", "label": "Make it funnier"},
                {"id": "similar_joke", "label": "Tell me a similar joke"}
            ]
            
            actions_str = "\n".join([f"- {action['id']}" for action in available_actions])
            
            prompt = f"""Rephrase this explanation in very simple, easy-to-understand words suitable for a child: {explanation}

Also, select 3-4 relevant action IDs from: {actions_str}

{parser.get_format_instructions()}"""
            
            response = llm.invoke(prompt)
            parsed_output = parser.parse(response.content)
            
            # Filter available actions
            suggestions = [action for action in available_actions if action["id"] in parsed_output.selected_action_ids]
            if not suggestions:
                suggestions = available_actions[:3]
            
            return {
                'explanation': parsed_output.explanation,
                'autosuggestions': suggestions,
                'status': 'explanation_simplified'
            }
            
        elif action == "make_funnier":
            # Enhance the joke
            parser = PydanticOutputParser(pydantic_object=JokeOutput)
            prompt = f"""Make this joke funnier and more entertaining while keeping the same topic ({topic}): {joke}

{parser.get_format_instructions()}"""
            
            response = llm.invoke(prompt)
            parsed_output = parser.parse(response.content)
            
            return {
                'joke': parsed_output.joke,
                'explanation': None,  # Clear explanation since joke changed
                'autosuggestions': None,
                'status': 'joke_enhanced'
            }
            
        elif action == "similar_joke":
            # Generate similar style joke
            parser = PydanticOutputParser(pydantic_object=JokeOutput)
            prompt = f"""Generate a joke similar in style and humor to this one, but with different content: {joke}

{parser.get_format_instructions()}"""
            
            response = llm.invoke(prompt)
            parsed_output = parser.parse(response.content)
            
            return {
                'joke': parsed_output.joke,
                'explanation': None,
                'autosuggestions': None,
                'status': 'similar_joke_generated'
            }
            
        elif action == "new_topic":
            # Signal that user wants a new topic (handled by API layer)
            return {
                'status': 'new_topic_requested'
            }
        
        else:
            print(f"Unknown action: {action}")
            return {
                'status': 'error',
                'error': f'Unknown action: {action}'
            }
            
    except Exception as e:
        print(f"Error handling autosuggestion: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }
