"""
Data models and state definitions for the joke generation agent.
"""

from typing import TypedDict, Optional


class JokeState(TypedDict):
    """
    State definition for the joke generation workflow.
    
    Attributes:
        topic (str): The topic for which to generate a joke
        joke (str): The generated joke content
        explanation (str): The explanation of the joke
        rating (str): Rating of the joke with reasoning
        alternative (str): Alternative version of the joke
        next_node (str): Next node to route to
        status (str): Current status of the workflow
    """
    topic: str
    joke: Optional[str]
    explanation: Optional[str]
    rating: Optional[str]
    alternative: Optional[str]
    next_node: str
    status: str
