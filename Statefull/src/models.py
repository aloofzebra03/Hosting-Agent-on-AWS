"""
Data models and state definitions for the joke generation agent.
"""

from typing import TypedDict


class JokeState(TypedDict):
    """
    State definition for the joke generation workflow.
    
    Attributes:
        topic (str): The topic for which to generate a joke
        joke (str): The generated joke content
        explanation (str): The explanation of the joke
    """
    topic: str
    joke: str
    explanation: str
