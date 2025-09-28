#!/usr/bin/env bash

# AIGG Services Live Dashboard
# Real-time monitoring of all services in your terminal

# Auto-detect repo directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# Configuration
API_PORT="${API_PORT:-8001}"
WRAPPER_PORT="${WRAPPER_PORT:-8003}"
REFRESH_INTERVAL="${REFRESH_INTERVAL:-2}"  # seconds

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'  # No Color

# Unicode characters
CHECK="✓"
CROSS="✗"
BULLET="•"

# Clear screen and move cursor to top
clear_screen() {
    printf "\033[2J\033[H"
}

# Get service status
get_service_status() {
    local service=$1
    if tmux has-session -t "$service" 2>/dev/null; then
        echo "${GREEN}${CHECK} Running${NC}"
    else
        echo "${RED}${CROSS} Stopped${NC}"
    fi
}

# Check health endpoint
check_health() {
    local port=$1
    if curl -sSf "http://localhost:${port}/health" >/dev/null 2>&1; then
        echo "${GREEN}${CHECK} Healthy${NC}"
    else
        echo "${RED}${CROSS} Unhealthy${NC}"
    fi
}

# Get log tail
get_recent_log() {
    local logfile=$1
    local lines=${2:-1}
    if [ -f "$logfile" ]; then
        tail -n "$lines" "$logfile" 2>/dev/null | tail -1 | cut -c1-80
    else
        echo "No log file"
    fi
}

# Count lines in log
count_log_lines() {
    local logfile=$1
    if [ -f "$logfile" ]; then
        wc -l < "$logfile" 2>/dev/null || echo "0"
    else
        echo "0"
    fi
}

# Get tmux session info
get_tmux_info() {
    local session=$1
    if tmux has-session -t "$session" 2>/dev/null; then
        local pane_pid=$(tmux list-panes -t "$session" -F "#{pane_pid}" 2>/dev/null | head -1)
        if [ -n "$pane_pid" ]; then
            # Get CPU and memory for the process
            ps -p "$pane_pid" -o %cpu,%mem --no-headers 2>/dev/null | awk '{printf "CPU: %s%% MEM: %s%%", $1, $2}'
        else
            echo "N/A"
        fi
    else
        echo "Not running"
    fi
}

# Main dashboard loop
dashboard() {
    while true; do
        clear_screen
        
        # Header
        echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${BOLD}${CYAN}║                        🚀 AIGG Services Dashboard 🚀                         ║${NC}"
        echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        
        # Timestamp
        echo -e "${YELLOW}Last Updated:${NC} $(date '+%Y-%m-%d %H:%M:%S')"
        echo -e "${YELLOW}Refresh Rate:${NC} ${REFRESH_INTERVAL}s | Press ${BOLD}Ctrl+C${NC} to exit"
        echo ""
        
        # Services Status
        echo -e "${BOLD}${MAGENTA}═══ Service Status ═══${NC}"
        echo ""
        
        # API Service
        api_status=$(get_service_status "aigg-api")
        api_health=$(check_health "$API_PORT")
        api_info=$(get_tmux_info "aigg-api")
        echo -e "  ${BOLD}API Server${NC} (port ${API_PORT})"
        echo -e "    Status:  $api_status"
        echo -e "    Health:  $api_health"
        echo -e "    Process: $api_info"
        echo ""
        
        # Wrapper Service
        wrapper_status=$(get_service_status "twitter-wrapper")
        wrapper_health=$(check_health "$WRAPPER_PORT")
        wrapper_info=$(get_tmux_info "twitter-wrapper")
        echo -e "  ${BOLD}Twitter Wrapper${NC} (port ${WRAPPER_PORT})"
        echo -e "    Status:  $wrapper_status"
        echo -e "    Health:  $wrapper_health"
        echo -e "    Process: $wrapper_info"
        echo ""
        
        # Bot Service
        bot_status=$(get_service_status "aigg-bot")
        bot_info=$(get_tmux_info "aigg-bot")
        echo -e "  ${BOLD}Twitter Bot${NC}"
        echo -e "    Status:  $bot_status"
        echo -e "    Process: $bot_info"
        echo ""
        
        # Log Activity
        echo -e "${BOLD}${MAGENTA}═══ Recent Activity ═══${NC}"
        echo ""
        
        # Wrapper logs
        wrapper_log="${REPO_DIR}/logs/twitter_wrapper.log"
        wrapper_lines=$(count_log_lines "$wrapper_log")
        wrapper_recent=$(get_recent_log "$wrapper_log")
        echo -e "  ${BOLD}Wrapper Log${NC} (${wrapper_lines} lines)"
        echo -e "    ${CYAN}└─${NC} $wrapper_recent"
        echo ""
        
        # Bot logs
        bot_log="${REPO_DIR}/logs/aigg_twitter_bot.log"
        bot_lines=$(count_log_lines "$bot_log")
        bot_recent=$(get_recent_log "$bot_log")
        echo -e "  ${BOLD}Bot Log${NC} (${bot_lines} lines)"
        echo -e "    ${CYAN}└─${NC} $bot_recent"
        echo ""
        
        # Quick Commands
        echo -e "${BOLD}${MAGENTA}═══ Quick Commands ═══${NC}"
        echo ""
        echo -e "  ${YELLOW}${BULLET}${NC} Start all:    ${CYAN}just up${NC}"
        echo -e "  ${YELLOW}${BULLET}${NC} Stop all:     ${CYAN}just down${NC}"
        echo -e "  ${YELLOW}${BULLET}${NC} View logs:    ${CYAN}just logs${NC}"
        echo -e "  ${YELLOW}${BULLET}${NC} Attach tmux:  ${CYAN}just attach [api|wrapper|bot]${NC}"
        echo ""
        
        # Footer
        echo -e "${BOLD}${CYAN}════════════════════════════════════════════════════════════════════════════════${NC}"
        
        # Wait before refresh
        sleep "$REFRESH_INTERVAL"
    done
}

# Run dashboard
dashboard