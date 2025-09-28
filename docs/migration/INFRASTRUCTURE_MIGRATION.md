# 🚀 AIGG Infrastructure Migration Guide

**Target Server**: `cosmos@65.108.231.245`  
**Current Server**: `cosmos@37.27.54.184` (aigg-insights)

## 📊 Current Infrastructure Overview

Based on analysis, your current setup includes:
- **Twitter Bot**: Running in tmux session `aigg-twitter-bot`
- **Twitter Wrapper API**: Running in tmux session `twitter-wrapper` (port 8003)
- **Market API**: Likely running on port 8001
- **PostgreSQL Database**: With market data (51K+ markets)
- **Cron Jobs**: Hourly data sync + daily cleanup
- **Environment Variables**: Twitter API, DB, Perplexity API keys
- **Configuration**: Whitelist system with user access controls

## 🎯 Migration Strategy

**Zero-Downtime Approach**: Set up new server in parallel, then switch traffic

---

## Phase 1: New Server Preparation

### Step 1: SSH Setup & System Updates
```bash
# SSH into new server
ssh cosmos@65.108.231.245

# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y tmux curl wget git htop build-essential libpq-dev
```

### Step 2: PostgreSQL Setup
```bash
# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres createdb aigg_insights
sudo -u postgres psql -c "CREATE USER aigg_user WITH PASSWORD 'secure_password_here';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE aigg_insights TO aigg_user;"
```

### Step 3: Create Project Structure
```bash
# Create main directory
mkdir -p /home/cosmos/aigg-insights
cd /home/cosmos/aigg-insights

# Create necessary subdirectories
mkdir -p logs config scripts src api db
```

---

## Phase 2: Data Transfer

### Step 4: Code Transfer

**Option A - Archive Transfer (Recommended)**
```bash
# On current server (37.27.54.184)
cd /home/cosmos
tar --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' \
    -czf aigg-insights-backup.tar.gz aigg-insights/

# Transfer to new server
scp aigg-insights-backup.tar.gz cosmos@65.108.231.245:/home/cosmos/

# On new server (65.108.231.245)
cd /home/cosmos
tar -xzf aigg-insights-backup.tar.gz
```

**Option B - Direct SCP Transfer**
```bash
# From current server or local machine with access
scp -r cosmos@37.27.54.184:/home/cosmos/aigg-insights/* \
    cosmos@65.108.231.245:/home/cosmos/aigg-insights/
```

### Step 5: Database Migration
```bash
# On current server - Export database
pg_dump -h localhost -U postgres aigg_insights > aigg_dump.sql

# Transfer database dump
scp aigg_dump.sql cosmos@65.108.231.245:/home/cosmos/

# On new server - Import database
psql -h localhost -U aigg_user -d aigg_insights < /home/cosmos/aigg_dump.sql
```

---

## Phase 3: Environment Setup

### Step 6: Python Environment
```bash
cd /home/cosmos/aigg-insights

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### Step 7: Environment Configuration
```bash
# Create environment file
cat > .env << 'EOF'
# Database
DB_NAME=aigg_insights
DB_USER=aigg_user
DB_PASSWORD=secure_password_here
DB_HOST=localhost
DB_PORT=5432

# Twitter API (Copy from current server)
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_secret

# AI Services
PERPLEXITY_API_KEY=your_perplexity_key

# API Configuration
API_HOST=0.0.0.0
API_PORT=8001
WRAPPER_API_PORT=8003
EOF

# Secure the file
chmod 600 .env
```

### Step 8: System Services Setup

**Cron Jobs**
```bash
# Edit crontab
crontab -e

# Add these entries:
# Hourly Polymarket data sync
0 * * * * cd /home/cosmos/aigg-insights && source venv/bin/activate && python scripts/populate_polymarket_data_clob.py >> logs/polymarket_cron.log 2>&1

# Daily cleanup at 3 AM
0 3 * * * cd /home/cosmos/aigg-insights && venv/bin/python scripts/cleanup_inactive_markets.py --execute >> /var/log/aigg-cleanup.log 2>&1

# Disk space monitoring
0 * * * * /home/cosmos/disk_space_alert.sh
```

**Disk Space Alert Script**
```bash
cat > /home/cosmos/disk_space_alert.sh << 'EOF'
#!/bin/bash
THRESHOLD=85
CURRENT=$(df / | grep / | awk '{ print $5}' | sed 's/%//g')
if [ "$CURRENT" -gt "$THRESHOLD" ]; then
    echo "$(date): Disk space ${CURRENT}% on $(hostname)" >> /var/log/disk-alert.log
fi
EOF

chmod +x /home/cosmos/disk_space_alert.sh
```

---

## Phase 4: Service Deployment

### Step 9: Start Core Services
```bash
cd /home/cosmos/aigg-insights

# 1. Market API
tmux new-session -d -s aigg-api \
  'cd /home/cosmos/aigg-insights && source venv/bin/activate && uvicorn api.main:app --host 0.0.0.0 --port 8001'

# 2. Twitter Wrapper API
tmux new-session -d -s twitter-wrapper \
  'cd /home/cosmos/aigg-insights && source venv/bin/activate && python src/api_wrapper/twitter_wrapper.py'

# 3. Twitter Bot
tmux new-session -d -s aigg-twitter-bot \
  'cd /home/cosmos/aigg-insights && source venv/bin/activate && python main.py twitter-bot --interval 900 --disable-whitelist'
```

### Step 10: Verification Tests
```bash
# Check tmux sessions
tmux list-sessions

# Test API endpoints
curl http://localhost:8001/health
curl http://localhost:8003/health

# Test database connection
source venv/bin/activate
python -c "
import psycopg2
from dotenv import load_dotenv
import os
load_dotenv()
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM polymarket_markets;')
print(f'Market count: {cur.fetchone()[0]}')
conn.close()
print('Database connection: SUCCESS')
"

# Test Twitter connection
python -c "
import tweepy, os
from dotenv import load_dotenv
load_dotenv()
auth = tweepy.OAuthHandler(os.getenv('TWITTER_API_KEY'), os.getenv('TWITTER_API_SECRET'))
auth.set_access_token(os.getenv('TWITTER_ACCESS_TOKEN'), os.getenv('TWITTER_ACCESS_TOKEN_SECRET'))
api = tweepy.API(auth)
try:
    api.verify_credentials()
    print('Twitter API connection: SUCCESS')
except Exception as e:
    print(f'Twitter API connection: FAILED - {e}')
"
```

---

## Phase 5: Traffic Switch & Cleanup

### Step 11: Network Configuration
```bash
# Open firewall ports
sudo ufw allow 8001/tcp
sudo ufw allow 8003/tcp
sudo ufw allow 22/tcp
sudo ufw --force enable
```

### Step 12: Update External References
- Any monitoring systems pointing to `37.27.54.184:8001`
- Documentation referencing the old IP
- External API consumers
- DNS records if applicable

### Step 13: Final Verification
```bash
# Complete system test
echo "=== AIGG INFRASTRUCTURE STATUS ==="
echo "Services:"
tmux list-sessions | grep -E "(aigg-|twitter-wrapper)" && echo "✅ All services running"

echo "APIs:"
curl -s http://localhost:8001/health >/dev/null && echo "✅ Market API responding" || echo "❌ Market API down"
curl -s http://localhost:8003/health >/dev/null && echo "✅ Wrapper API responding" || echo "❌ Wrapper API down"

echo "Database:"
source venv/bin/activate
python -c "
import psycopg2
from dotenv import load_dotenv
import os
load_dotenv()
try:
    conn = psycopg2.connect(host=os.getenv('DB_HOST'), database=os.getenv('DB_NAME'), user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'))
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM polymarket_markets WHERE active = true;')
    count = cur.fetchone()[0]
    print(f'✅ Database active: {count} markets')
    conn.close()
except Exception as e:
    print(f'❌ Database error: {e}')
"

echo "Cron jobs:"
crontab -l | grep -q "polymarket_data_clob" && echo "✅ Cron jobs installed" || echo "❌ Cron jobs missing"
```

---

## 🚨 Emergency Rollback Procedure

If issues arise:

1. **Keep old server running** during migration
2. **Revert external references** back to `37.27.54.184`
3. **Troubleshoot new server** while old handles traffic
4. **Only shut down old server** after 24-48 hours of stable operation

---

## 📋 Pre-Migration Checklist

**Before starting migration:**
- [ ] Backup current server data
- [ ] Document all environment variables
- [ ] Note any custom configurations
- [ ] Verify SSH access to new server
- [ ] Plan maintenance window (if needed)

**Migration completion checklist:**
- [ ] All services running in tmux
- [ ] Database migrated with all data
- [ ] APIs responding correctly
- [ ] Cron jobs scheduled
- [ ] Environment variables set
- [ ] Twitter bot operational
- [ ] External references updated
- [ ] 24-hour monitoring period completed

---

## 🔧 Quick Commands Reference

**Service Management:**
```bash
# Check all services
tmux list-sessions

# Restart a service
tmux kill-session -t aigg-twitter-bot
tmux new-session -d -s aigg-twitter-bot 'cd /home/cosmos/aigg-insights && source venv/bin/activate && python main.py twitter-bot --interval 900 --disable-whitelist'

# View service logs
tmux attach-session -t aigg-twitter-bot  # Ctrl+B, D to detach

# Check system resources
htop
df -h
```

**Database Management:**
```bash
# Connect to database
psql -h localhost -U aigg_user -d aigg_insights

# Check market count
psql -h localhost -U aigg_user -d aigg_insights -c "SELECT COUNT(*) FROM polymarket_markets;"
```

**API Testing:**
```bash
# Test market search
curl "http://localhost:8001/markets/search?query=trump&limit=5"

# Health checks
curl http://localhost:8001/health
curl http://localhost:8003/health
```

---

**Estimated Migration Time**: 2-4 hours  
**Expected Downtime**: 0-15 minutes (during traffic switch)  
**Rollback Time**: 5-10 minutes if needed

**Post-Migration**: Monitor for 24-48 hours before decommissioning old server.

Good luck with the migration! 🚀 