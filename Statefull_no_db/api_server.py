from fastapi import FastAPI, HTTPException
from pydantic import BaseModel,Field
from typing import Optional
from typing import Annotated
import uvicorn
from src.graph import start_joke_generation, continue_workflow

# Create interrupt-based FastAPI app
app = FastAPI(
    title="Interrupt-Based Joke Generation API", 
    version="3.0.0",
    description="API with interrupt-based routing (NO persistence/DB)"
)

# Request models
class StartRequest(BaseModel):
    topic: str

class ContinueRequest(BaseModel):
    topic: str
    joke: Optional[str] = None
    explanation: Optional[str] = None
    rating: Optional[str] = None
    alternative: Optional[str] = None
    next_node: str
    status: str

class StateResponse(BaseModel):
    success: Annotated[bool,Field(..., description="Indicates if the request was successful")]
    state: Annotated[ContinueRequest,Field(..., description="Current state of the workflow")]
    completed: Annotated[bool,Field(..., description="Indicates if the workflow is completed")]
    message: Annotated[str,Field(..., description="Informational message about the workflow")]
    

@app.get("/")
def read_root():
    return {
        "message": "Interrupt-Based Joke Generation API is running!",
        "version": "3.0.0 (No DB - Interrupt-based)",
        "description": "State is returned after each node and sent back in continue endpoint",
        "endpoints": [
            "/health",
            "/start - Start joke generation (returns state + next_node)",
            "/continue - Continue with provided state (auto-routes based on next_node)"
        ],
        "nodes": [
            "generate_joke",
            "generate_explanation", 
            "generate_rating",
            "generate_alternative"
        ]
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "persistence": "None - Interrupt-based routing",
        "mode": "stateless"
    }

@app.post("/start",response_model = StateResponse,response_description="State after starting workflow")
def start_endpoint(request: StartRequest):
    try:
        print(f"API /start - topic: {request.topic}")
        result = start_joke_generation(request.topic)
        
        return {
            "success": True,
            "state": {
                "topic": result['topic'],
                "joke": result['joke'],
                "explanation": result['explanation'],
                "rating": result['rating'],
                "alternative": result['alternative'],
                "next_node": result['next_node'],
                "status": result['status']
            },
            "completed": False,
            "message": f"Node executed. Next node: {result['next_node']}. Send this state to /continue."
        }
    except Exception as e:
        print(f"API error in /start: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/continue",response_model= StateResponse,response_description="State after continuing workflow")
def continue_endpoint(request: ContinueRequest):
    try:
        # Convert request to state dict
        state = {
            "topic": request.topic,
            "joke": request.joke,
            "explanation": request.explanation,
            "rating": request.rating,
            "alternative": request.alternative,
            "next_node": request.next_node,
            "status": request.status
        }
        
        print(f"API /continue - routing to: {request.next_node}")
        result = continue_workflow(state)
        
        is_completed = result.get('next_node') == 'END'
        
        return {
            "success": True,
            "state": {
                "topic": result['topic'],
                "joke": result['joke'],
                "explanation": result['explanation'],
                "rating": result['rating'],
                "alternative": result['alternative'],
                "next_node": result['next_node'],
                "status": result['status']
            },
            "completed": is_completed,
            "message": result.get('message') if is_completed else f"Node executed. Next node: {result['next_node']}. Send this state to /continue again."
        }
    except Exception as e:
        print(f"API error in /continue: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
