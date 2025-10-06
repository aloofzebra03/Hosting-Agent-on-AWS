@echo off
REM Deployment script for Windows
REM Usage: deploy.bat [environment]

setlocal enabledelayedexpansion

set ENVIRONMENT=%1
if "%ENVIRONMENT%"=="" set ENVIRONMENT=development

set APP_NAME=joke-generation-agent

echo 🚀 Deploying %APP_NAME% to %ENVIRONMENT% environment...

REM Create directories if they don't exist
if not exist data mkdir data
if not exist logs mkdir logs

REM Copy environment file
if not exist .env (
    echo 📝 Creating .env file from template...
    (
        echo # Google AI API Configuration
        echo GOOGLE_API_KEY=your_google_api_key_here
        echo.
        echo # Model Configuration
        echo MODEL_NAME=gemini-2.0-flash
        echo.
        echo # Application Settings
        echo DEBUG=false
        echo LOG_LEVEL=INFO
        echo.
        echo # Checkpointer Configuration
        echo USE_PERSISTENT_CHECKPOINTER=true
        echo CHECKPOINT_DB_PATH=/app/data/checkpoints.db
    ) > .env
    echo ⚠️  Please update the .env file with your API keys before continuing!
    pause
    exit /b 1
)

REM Build and start the application
echo 🔨 Building Docker containers...
docker-compose build

echo 🏃 Starting services...
if "%ENVIRONMENT%"=="production" (
    docker-compose --profile production up -d
) else (
    docker-compose up -d
)

REM Wait for services to be healthy
echo ⏳ Waiting for services to be healthy...
timeout /t 10 /nobreak

REM Health check
echo 🏥 Performing health check...
curl -f http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Deployment successful! Service is healthy.
    echo 🌐 API is available at: http://localhost:8000
    echo 📚 API documentation: http://localhost:8000/docs
) else (
    echo ❌ Health check failed. Checking logs...
    docker-compose logs joke-agent
    exit /b 1
)

echo 🎉 Deployment complete!
pause
