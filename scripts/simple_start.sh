#!/usr/bin/env bash
set -euo pipefail

# Simple, bulletproof service starter

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

API_PORT="${API_PORT:-8001}"
WRAPPER_PORT="${WRAPPER_PORT:-8003}"
BOT_INTERVAL="${BOT_INTERVAL:-60}"

cd "$REPO_DIR"

# Ensure logs directory exists
mkdir -p logs

# Kill any existing sessions
tmux kill-session -t aigg-api 2>/dev/null || true
tmux kill-session -t twitter-wrapper 2>/dev/null || true
tmux kill-session -t aigg-bot 2>/dev/null || true

echo "🚀 Starting AIGG Services..."

# Start API
echo "  Starting API on port $API_PORT..."
tmux new -s aigg-api -d "cd '$REPO_DIR' && python3 main.py api-server --port $API_PORT --host 0.0.0.0"

# Wait for API to be ready
echo "  Waiting for API to be healthy..."
for i in {1..30}; do
  if curl -sSf "http://localhost:$API_PORT/health" >/dev/null 2>&1; then
    echo "  ✅ API is ready!"
    break
  fi
  sleep 1
done

# Start Wrapper
echo "  Starting Wrapper on port $WRAPPER_PORT..."
tmux new -s twitter-wrapper -d "cd '$REPO_DIR' && python3 main.py wrapper-api --port $WRAPPER_PORT"

# Wait for Wrapper to be ready
echo "  Waiting for Wrapper to be healthy..."
for i in {1..30}; do
  if curl -sSf "http://localhost:$WRAPPER_PORT/health" >/dev/null 2>&1; then
    echo "  ✅ Wrapper is ready!"
    break
  fi
  sleep 1
done

# Start Bot
echo "  Starting Bot..."
tmux new -s aigg-bot -d "cd '$REPO_DIR' && python3 main.py twitter-bot --interval $BOT_INTERVAL"

echo ""
echo "✅ All services started successfully!"
echo ""
echo "📊 Check status:  just status"
echo "📝 Test:         just analyze 'Will Bitcoin hit 150k?'"
echo "🛑 Stop:         just down"