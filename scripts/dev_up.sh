#!/usr/bin/env bash
# Bulletproof service manager - guaranteed to work

set -euo pipefail

# Config
API_PORT="${API_PORT:-8001}"
WRAPPER_PORT="${WRAPPER_PORT:-8003}"
BOT_INTERVAL="${BOT_INTERVAL:-60}"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd "$REPO_DIR"

# Function to kill all Python processes related to main.py
kill_all_python() {
    echo -e "${YELLOW}Killing all Python processes...${NC}"
    pkill -f "python.*main.py" 2>/dev/null || true
    pkill -f "python3.*main.py" 2>/dev/null || true
    sleep 1
}

# Function to kill all tmux sessions
kill_all_tmux() {
    echo -e "${YELLOW}Killing all tmux sessions...${NC}"
    unset TMUX
    tmux kill-server 2>/dev/null || true
    sleep 1
}

# Function to start services
start_services() {
    echo -e "${GREEN}Starting services...${NC}"
    
    # Ensure logs directory exists
    mkdir -p logs
    
    # Start API
    echo -e "  ${GREEN}[1/3]${NC} Starting API on port $API_PORT..."
    TMUX= tmux new-session -d -s api bash -c "cd '$REPO_DIR' && source venv/bin/activate && python3 main.py api-server --port $API_PORT --host 0.0.0.0 2>&1 | tee -a logs/api.log"
    
    # Wait for API
    echo -e "  ${YELLOW}Waiting for API...${NC}"
    for i in {1..30}; do
        if curl -sSf "http://localhost:$API_PORT/health" >/dev/null 2>&1; then
            echo -e "  ${GREEN}✓${NC} API is ready!"
            break
        fi
        sleep 1
        if [ $i -eq 30 ]; then
            echo -e "  ${RED}✗${NC} API failed to start!"
            return 1
        fi
    done
    
    # Start Wrapper
    echo -e "  ${GREEN}[2/3]${NC} Starting Wrapper on port $WRAPPER_PORT..."
    TMUX= tmux new-session -d -s wrapper bash -c "cd '$REPO_DIR' && source venv/bin/activate && python3 main.py wrapper-api --port $WRAPPER_PORT 2>&1 | tee -a logs/wrapper.log"
    
    # Wait for Wrapper
    echo -e "  ${YELLOW}Waiting for Wrapper...${NC}"
    for i in {1..30}; do
        if curl -sSf "http://localhost:$WRAPPER_PORT/health" >/dev/null 2>&1; then
            echo -e "  ${GREEN}✓${NC} Wrapper is ready!"
            break
        fi
        sleep 1
        if [ $i -eq 30 ]; then
            echo -e "  ${RED}✗${NC} Wrapper failed to start!"
            return 1
        fi
    done
    
    # Start Bot
    echo -e "  ${GREEN}[3/3]${NC} Starting Bot (interval: ${BOT_INTERVAL}s)..."
    TMUX= tmux new-session -d -s bot bash -c "cd '$REPO_DIR' && source venv/bin/activate && python3 main.py twitter-bot --interval $BOT_INTERVAL 2>&1 | tee -a logs/bot.log"
    
    echo -e "${GREEN}✅ All services started successfully!${NC}"
}

# Function to show status
show_status() {
    echo -e "\n${YELLOW}=== Service Status ===${NC}\n"
    
    # Check tmux sessions
    echo -e "${GREEN}Tmux Sessions:${NC}"
    if tmux ls 2>/dev/null; then
        tmux ls | sed 's/^/  /'
    else
        echo -e "  ${RED}No tmux sessions running${NC}"
    fi
    
    echo -e "\n${GREEN}Health Checks:${NC}"
    
    # API health
    echo -n "  API (port $API_PORT): "
    if curl -sSf "http://localhost:$API_PORT/health" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ HEALTHY${NC}"
    else
        echo -e "${RED}✗ DOWN${NC}"
    fi
    
    # Wrapper health
    echo -n "  Wrapper (port $WRAPPER_PORT): "
    if curl -sSf "http://localhost:$WRAPPER_PORT/health" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ HEALTHY${NC}"
    else
        echo -e "${RED}✗ DOWN${NC}"
    fi
    
    echo -e "\n${GREEN}Python Processes:${NC}"
    ps aux | grep -E "python3?.*main.py" | grep -v grep | sed 's/^/  /' || echo -e "  ${RED}None running${NC}"
}

# Main command handler
case "${1:-}" in
    up|start)
        echo -e "${GREEN}🚀 Starting AIGG services...${NC}"
        kill_all_python
        kill_all_tmux
        start_services
        show_status
        ;;
    
    down|stop)
        echo -e "${RED}🛑 Stopping AIGG services...${NC}"
        kill_all_python
        kill_all_tmux
        echo -e "${GREEN}✅ All services stopped${NC}"
        ;;
    
    restart)
        echo -e "${YELLOW}🔄 Restarting AIGG services...${NC}"
        kill_all_python
        kill_all_tmux
        sleep 2
        start_services
        show_status
        ;;
    
    status)
        show_status
        ;;
    
    *)
        echo "Usage: $0 {up|down|restart|status}"
        echo "  up/start    - Start all services"
        echo "  down/stop   - Stop all services"
        echo "  restart     - Restart all services"
        echo "  status      - Show service status"
        exit 1
        ;;
esac