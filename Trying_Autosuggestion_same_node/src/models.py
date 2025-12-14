"""
Data models and state definitions for the joke generation agent.
"""

from typing import TypedDict, Optional, List


class JokeState(TypedDict):
    """
    State definition for the joke generation workflow.
    
    Attributes:
        topic (str): The topic for which to generate a joke
        joke (str): The generated joke content
        explanation (str): The explanation of the joke
        autosuggestions (List[dict]): List of suggested actions user can take
        selected_action (str): The action selected by user from autosuggestions
        status (str): Current status of the workflow
    """
    topic: str
    joke: Optional[str]
    explanation: Optional[str]
    autosuggestions: Optional[List[dict]]
    selected_action: Optional[str]
    status: str  # "started", "joke_generated", "explanation_generated", "awaiting_action", "completed"
