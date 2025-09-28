# Use bash so we can source and use arrays if needed
set shell := ["bash", "-euo", "pipefail", "-c"]

# Default environment (override when calling: API_PORT=8000 just up)
export API_PORT := env_var_or_default("API_PORT", "8001")
export WRAPPER_PORT := env_var_or_default("WRAPPER_PORT", "8003")
export BOT_INTERVAL := env_var_or_default("BOT_INTERVAL", "60")
export DISABLE_WHITELIST := "${DISABLE_WHITELIST:-}"  # set to 'true' to disable whitelist

help:
    @echo "🚀 AIGG Development Commands"
    @echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    @echo "  just up         # Start all services (tmux)"
    @echo "  just down       # Stop all services"
    @echo "  just restart    # Restart all services"
    @echo "  just status     # Show health and recent logs"
    @echo "  just dashboard  # 📊 Live monitoring dashboard"
    @echo "  just logs       # Tail wrapper & bot logs"
    @echo "  just attach-bot, attach-api, attach-wrapper  # Attach to tmux"
    @echo ""
    @echo "🔧 System Management:"
    @echo "  just sys-install  # Install systemd units (sudo)"
    @echo "  just sys-start|sys-stop|sys-status|sys-restart|sys-enable|sys-disable"
    @echo ""
    @echo "🧪 Testing:"
    @echo "  just health     # Check health endpoints"
    @echo "  just analyze <query>  # Test market analysis"
    @echo "  just test       # Run pytest suite"
    @echo ""
    @echo "⚙️  Configuration (set before running):"
    @echo "  API_PORT=${API_PORT}  WRAPPER_PORT=${WRAPPER_PORT}  BOT_INTERVAL=${BOT_INTERVAL}"

# ----- Dev (tmux) orchestrator -----

up:
    @export API_PORT={{API_PORT}} && export WRAPPER_PORT={{WRAPPER_PORT}} && export BOT_INTERVAL={{BOT_INTERVAL}} && bash ./scripts/dev_up.sh up

down:
    @bash ./scripts/dev_up.sh down

restart:
    @export API_PORT={{API_PORT}} && export WRAPPER_PORT={{WRAPPER_PORT}} && export BOT_INTERVAL={{BOT_INTERVAL}} && bash ./scripts/dev_up.sh restart

status:
    @export API_PORT={{API_PORT}} && export WRAPPER_PORT={{WRAPPER_PORT}} && bash ./scripts/dev_up.sh status

# Dashboard - Live monitoring
dashboard:
    @API_PORT={{API_PORT}} WRAPPER_PORT={{WRAPPER_PORT}} ./scripts/dashboard.sh

# Watch mode - Split screen monitoring (tmux)
watch:
    @./scripts/watch.sh

# Tail logs
logs:
    @./scripts/dev_up.sh logs

# Attach to tmux sessions
attach-bot:
    @tmux attach -t aigg-bot || (echo "No 'aigg-bot' session" && exit 1)

attach-wrapper:
    @tmux attach -t twitter-wrapper || (echo "No 'twitter-wrapper' session" && exit 1)

attach-api:
    @tmux attach -t aigg-api || (echo "No 'aigg-api' session" && exit 1)

# Generic attach with parameter
attach SESSION:
    @tmux attach -t {{SESSION}} || (echo "No '{{SESSION}}' session" && exit 1)

# ----- Systemd helpers -----

sys-install:
    @echo "Installing systemd unit files (sudo)..."
    @sudo cp config/aigg-api.service /etc/systemd/system/aigg-api.service
    @sudo cp systemd/aigg-wrapper.service /etc/systemd/system/aigg-wrapper.service
    @sudo cp systemd/aigg-twitter-bot.service /etc/systemd/system/aigg-twitter-bot.service
    @sudo systemctl daemon-reload
    @echo "Done. Use 'just sys-enable && just sys-start' to enable & start."

sys-enable:
    @sudo systemctl enable aigg-api aigg-wrapper aigg-twitter-bot

sys-disable:
    @sudo systemctl disable aigg-api aigg-wrapper aigg-twitter-bot

sys-start:
    @sudo systemctl start aigg-api aigg-wrapper aigg-twitter-bot

sys-stop:
    @sudo systemctl stop aigg-twitter-bot aigg-wrapper aigg-api

sys-restart:
    @sudo systemctl restart aigg-api aigg-wrapper aigg-twitter-bot

sys-status:
    @systemctl --no-pager status aigg-api aigg-wrapper aigg-twitter-bot || true

sys-logs:
    @echo "journalctl -u aigg-api -f"
    @echo "journalctl -u aigg-wrapper -f"
    @echo "journalctl -u aigg-twitter-bot -f"

# ----- Health & Testing -----

health:
    @echo -n "API (:${API_PORT}) -> "
    @curl -sSf "http://localhost:${API_PORT}/health" >/dev/null && echo OK || echo FAIL
    @echo -n "Wrapper (:${WRAPPER_PORT}) -> "
    @curl -sSf "http://localhost:${WRAPPER_PORT}/health" >/dev/null && echo OK || echo FAIL

# Test market analysis
analyze query:
    @echo "🔍 Analyzing: {{query}}"
    @curl -s -X POST http://localhost:{{WRAPPER_PORT}}/analyze \
      -H 'Content-Type: application/json' \
      -d '{"query":"{{query}}","user_id":"195487174"}' | jq -r '.tweet_text // .error_message'

# Run tests
test:
    @echo "🧪 Running tests..."
    @source venv/bin/activate && python -m pytest tests/ -v

# Quick test of all components
test-all: health
    @echo "🧪 Testing market analysis..."
    @just analyze "Will Bitcoin hit 150k?" | head -5


