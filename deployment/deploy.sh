#!/bin/bash

# Deployment script for AWS EC2
# Usage: ./deploy.sh [environment]

set -e

ENVIRONMENT=${1:-development}
APP_NAME="joke-generation-agent"
REGION="us-east-1"

echo "🚀 Deploying $APP_NAME to $ENVIRONMENT environment..."

# Create directories if they don't exist
mkdir -p data logs

# Copy environment file
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cat > .env << EOF
# Google AI API Configuration
GOOGLE_API_KEY=your_google_api_key_here

# Model Configuration
MODEL_NAME=gemini-2.0-flash

# Application Settings
DEBUG=false
LOG_LEVEL=INFO

# Checkpointer Configuration
USE_PERSISTENT_CHECKPOINTER=true
CHECKPOINT_DB_PATH=/app/data/checkpoints.db
EOF
    echo "⚠️  Please update the .env file with your API keys before continuing!"
    exit 1
fi

# Build and start the application
echo "🔨 Building Docker containers..."
docker-compose build

echo "🏃 Starting services..."
if [ "$ENVIRONMENT" = "production" ]; then
    docker-compose --profile production up -d
else
    docker-compose up -d
fi

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Health check
echo "🏥 Performing health check..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Deployment successful! Service is healthy."
    echo "🌐 API is available at: http://localhost:8000"
    echo "📚 API documentation: http://localhost:8000/docs"
else
    echo "❌ Health check failed. Checking logs..."
    docker-compose logs joke-agent
    exit 1
fi

echo "🎉 Deployment complete!"
