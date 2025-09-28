#!/usr/bin/env bash

# AIGG Watch Mode - Split screen monitoring
# Uses tmux to create a monitoring dashboard

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

SESSION="aigg-watch"

# Kill existing watch session if it exists
tmux kill-session -t "$SESSION" 2>/dev/null

# Create new session with dashboard
tmux new-session -d -s "$SESSION" -n "monitor" "$SCRIPT_DIR/dashboard.sh"

# Split horizontally for logs
tmux split-window -v -t "$SESSION:monitor" -p 30 "tail -f $REPO_DIR/logs/*.log"

# Split vertically for health checks
tmux split-window -h -t "$SESSION:monitor.1" "watch -n 5 'just health'"

# Attach to session
echo "Starting watch mode..."
echo "Layout: Dashboard (top) | Logs (bottom-left) | Health (bottom-right)"
echo ""
tmux attach-session -t "$SESSION"