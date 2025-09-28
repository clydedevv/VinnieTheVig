#!/bin/bash

# AIGG Services Startup Script
# Run this after configuring .env with proper API keys

echo "🚀 Starting AIGG Infrastructure Services..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Check if .env file exists with required variables
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please configure environment variables."
    exit 1
fi

cd /home/cosmos/aigg-insights

# Kill existing sessions if they exist
tmux kill-session -t aigg-api 2>/dev/null || true
tmux kill-session -t twitter-wrapper 2>/dev/null || true
tmux kill-session -t aigg-twitter-bot 2>/dev/null || true

echo "📊 Starting Main API Server (port 8001)..."
tmux new-session -d -s aigg-api \
  'cd /home/cosmos/aigg-insights && source venv/bin/activate && uvicorn api.main:app --host 0.0.0.0 --port 8001'

echo "🔗 Starting Twitter Wrapper API (port 8003)..."
tmux new-session -d -s twitter-wrapper \
  'cd /home/cosmos/aigg-insights && source venv/bin/activate && python src/api_wrapper/twitter_wrapper.py'

echo "🤖 Starting Twitter Bot (X Premium: 30s checks)..."
tmux new-session -d -s aigg-twitter-bot \
  'cd /home/cosmos/aigg-insights && source venv/bin/activate && python main.py twitter-bot --interval 30 --disable-whitelist'

echo "✅ All services started!"
echo ""
echo "📋 Service Status:"
echo "   • Main API:      tmux attach-session -t aigg-api"
echo "   • Wrapper API:   tmux attach-session -t twitter-wrapper"  
echo "   • Twitter Bot:   tmux attach-session -t aigg-twitter-bot"
echo ""
echo "🔍 Check status with: tmux list-sessions"
echo "🌐 Test API at: http://localhost:8001/health" 