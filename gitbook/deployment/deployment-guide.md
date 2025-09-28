# Deployment Guide

## Prerequisites

### System Requirements
- Ubuntu 20.04+ or similar Linux distribution
- Python 3.9+
- PostgreSQL 14+
- 4GB+ RAM minimum (8GB recommended)
- 20GB+ disk space

### Required API Keys
- Twitter API v2 (X Premium account)
- Fireworks AI API key
- Perplexity API key
- PostgreSQL database credentials

## Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/clydedevv/VinnieTheVig.git
cd aigg-insights
```

### 2. Install Dependencies

```bash
# System packages
sudo apt-get update
sudo apt-get install -y python3-pip postgresql postgresql-contrib tmux

# Python dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

Create `.env` file with required credentials:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/aigg_insights

# Twitter API
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret

# AI Services
FIREWORKS_API_KEY=your_fireworks_key
PERPLEXITY_API_KEY=your_perplexity_key

# Service Configuration
MARKET_API_PORT=8001
WRAPPER_API_PORT=8003
TWITTER_BOT_INTERVAL=30
```

### 4. Database Setup

```bash
# Create database
sudo -u postgres psql -c "CREATE DATABASE aigg_insights;"
sudo -u postgres psql -c "CREATE USER aigg_user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE aigg_insights TO aigg_user;"

# Run migrations
python scripts/setup_database.py
```

### 5. Import Market Data

```bash
# Download Polymarket data
python scripts/import_polymarket_data.py

# Verify import
python main.py status
```

## Starting Services

### Using Tmux (Recommended)

Start all services in separate tmux sessions:

```bash
# Start Market API
tmux new -s market-api -d
tmux send-keys -t market-api "python main.py api-server --port 8001" Enter

# Start Twitter Wrapper
tmux new -s twitter-wrapper -d
tmux send-keys -t twitter-wrapper "python main.py wrapper-api --port 8003" Enter

# Start Twitter Bot
tmux new -s aigg-bot -d
tmux send-keys -t aigg-bot "python main.py twitter-bot --interval 30 --disable-whitelist" Enter
```

### Viewing Service Logs

```bash
# Attach to tmux session
tmux attach -t market-api      # View Market API logs
tmux attach -t twitter-wrapper  # View Wrapper API logs
tmux attach -t aigg-bot         # View Bot logs

# Detach from session: Ctrl+B, then D
```

### Using Systemd (Production)

Create service files in `/etc/systemd/system/`:

#### market-api.service
```ini
[Unit]
Description=AIGG Market API
After=network.target postgresql.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/aigg-insights
Environment="PATH=/home/ubuntu/.local/bin:/usr/bin"
ExecStart=/usr/bin/python3 main.py api-server --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
```

#### twitter-wrapper.service
```ini
[Unit]
Description=AIGG Twitter Wrapper
After=network.target market-api.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/aigg-insights
Environment="PATH=/home/ubuntu/.local/bin:/usr/bin"
ExecStart=/usr/bin/python3 main.py wrapper-api --port 8003
Restart=always

[Install]
WantedBy=multi-user.target
```

#### twitter-bot.service
```ini
[Unit]
Description=AIGG Twitter Bot
After=network.target twitter-wrapper.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/aigg-insights
Environment="PATH=/home/ubuntu/.local/bin:/usr/bin"
ExecStart=/usr/bin/python3 main.py twitter-bot --interval 30 --disable-whitelist
Restart=always

[Install]
WantedBy=multi-user.target
```

Start services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable market-api twitter-wrapper twitter-bot
sudo systemctl start market-api twitter-wrapper twitter-bot
```

## Health Checks

### Verify Services

```bash
# Check Market API
curl http://localhost:8001/health

# Check Twitter Wrapper
curl http://localhost:8003/health

# Check overall system status
python main.py status
```

### Expected Response

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "markets": {
    "total": 114450,
    "active": 6991
  },
  "uptime": "2 days, 3:45:22"
}
```

## Monitoring

### Service Status

```bash
# Tmux sessions
tmux ls

# Systemd services
sudo systemctl status market-api
sudo systemctl status twitter-wrapper
sudo systemctl status twitter-bot
```

### Log Files

```bash
# Application logs
tail -f logs/market_api.log
tail -f logs/twitter_wrapper.log
tail -f logs/twitter_bot.log

# System logs (if using systemd)
sudo journalctl -u market-api -f
sudo journalctl -u twitter-wrapper -f
sudo journalctl -u twitter-bot -f
```

### Database Monitoring

```bash
# Check market count
psql -d aigg_insights -c "SELECT COUNT(*) FROM polymarket_markets;"

# Check active markets
psql -d aigg_insights -c "SELECT COUNT(*) FROM polymarket_markets WHERE is_active = true;"

# Recent analyses
psql -d aigg_insights -c "SELECT created_at, query, market_title FROM analysis ORDER BY created_at DESC LIMIT 5;"
```

## Maintenance

### Daily Tasks

```bash
# Clean inactive markets
python scripts/cleanup_inactive_markets.py

# Update market data
python scripts/sync_polymarket_data.py
```

### Weekly Tasks

```bash
# Database vacuum
psql -d aigg_insights -c "VACUUM ANALYZE;"

# Log rotation
find logs/ -name "*.log" -mtime +7 -delete
```

### Backup

```bash
# Database backup
pg_dump aigg_insights > backups/aigg_$(date +%Y%m%d).sql

# Configuration backup
tar -czf backups/config_$(date +%Y%m%d).tar.gz .env *.json
```

## Troubleshooting

### Service Won't Start

1. Check port availability:
```bash
sudo lsof -i :8001  # Market API port
sudo lsof -i :8003  # Wrapper API port
```

2. Verify environment variables:
```bash
python -c "import os; print(os.getenv('DATABASE_URL'))"
```

3. Test database connection:
```bash
python -c "from src.utils.database import test_connection; test_connection()"
```

### High Response Times

1. Check database performance:
```bash
psql -d aigg_insights -c "SELECT * FROM pg_stat_activity;"
```

2. Monitor API response times:
```bash
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8001/health
```

3. Review rate limits in logs

### Twitter Bot Not Responding

1. Verify Twitter credentials:
```bash
python scripts/test_twitter_auth.py
```

2. Check mention polling:
```bash
tail -f logs/twitter_bot.log | grep "Checking mentions"
```

3. Review rate limit status

## Security Considerations

### API Key Management

- Store all keys in environment variables
- Never commit `.env` file to repository
- Rotate keys regularly
- Use separate keys for development/production

### Network Security

```bash
# Configure firewall
sudo ufw allow 22/tcp     # SSH
sudo ufw allow 8001/tcp   # Market API (restrict to localhost in production)
sudo ufw allow 8003/tcp   # Wrapper API (restrict to localhost in production)
sudo ufw enable
```

### Database Security

```bash
# Restrict database access
# Edit /etc/postgresql/14/main/pg_hba.conf
# Allow only local connections
```

### Process Isolation

- Run services as non-root user
- Use separate system users for each service
- Implement resource limits in systemd

## Scaling Deployment

### Multiple Instances

For high availability, deploy multiple instances behind a load balancer:

```bash
# Instance 1
python main.py api-server --port 8001 --instance 1

# Instance 2
python main.py api-server --port 8002 --instance 2
```

### Database Replication

Configure PostgreSQL streaming replication for read replicas:

```bash
# On primary
postgresql.conf:
wal_level = replica
max_wal_senders = 3
```

### Caching Layer

Add Redis for response caching:

```bash
# Install Redis
sudo apt-get install redis-server

# Configure in .env
REDIS_URL=redis://localhost:6379/0
```

## Performance Optimization

### Database Indexes

```sql
CREATE INDEX idx_markets_active ON polymarket_markets(is_active);
CREATE INDEX idx_markets_category ON polymarket_markets(category);
CREATE INDEX idx_markets_created ON polymarket_markets(created_at DESC);
```

### Connection Pooling

Configure in database utilities:
```python
pool_size=20
max_overflow=40
pool_timeout=30
```

### API Response Caching

Implement caching for frequent queries:
- Market search results: 5 minutes
- Health checks: 30 seconds
- Static data: 1 hour