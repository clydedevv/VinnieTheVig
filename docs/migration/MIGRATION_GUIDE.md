# 🚀 AIGG Infrastructure Migration Guide

**Migration from current server to: `cosmos@65.108.231.245`**

## 📋 Pre-Migration Checklist

### Current Server Analysis
Based on the current setup, you have:
- ✅ **Twitter Bot**: Running in tmux session `aigg-twitter-bot`
- ✅ **Twitter Wrapper API**: Running in tmux session `twitter-wrapper`  
- ✅ **Multiple tmux sessions**: 0, 5, 6, 9, polymarket
- ✅ **Cron jobs**: Hourly Polymarket data sync + daily cleanup
- ✅ **PostgreSQL Database**: With AIGG insights data
- ✅ **Configuration**: Whitelist, environment variables
- ✅ **Python environment**: Virtual environment with dependencies

### Migration Strategy
1. **Parallel Setup**: Set up new server while keeping current one running
2. **Data Transfer**: Copy codebase, database, and configurations
3. **Service Migration**: Move services one by one with testing
4. **DNS/Traffic Switch**: Update any external references
5. **Cleanup**: Shut down old server after verification

---

## 🔧 Step 1: System Setup on New Server

### SSH into New Server
```bash
ssh cosmos@65.108.231.245
```

### Install System Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and development tools
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y build-essential libpq-dev

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Install tmux and other utilities
sudo apt install -y tmux curl wget git htop
```

### Setup PostgreSQL
```bash
# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE aigg_insights;
CREATE USER postgres WITH PASSWORD 'your_db_password_here';
GRANT ALL PRIVILEGES ON DATABASE aigg_insights TO postgres;
ALTER USER postgres CREATEDB;
\q
EOF
```

---

## 📁 Step 2: Code Transfer

### Create Project Directory
```bash
cd /home/cosmos
mkdir -p aigg-insights
cd aigg-insights
```

### Transfer Codebase (Choose one method)

#### Method A: Git Clone (Recommended)
```bash
# If you have the code in a git repository
git clone <your-repo-url> .
```

#### Method B: Direct Transfer via SCP
```bash
# Run from your local machine or current server
scp -r /home/cosmos/aigg-insights/* cosmos@65.108.231.245:/home/cosmos/aigg-insights/
```

#### Method C: Create Archive and Transfer
```bash
# On current server
cd /home/cosmos
tar -czf aigg-backup.tar.gz aigg-insights/

# Transfer
scp aigg-backup.tar.gz cosmos@65.108.231.245:/home/cosmos/

# On new server
cd /home/cosmos
tar -xzf aigg-backup.tar.gz
```

---

## 🐍 Step 3: Python Environment Setup

```bash
cd /home/cosmos/aigg-insights

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import tweepy, psycopg2, requests; print('All packages installed successfully')"
```

---

## 🗄️ Step 4: Database Migration

### Export Database from Current Server
```bash
# On current server
cd /home/cosmos/aigg-insights
pg_dump -h localhost -U postgres aigg_insights > aigg_insights_backup.sql

# Transfer to new server
scp aigg_insights_backup.sql cosmos@65.108.231.245:/home/cosmos/
```

### Import Database on New Server
```bash
# On new server
cd /home/cosmos
psql -h localhost -U postgres -d aigg_insights < aigg_insights_backup.sql
```

### Verify Database
```bash
# Test database connection
cd /home/cosmos/aigg-insights
source venv/bin/activate
python -c "
import psycopg2
conn = psycopg2.connect(
    host='localhost',
    database='aigg_insights',
    user='postgres',
    password='your_db_password_here'
)
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM polymarket_markets;')
print(f'Market count: {cur.fetchone()[0]}')
conn.close()
"
```

---

## 🔐 Step 5: Environment Configuration

### Create Environment File
```bash
cd /home/cosmos/aigg-insights
cat > .env << 'EOF'
# Database Configuration
DB_NAME=aigg_insights
DB_USER=postgres
DB_PASSWORD=your_db_password_here
DB_HOST=localhost
DB_PORT=5432

# Twitter API Configuration
TWITTER_BEARER_TOKEN=your_bearer_token_here
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here

# AI Services
PERPLEXITY_API_KEY=your_perplexity_key_here

# API Configuration
API_HOST=0.0.0.0
API_PORT=8001
WRAPPER_API_PORT=8003
EOF

# Secure the environment file
chmod 600 .env
```

### Copy Configuration Files
```bash
# Ensure config directory exists
mkdir -p config

# The whitelist.json should already be in your transferred files
# Verify it exists:
ls -la config/whitelist.json
```

---

## ⚙️ Step 6: Service Setup

### Create Log Directory
```bash
mkdir -p /home/cosmos/aigg-insights/logs
mkdir -p /var/log  # For system logs (may need sudo)
```

### Setup Cron Jobs
```bash
# Edit crontab
crontab -e

# Add these lines:
# Disk space alert
0 * * * * /home/cosmos/disk_space_alert.sh

# Polymarket data population - runs every hour
0 * * * * cd /home/cosmos/aigg-insights && source venv/bin/activate && python scripts/populate_polymarket_data_clob.py >> /home/cosmos/aigg-insights/logs/polymarket_cron.log 2>&1

# Daily database cleanup (3 AM) - Removes expired markets
0 3 * * * cd /home/cosmos/aigg-insights && /home/cosmos/aigg-insights/venv/bin/python scripts/cleanup_inactive_markets.py --execute >> /var/log/aigg-cleanup.log 2>&1
```

### Create Disk Space Alert Script
```bash
cat > /home/cosmos/disk_space_alert.sh << 'EOF'
#!/bin/bash
# Disk space monitoring script
THRESHOLD=90
CURRENT=$(df / | grep / | awk '{ print $5}' | sed 's/%//g')
if [ "$CURRENT" -gt "$THRESHOLD" ]; then
    echo "Disk Space Alert: ${CURRENT}% used on $(hostname)" | logger
fi
EOF

chmod +x /home/cosmos/disk_space_alert.sh
```

---

## 🚀 Step 7: Start Services

### Test Individual Components First
```bash
cd /home/cosmos/aigg-insights
source venv/bin/activate

# Test Market API
python -c "
from api.main import app
import uvicorn
print('Market API test passed')
"

# Test Twitter Bot (dry run)
python main.py --help
```

### Start Services in tmux Sessions
```bash
cd /home/cosmos/aigg-insights

# 1. Market API
tmux new-session -d -s aigg-api 'cd /home/cosmos/aigg-insights && source venv/bin/activate && uvicorn api.main:app --host 0.0.0.0 --port 8001'

# 2. Twitter Wrapper API  
tmux new-session -d -s twitter-wrapper 'cd /home/cosmos/aigg-insights && source venv/bin/activate && python src/api_wrapper/twitter_wrapper.py'

# 3. Twitter Bot (with 15-minute intervals)
tmux new-session -d -s aigg-twitter-bot 'cd /home/cosmos/aigg-insights && source venv/bin/activate && python main.py twitter-bot --interval 900 --disable-whitelist'

# 4. Polymarket data sync (if needed as separate session)
# tmux new-session -d -s polymarket 'cd /home/cosmos/aigg-insights && source venv/bin/activate && python scripts/populate_polymarket_data_clob.py'
```

### Verify Services
```bash
# Check tmux sessions
tmux list-sessions

# Test API endpoints
curl http://localhost:8001/health
curl http://localhost:8003/health  # If wrapper API has health endpoint

# Check logs
tail -f logs/polymarket_cron.log
```

---

## 🔍 Step 8: Testing & Verification

### Test Market API
```bash
# Test market search
curl "http://localhost:8001/markets/search?query=trump&limit=5"

# Test health endpoint
curl "http://localhost:8001/health"
```

### Test Twitter Bot (if in development mode)
```bash
# Check if bot can connect to Twitter
cd /home/cosmos/aigg-insights
source venv/bin/activate
python -c "
import tweepy
import os
from dotenv import load_dotenv
load_dotenv()

auth = tweepy.OAuthHandler(os.getenv('TWITTER_API_KEY'), os.getenv('TWITTER_API_SECRET'))
auth.set_access_token(os.getenv('TWITTER_ACCESS_TOKEN'), os.getenv('TWITTER_ACCESS_TOKEN_SECRET'))
api = tweepy.API(auth)

try:
    api.verify_credentials()
    print('Twitter API connection successful')
except Exception as e:
    print(f'Twitter API connection failed: {e}')
"
```

### Monitor Services
```bash
# Check processes
ps aux | grep python
ps aux | grep uvicorn

# Monitor logs in real-time
tmux attach-session -t aigg-twitter-bot  # Ctrl+B, D to detach
tmux attach-session -t twitter-wrapper
tmux attach-session -t aigg-api
```

---

## 🌐 Step 9: Network Configuration

### Update Firewall (if needed)
```bash
# Allow API ports
sudo ufw allow 8001/tcp  # Market API
sudo ufw allow 8003/tcp  # Wrapper API
sudo ufw allow 22/tcp    # SSH
sudo ufw enable
```

### Update External References
- Update any external services pointing to `37.27.54.184:8001`
- Change to `65.108.231.245:8001`
- Update documentation, monitoring tools, etc.

---

## ✅ Step 10: Post-Migration Verification

### Complete System Test
```bash
# 1. Database connectivity
cd /home/cosmos/aigg-insights
source venv/bin/activate
python -c "
import psycopg2
from datetime import datetime
conn = psycopg2.connect(host='localhost', database='aigg_insights', user='postgres', password='your_password')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM polymarket_markets WHERE active = true;')
print(f'Active markets: {cur.fetchone()[0]}')
conn.close()
print('Database test: PASSED')
"

# 2. API functionality
curl -s "http://localhost:8001/health" | grep -q "status" && echo "API test: PASSED" || echo "API test: FAILED"

# 3. Cron jobs
crontab -l | grep -q "polymarket_data_clob" && echo "Cron test: PASSED" || echo "Cron test: FAILED"

# 4. Tmux sessions
tmux list-sessions | grep -q "aigg-twitter-bot" && echo "Twitter bot: RUNNING" || echo "Twitter bot: NOT RUNNING"
tmux list-sessions | grep -q "twitter-wrapper" && echo "Wrapper API: RUNNING" || echo "Wrapper API: NOT RUNNING"
tmux list-sessions | grep -q "aigg-api" && echo "Market API: RUNNING" || echo "Market API: NOT RUNNING"
```

---

## 📋 Migration Checklist

- [ ] **System Dependencies**: Python, PostgreSQL, tmux installed
- [ ] **Codebase**: All files transferred and verified
- [ ] **Database**: Exported, transferred, and imported successfully
- [ ] **Environment**: .env file created with all credentials
- [ ] **Configuration**: whitelist.json and other config files in place
- [ ] **Virtual Environment**: Created and dependencies installed
- [ ] **Cron Jobs**: Set up for data sync and cleanup
- [ ] **Services**: All tmux sessions running
- [ ] **APIs**: Market API and Wrapper API responding
- [ ] **Twitter Bot**: Connected and monitoring mentions
- [ ] **Logs**: Log directories created and writable
- [ ] **Firewall**: Ports opened if necessary
- [ ] **External References**: Updated to new server IP
- [ ] **Testing**: All components tested individually and together

---

## 🆘 Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Reset password if needed
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'new_password';"
```

#### Python Dependencies Issues
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### Port Already in Use
```bash
# Find and kill process using port
sudo lsof -ti:8001 | xargs sudo kill -9
sudo lsof -ti:8003 | xargs sudo kill -9
```

#### Tmux Session Issues
```bash
# Kill all sessions and restart
tmux kill-server
# Then restart services as shown in Step 7
```

---

## 🔄 Rollback Plan (If Needed)

If migration fails, you can quickly rollback:

1. **Keep Current Server Running**: Don't shut down until new server is verified
2. **Revert External References**: Change API endpoints back to old server
3. **Monitor Both Servers**: Ensure no data loss during migration
4. **Debug on New Server**: Fix issues while old server handles traffic

---

## 📞 Final Steps

1. **Test the complete flow**: Tweet at the bot, verify response
2. **Monitor for 24 hours**: Ensure stability
3. **Update documentation**: Record any configuration changes
4. **Backup new server**: Create initial backup after migration
5. **Shut down old server**: Only after complete verification

**Migration Target**: `cosmos@65.108.231.245`
**Estimated Time**: 2-4 hours depending on database size
**Downtime**: Minimal if done properly with parallel setup

Good luck with the migration! 🚀 