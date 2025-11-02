# Hosting LangGraph Agent on AWS

A comprehensive demonstration of deploying stateful and stateless LangGraph agents as Fast APIs on AWS, featuring three different implementation patterns for building conversational AI workflows with different persistence strategies.

## 🎯 Project Overview

This project demonstrates how to build, containerize, and deploy LangGraph-based AI agents to AWS. It showcases three distinct architectural patterns for managing conversational state in AI workflows:

1. **Stateful with Database** - PostgreSQL/SQLite persistence with interrupts
2. **Stateful without Database** - In-memory state with client-side routing
3. **Stateless** - Simple request-response pattern

All implementations use FastAPI for REST endpoints, Docker for containerization, and Google Gemini AI for content generation.

## 📁 Project Structure

```
Hosting-Agent-on-AWS/
│
├── Statefull/                    # PostgreSQL-backed stateful agent
│   ├── src/
│   │   ├── graph.py             # LangGraph workflow with PostgreSQL checkpointing
│   │   ├── core.py              # Joke & explanation generators
│   │   ├── models.py            # State type definitions
│   │   └── config.py            # LLM configuration
│   ├── api_server.py            # FastAPI endpoints (/start, /continue, /status)
│   ├── Dockerfile               # Container configuration
│   └── requirements.txt         # Python dependencies
│
├── Statefull_no_db/             # Interrupt-based stateful agent (no persistence)
│   ├── src/
│   │   ├── graph.py             # LangGraph workflow with client-side state
│   │   ├── core.py              # Multi-step generators (joke, explanation, rating, alternative)
│   │   ├── models.py            # State type definitions
│   │   └── config.py            # LLM configuration
│   ├── api_server.py            # FastAPI endpoints with state forwarding
│   ├── Dockerfile               # Container configuration
│   └── requirements.txt         # Python dependencies
│
├── Stateless/                   # Simple stateless agent
│   ├── src/
│   │   ├── graph.py             # Basic LangGraph workflow
│   │   ├── core.py              # Joke & explanation generators
│   │   ├── models.py            # State type definitions
│   │   └── config.py            # LLM configuration
│   ├── api_server.py            # FastAPI endpoint (/generate-joke)
│   ├── Dockerfile               # Container configuration
│   └── requirements.txt         # Python dependencies

```

## 🏗️ Architecture Patterns

### 1. Stateful (with Database) - Full Persistence

**Use Case:** Production applications requiring persistent state across server restarts, multiple users, and long-running workflows.

**Key Features:**

- PostgreSQL (Supabase) or SQLite for checkpoint storage
- State survives server restarts
- Multi-step workflow with interrupts
- Thread-based session management
- Scalable to thousands of concurrent conversations

**Flow:**

```
Client → POST /start {topic, thread_id}
         ↓
     Generate Joke → Save to DB → Return Joke
         ↓
Client → POST /continue {thread_id}
         ↓
     Load State from DB → Generate Explanation → Return Result
```

**Endpoints:**

- `POST /start` - Start workflow, generate joke (pauses)
- `POST /continue` - Resume workflow, generate explanation
- `POST /status` - Check thread status

### 2. Stateful (without Database) - Client-Side State

**Use Case:** Applications where clients can maintain state, reducing server-side complexity and database dependencies.

**Key Features:**

- State returned to client after each step
- Client sends state back to continue
- No database required
- Automatic routing based on `next_node`
- Four-step workflow: joke → explanation → rating → alternative

**Flow:**

```
Client → POST /start {topic}
         ↓
     Generate Joke → Return {joke, next_node: "explanation"}
         ↓
Client → POST /continue {state with next_node}
         ↓
     Route to Explanation → Return {joke, explanation, next_node: "rating"}
         ↓
     (Continues through all nodes until next_node: "END")
```

**Endpoints:**

- `POST /start` - Start workflow, return initial state
- `POST /continue` - Continue with provided state, auto-route to next node

### 3. Stateless - Simple Request-Response

**Use Case:** Simple APIs where each request is independent, no multi-step workflows needed.

**Key Features:**

- Single endpoint does everything
- No state management
- Simplest implementation
- Suitable for one-shot tasks

**Flow:**

```
Client → POST /generate-joke {topic}
         ↓
     Generate Joke + Explanation → Return Complete Result
```

**Endpoints:**

- `POST /generate-joke` - Generate joke and explanation in one call

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Google AI API Key ([Get it here](https://makersuite.google.com/app/apikey))
- (Optional) Supabase PostgreSQL database for Stateful version

## 🐳 Docker Deployment

### Build and Push to Docker Hub

```bash
# Navigate to desired implementation
cd Statefull  # or Statefull_no_db or Stateless

# Build image
docker build -t your-username/joke-agent:latest .

# Push to Docker Hub
docker login
docker push your-username/joke-agent:latest
```

### Pull and Run

```bash
docker pull your-username/joke-agent:latest
docker run -p 8000:8000 --env-file .env your-username/joke-agent:latest
```

## ☁️ AWS Deployment

Mentioned in detail in the second document alongwith handling of environment variables.

## 🔑 Environment Variables

### Required for All Versions

```env
# Google AI API Key (required)
GOOGLE_API_KEY=your_google_api_key_here

# Model Configuration (optional)
MODEL_NAME=gemini-2.0-flash  # or gemini-1.5-pro
```

### Additional for Stateful (with DB)

```env
# PostgreSQL Connection (Supabase or self-hosted)
POSTGRES_DATABASE_URL=postgresql://user:pass@host:5432/database

# Or for local SQLite (fallback)
CHECKPOINT_DB_PATH=/app/data/checkpoints.db
```

## 🔧 Technology Stack

- **Backend Framework:** FastAPI
- **AI Orchestration:** LangGraph
- **LLM Provider:** Google Gemini AI (gemini-2.0-flash)
- **State Management:** PostgreSQL (Supabase), SQLite, In-Memory
- **Containerization:** Docker
- **Cloud Platform:** AWS (EC2)

## 📝 API Documentation

After starting the server, visit:

- **Swagger UI:** http://localhost:8000/docs

## 🎓 Use Cases

### Stateful (with Database)

- Multi-user chat applications
- Long-running workflows requiring resumption
- Production systems needing audit trails
- Applications requiring state across server restarts

### Stateful (without Database)

- Mobile/web apps maintaining their own state
- Microservices with client-side state management
- Reduced server complexity scenarios
- Cost-sensitive deployments (no database costs)

### Stateless

- Simple API services
- One-shot tasks
- Prototype and demo applications
- High-throughput, low-latency requirements

## 📚 Additional Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Google AI Studio](https://makersuite.google.com/)
- [Docker Documentation](https://docs.docker.com/)
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)

**Happy Deploying! 🚀**
