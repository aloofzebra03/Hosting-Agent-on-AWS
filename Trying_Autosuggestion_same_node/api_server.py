from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from src.graph import start_joke_generation, continue_with_explanation, get_thread_status, handle_user_action

# Create stateful FastAPI app
app = FastAPI(
    title="Stateful Joke Generation API with Autosuggestions", 
    version="3.0.0",
    description="API with persistent state management, interrupts, and smart autosuggestions"
)

# Request models
class StartRequest(BaseModel):
    topic: str
    thread_id: str

class ContinueRequest(BaseModel):
    thread_id: str

class StatusRequest(BaseModel):
    thread_id: str

class ActionRequest(BaseModel):
    thread_id: str
    action: str  # The autosuggestion action ID selected by user

@app.get("/")
def read_root():
    return {
        "message": "Stateful Joke Generation API with Autosuggestions is running!",
        "version": "3.0.0",
        "endpoints": [
            "/health",
            "/start - Start joke generation",
            "/continue - Generate explanation and autosuggestions",
            "/action - Handle user's selected autosuggestion",
            "/status - Check thread status"
        ]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "persistence": "InMemory", "features": ["interrupts", "autosuggestions"]}

@app.post("/start")
def start_endpoint(request: StartRequest):
    try:
        print(f"API /start - topic: {request.topic}, thread: {request.thread_id}")
        result = start_joke_generation(request.topic, request.thread_id)
        
        return {
            "success": True,
            "thread_id": result['thread_id'],
            "topic": result['topic'],
            "joke": result['joke'],
            "status": result['status'],
            "message": "Joke generated. Call /continue to get explanation."
        }
    except Exception as e:
        print(f"API error in /start: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/continue")
def continue_endpoint(request: ContinueRequest):
    try:
        print(f"API /continue - thread: {request.thread_id}")
        result = continue_with_explanation(request.thread_id)
        
        return {
            "success": True,
            "thread_id": result['thread_id'],
            "topic": result['topic'],
            "joke": result['joke'],
            "explanation": result['explanation'],
            "autosuggestions": result.get('autosuggestions', []),
            "status": result['status'],
            "message": "Explanation and autosuggestions generated. Use /action to select an autosuggestion."
        }
    except ValueError as e:
        print(f"API validation error in /continue (Invalid thread id): {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"API error in /continue: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/action")
def action_endpoint(request: ActionRequest):
    """
    Handle user's selected autosuggestion action.
    
    Valid actions:
    - another_joke: Generate a new joke on the same topic
    - simpler_explanation: Simplify the explanation
    - make_funnier: Enhance the joke
    - similar_joke: Generate a similar style joke
    - new_topic: Request a new topic (returns completed status)
    """
    try:
        print(f"API /action - thread: {request.thread_id}, action: {request.action}")
        result = handle_user_action(request.thread_id, request.action)
        
        response = {
            "success": True,
            "thread_id": result['thread_id'],
            "topic": result['topic'],
            "joke": result['joke'],
            "explanation": result.get('explanation'),
            "autosuggestions": result.get('autosuggestions', []),
            "status": result['status'],
            "action_performed": result['action_performed']
        }
        
        # Add appropriate message based on status
        if result['status'] in ['joke_regenerated', 'joke_enhanced', 'similar_joke_generated']:
            response["message"] = "New joke generated! Call /continue to get explanation and new suggestions."
        elif result['status'] == 'explanation_simplified':
            response["message"] = "Explanation simplified with new autosuggestions! Select another action or call /start for a new topic."
        elif result['status'] == 'new_topic_requested':
            response["message"] = "Session completed. Call /start with a new topic."
        else:
            response["message"] = "Action completed."
            response["message"] = "Session completed. Call /start with a new topic."
        else:
            response["message"] = "Action completed."
        
        return response
        
    except ValueError as e:
        print(f"API validation error in /action: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"API error in /action: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/status")
def status_endpoint(request: StatusRequest):
    try:
        print(f"API /status - thread: {request.thread_id}")
        result = get_thread_status(request.thread_id)
        
        if not result.get('exists'):
            raise HTTPException(status_code=404, detail=result.get('message'))
        
        return {
            "success": True,
            **result
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"API error in /status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# if __name__ == "__main__":
#     print("Starting Stateful Joke Generation API server on port 8000...")
#     print("Endpoints available:")
#     print("  GET  /health - Health check")
#     print("  POST /start - Start joke generation")
#     print("  POST /continue - Generate explanation")
#     print("  POST /status - Check thread status")
#     uvicorn.run(app, host="0.0.0.0", port=8000)
