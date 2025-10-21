from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from src.graph import generate_joke_with_explanation

# Create simple FastAPI app
app = FastAPI(title="Joke Generation API", version="1.0.0")

# Simple request model
class JokeRequest(BaseModel):
    topic: str
    thread_id: str = "default"

@app.get("/")
def read_root():
    return {"message": "Joke Generation API is running!", "endpoints": ["/health", "/generate-joke"]}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/generate-joke")
def generate_joke_endpoint(request: JokeRequest):
    try:
        print(f"API request for topic: {request.topic}")
        result = generate_joke_with_explanation(request.topic, request.thread_id)
        
        return {
            "topic": request.topic,
            "joke": result.get("joke", "No joke generated"),
            "explanation": result.get("explanation", "No explanation generated"),
            "thread_id": request.thread_id
        }
    except Exception as e:
        print(f"API error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# if __name__ == "__main__":
#     print("Starting Joke Generation API server on port 8000...")
#     print("Endpoints available:")
#     print("  GET  /health - Health check")
#     print("  POST /generate-joke - Generate joke")
#     uvicorn.run(app, host="0.0.0.0", port=8000)
