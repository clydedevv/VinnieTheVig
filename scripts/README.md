# AIGG Scripts & Development Tools

## Quick Start with Just

The easiest way to manage AIGG services:

```bash
# Start everything
just up

# Monitor in real-time
just dashboard

# Stop everything  
just down
```

## Available Commands

### 🚀 Core Operations
- `just up` - Start all services
- `just down` - Stop all services
- `just restart` - Restart all services
- `just status` - Quick health check

### 📊 Monitoring
- `just dashboard` - Live terminal dashboard (updates every 2s)
- `just watch` - Split-screen tmux monitoring
- `just logs` - Tail all log files
- `just health` - Check service health endpoints

### 🧪 Testing
- `just analyze "query"` - Test market analysis
- `just test` - Run pytest suite
- `just test-all` - Quick integration test

### 🔧 Advanced
- `just attach [api|wrapper|bot]` - Attach to tmux session
- `just sys-install` - Install systemd services
- `just sys-status` - Check systemd status

## dev_up.sh - Development Environment Manager

A single command to manage all AIGG services during development using tmux sessions.

### Quick Start

```bash
# Start all services
./scripts/dev_up.sh up

# Check status
./scripts/dev_up.sh status

# Tail logs
./scripts/dev_up.sh logs

# Stop everything
./scripts/dev_up.sh down
```

### Commands

- `up/start` - Start all services (API, wrapper, bot)
- `down/stop` - Stop all services
- `restart` - Restart all services
- `status/ps` - Show health status and recent logs
- `logs/tail` - Tail all log files continuously

### Configuration

Set these environment variables before running:

```bash
export API_PORT=8001              # API server port
export WRAPPER_PORT=8003          # Twitter wrapper port  
export BOT_INTERVAL=30            # Bot check interval (seconds)
export DISABLE_WHITELIST=true     # Disable whitelist for testing
```

### Accessing Services

Once started, you can:
- Attach to tmux sessions: `tmux attach -t aigg-api`
- Check API health: `curl http://localhost:8001/health`
- Check wrapper health: `curl http://localhost:8003/health`

### Features

✅ Auto-detects repository location  
✅ Sources `.env` automatically  
✅ Activates virtual environment  
✅ Creates logs directory  
✅ Color-coded output  
✅ Health checks included  
✅ Works with docker-compose aliases (`up`/`down`)