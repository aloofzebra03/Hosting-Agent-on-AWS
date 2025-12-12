from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from src.graph import start_joke_generation, continue_with_explanation, get_thread_status

# Create stateful FastAPI app
app = FastAPI(
    title="Stateful Joke Generation API", 
    version="2.0.0",
    description="API with persistent state management for joke generation"
)

# Request models
class StartRequest(BaseModel):
    topic: str
    thread_id: str

class ContinueRequest(BaseModel):
    thread_id: str

class StatusRequest(BaseModel):
    thread_id: str

@app.get("/")
def read_root():
    return {
        "message": "Stateful Joke Generation API is running!",
        "version": "2.0.0(Statefull)",
        "endpoints": [
            "/health",
            "/start - Start joke generation",
            "/continue - Generate explanation",
            "/status - Check thread status"
        ]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "persistence": "SQLite"}

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
            "status": result['status'],
            "message": "Workflow completed."
        }
    except ValueError as e:
        print(f"API validation error in /continue (Invalid thread id): {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"API error in /continue: {str(e)}")
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
