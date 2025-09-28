# Running the System

Complete guide to running AIGG Insights in various modes and configurations.

## System Architecture Overview

```mermaid
graph LR
    CLI[main.py CLI] --> Bot[Twitter Bot]
    CLI --> API[Market API]
    CLI --> Wrapper[Wrapper API]
    CLI --> Analysis[Analysis Engine]

    Bot --> DB[(PostgreSQL)]
    API --> DB
    Wrapper --> Analysis
    Analysis --> DB
```

## Quick Start Commands

```bash
# Single analysis
python main.py analyze "Will Bitcoin reach 200k?"

# Start API server
python main.py api-server --port 8001

# Start Twitter bot
python main.py twitter-bot --interval 30

# Run tests
python main.py test
```

## 1. CLI Interface (`main.py`)

The central command interface for all operations.

### Available Commands

```bash
# Show all commands
python main.py --help

# Commands:
#   analyze          Run market analysis
#   api-server       Start Market API server
#   wrapper-api      Start Twitter Wrapper API
#   twitter-bot      Start Twitter bot
#   database         Database operations
#   test             Run tests
#   status           System status check
```

### Command Details

#### analyze - Market Analysis

```bash
# Basic analysis
python main.py analyze "Your market question"

# With options
python main.py analyze "Bitcoin 200k?" \
    --detailed \
    --save-to-db \
    --format json

# Parameters:
#   --detailed      Include research data
#   --save-to-db    Store results in database
#   --format        Output format (json|text|twitter)
#   --persona       Analysis persona (technical|casual|degen)
```

#### api-server - Market API

```bash
# Start with defaults
python main.py api-server

# Custom configuration
python main.py api-server \
    --port 8001 \
    --host 0.0.0.0 \
    --workers 4 \
    --reload

# Parameters:
#   --port          Port number (default: 8001)
#   --host          Host address (default: 127.0.0.1)
#   --workers       Number of workers (default: 1)
#   --reload        Auto-reload on code changes
```

#### wrapper-api - Twitter Integration API

```bash
# Start wrapper API
python main.py wrapper-api \
    --port 8003 \
    --host 0.0.0.0

# Parameters:
#   --port          Port number (default: 8003)
#   --host          Host address (default: 127.0.0.1)
```

#### twitter-bot - Twitter Bot

```bash
# Start with X Premium (30-second interval)
python main.py twitter-bot --interval 30 --disable-whitelist

# Development mode (no posting)
python main.py twitter-bot --dry-run --verbose

# Parameters:
#   --interval           Check interval in seconds (30 for Premium)
#   --disable-whitelist  Allow all users
#   --dry-run           Don't post responses
#   --verbose           Detailed logging
#   --max-mentions      Max mentions per cycle
```

#### database - Database Operations

```bash
# Initialize database
python main.py database init

# Load markets
python main.py database load-markets --full

# Update markets
python main.py database update-markets

# Database commands:
#   init            Create schema
#   load-markets    Import from Polymarket
#   update-markets  Update existing markets
#   validate        Check data integrity
#   backup          Create backup
#   restore         Restore from backup
```

#### test - Run Tests

```bash
# Run all tests
python main.py test

# Specific component
python main.py test --component flow
python main.py test --component api
python main.py test --component bot

# With coverage
python main.py test --coverage

# Parameters:
#   --component     Test specific component
#   --coverage      Generate coverage report
#   --verbose       Detailed output
```

#### status - System Health Check

```bash
# Check system status
python main.py status

# Detailed status
python main.py status --detailed

# Output format
python main.py status --format json
```

## 2. Development Mode

### Local Development Setup

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Set development environment
export ENV=development
export DEBUG=true

# 3. Start services
python main.py api-server --reload &
python main.py wrapper-api --reload &

# 4. Run development bot
python main.py twitter-bot --dry-run --verbose
```

### Development Tools

```bash
# Watch logs
tail -f logs/aigg.log

# Monitor database
watch -n 5 'psql -c "SELECT count(*) FROM analysis"'

# API documentation
open http://localhost:8001/docs
```

## 3. Production Deployment

### Using systemd Services

Create service files:

```ini
# /etc/systemd/system/aigg-api.service
[Unit]
Description=AIGG Market API
After=network.target postgresql.service

[Service]
Type=simple
User=aigg
Group=aigg
WorkingDirectory=/opt/aigg-insights
Environment="PATH=/opt/aigg-insights/venv/bin"
ExecStart=/opt/aigg-insights/venv/bin/python main.py api-server --port 8001 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/aigg-bot.service
[Unit]
Description=AIGG Twitter Bot
After=network.target aigg-api.service

[Service]
Type=simple
User=aigg
Group=aigg
WorkingDirectory=/opt/aigg-insights
Environment="PATH=/opt/aigg-insights/venv/bin"
ExecStart=/opt/aigg-insights/venv/bin/python main.py twitter-bot --interval 30
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```

### Start Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable aigg-api
sudo systemctl enable aigg-bot

# Start services
sudo systemctl start aigg-api
sudo systemctl start aigg-bot

# Check status
sudo systemctl status aigg-api
sudo systemctl status aigg-bot

# View logs
journalctl -u aigg-api -f
journalctl -u aigg-bot -f
```

### Using Docker

```bash
# Build image
docker build -t aigg-insights .

# Run API
docker run -d \
    --name aigg-api \
    -p 8001:8001 \
    --env-file .env \
    aigg-insights python main.py api-server

# Run Bot
docker run -d \
    --name aigg-bot \
    --env-file .env \
    aigg-insights python main.py twitter-bot --interval 30
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: aigg_insights
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: .
    command: python main.py api-server --port 8001 --workers 4
    ports:
      - "8001:8001"
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/aigg_insights
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped

  bot:
    build: .
    command: python main.py twitter-bot --interval 30
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/aigg_insights
    depends_on:
      - api
      - postgres
    restart: unless-stopped

volumes:
  postgres_data:
```

Run with Docker Compose:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 4. Process Management

### Using PM2

```bash
# Install PM2
npm install -g pm2

# Start services
pm2 start ecosystem.config.js

# ecosystem.config.js
module.exports = {
  apps: [
    {
      name: 'aigg-api',
      script: 'python',
      args: 'main.py api-server --port 8001',
      cwd: '/opt/aigg-insights',
      env: {
        PATH: '/opt/aigg-insights/venv/bin'
      }
    },
    {
      name: 'aigg-bot',
      script: 'python',
      args: 'main.py twitter-bot --interval 30',
      cwd: '/opt/aigg-insights',
      env: {
        PATH: '/opt/aigg-insights/venv/bin'
      }
    }
  ]
}

# Management commands
pm2 status
pm2 logs aigg-api
pm2 restart aigg-bot
pm2 save
pm2 startup
```

### Using Supervisor

```ini
# /etc/supervisor/conf.d/aigg.conf
[program:aigg-api]
command=/opt/aigg-insights/venv/bin/python main.py api-server --port 8001
directory=/opt/aigg-insights
user=aigg
autostart=true
autorestart=true
stderr_logfile=/var/log/aigg/api.err.log
stdout_logfile=/var/log/aigg/api.out.log

[program:aigg-bot]
command=/opt/aigg-insights/venv/bin/python main.py twitter-bot --interval 30
directory=/opt/aigg-insights
user=aigg
autostart=true
autorestart=true
stderr_logfile=/var/log/aigg/bot.err.log
stdout_logfile=/var/log/aigg/bot.out.log
```

## 5. Monitoring & Logging

### Log Configuration

```python
# config/logging.yaml
version: 1
formatters:
  default:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

handlers:
  console:
    class: logging.StreamHandler
    formatter: default
    stream: ext://sys.stdout

  file:
    class: logging.handlers.RotatingFileHandler
    formatter: default
    filename: logs/aigg.log
    maxBytes: 10485760  # 10MB
    backupCount: 5

root:
  level: INFO
  handlers: [console, file]
```

### Health Monitoring

```bash
# Health check endpoint
curl http://localhost:8001/health

# Metrics endpoint
curl http://localhost:8001/metrics

# Status check script
#!/bin/bash
services=("aigg-api:8001" "aigg-wrapper:8003")

for service in "${services[@]}"; do
    name="${service%%:*}"
    port="${service##*:}"

    if curl -f "http://localhost:$port/health" > /dev/null 2>&1; then
        echo "OK: $name is healthy"
    else
        echo "FAIL: $name is down"
    fi
done
```

### Performance Monitoring

```python
# Monitor resource usage
import psutil

def get_system_stats():
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "connections": len(psutil.net_connections()),
        "processes": len(psutil.pids())
    }
```

## 6. Scaling Strategies

### Horizontal Scaling

```nginx
# nginx.conf for load balancing
upstream aigg_api {
    least_conn;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 80;
    server_name api.aigg.com;

    location / {
        proxy_pass http://aigg_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Running Multiple Instances

```bash
# Start multiple API servers
for port in 8001 8002 8003; do
    python main.py api-server --port $port &
done

# Start multiple bots with coordination
python main.py twitter-bot --instance 1 --total-instances 3 &
python main.py twitter-bot --instance 2 --total-instances 3 &
python main.py twitter-bot --instance 3 --total-instances 3 &
```

## 7. Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Find process using port
lsof -i :8001

# Kill process
kill -9 <PID>
```

#### Database Connection Issues

```bash
# Test connection
psql -U aigg_user -d aigg_insights -c "SELECT 1"

# Check PostgreSQL status
sudo systemctl status postgresql
```

#### Memory Issues

```bash
# Check memory usage
free -h

# Clear Python cache
python -c "import gc; gc.collect()"
```

#### API Not Responding

```bash
# Check service status
systemctl status aigg-api

# Restart service
systemctl restart aigg-api

# Check logs
journalctl -u aigg-api -n 100
```

### Debug Mode

```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG

# Run with verbose output
python main.py analyze "test query" --verbose

# Profile performance
python -m cProfile -s cumtime main.py analyze "test"
```

## 8. Maintenance Mode

### Graceful Shutdown

```python
# Signal handler for graceful shutdown
import signal
import sys

def signal_handler(sig, frame):
    print('Gracefully shutting down...')
    # Clean up resources
    # Close database connections
    # Save state
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
```

### Maintenance Script

```bash
#!/bin/bash
# maintenance.sh

echo "Starting maintenance mode..."

# Stop services
systemctl stop aigg-bot
systemctl stop aigg-api

# Backup database
pg_dump -U aigg_user -d aigg_insights > backup_$(date +%Y%m%d).sql

# Run maintenance tasks
python scripts/cleanup_old_data.py
python scripts/optimize_database.py

# Start services
systemctl start aigg-api
systemctl start aigg-bot

echo "Maintenance complete!"
```