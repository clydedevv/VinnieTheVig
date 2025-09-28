# AIGG Infrastructure Migration Guide

**Migrating from**: Current server (37.27.54.184)  
**Migrating to**: cosmos@65.108.231.245

## Current Setup Analysis

From your current server, I can see:
- **Twitter Bot**: aigg-twitter-bot tmux session
- **Twitter Wrapper**: twitter-wrapper tmux session  
- **Multiple tmux sessions**: 0, 5, 6, 9, polymarket
- **Cron jobs**: Hourly Polymarket sync + daily cleanup
- **PostgreSQL database**: With market data
- **Whitelist system**: VIP/Admin access controls

## Complete Migration Steps

### 1. Prepare New Server

SSH into new server:
```bash
ssh cosmos@65.108.231.245
```

Install system dependencies:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y tmux curl wget git htop build-essential libpq-dev
```

Setup PostgreSQL:
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo -u postgres createdb aigg_insights
sudo -u postgres psql -c "CREATE USER aigg_user WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE aigg_insights TO aigg_user;"
```

### 2. Transfer Your Codebase

Create project directory:
```bash
mkdir -p /home/cosmos/aigg-insights
cd /home/cosmos/aigg-insights
```

Transfer code (run from current server):
```bash
cd /home/cosmos
tar --exclude='venv' --exclude='__pycache__' -czf aigg-backup.tar.gz aigg-insights/
scp aigg-backup.tar.gz cosmos@65.108.231.245:/home/cosmos/
```

Extract on new server:
```bash
cd /home/cosmos
tar -xzf aigg-backup.tar.gz
```

### 3. Database Migration

Export from current server:
```bash
pg_dump -h localhost -U postgres aigg_insights > aigg_db_backup.sql
scp aigg_db_backup.sql cosmos@65.108.231.245:/home/cosmos/
```

Import to new server:
```bash
psql -h localhost -U aigg_user -d aigg_insights < /home/cosmos/aigg_db_backup.sql
```

### 4. Python Environment

```bash
cd /home/cosmos/aigg-insights
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Environment Configuration

Create .env file:
```bash
cat > .env << 'EOF'
DB_NAME=aigg_insights
DB_USER=aigg_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Copy these from your current server's environment
TWITTER_BEARER_TOKEN=
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_TOKEN_SECRET=
PERPLEXITY_API_KEY=

API_HOST=0.0.0.0
API_PORT=8001
WRAPPER_API_PORT=8003
EOF

chmod 600 .env
```

### 6. Setup Cron Jobs

```bash
crontab -e
```

Add these lines:
```bash
0 * * * * cd /home/cosmos/aigg-insights && source venv/bin/activate && python scripts/populate_polymarket_data_clob.py >> logs/polymarket_cron.log 2>&1
0 3 * * * cd /home/cosmos/aigg-insights && venv/bin/python scripts/cleanup_inactive_markets.py --execute >> /var/log/aigg-cleanup.log 2>&1
```

### 7. Start Services

```bash
cd /home/cosmos/aigg-insights

# Market API
tmux new-session -d -s aigg-api 'cd /home/cosmos/aigg-insights && source venv/bin/activate && uvicorn api.main:app --host 0.0.0.0 --port 8001'

# Twitter Wrapper
tmux new-session -d -s twitter-wrapper 'cd /home/cosmos/aigg-insights && source venv/bin/activate && python src/api_wrapper/twitter_wrapper.py'

# Twitter Bot
tmux new-session -d -s aigg-twitter-bot 'cd /home/cosmos/aigg-insights && source venv/bin/activate && python main.py twitter-bot --interval 900 --disable-whitelist'
```

### 8. Verify Everything Works

Check services:
```bash
tmux list-sessions
curl http://localhost:8001/health
curl http://localhost:8003/health
```

Test database:
```bash
source venv/bin/activate
python -c "
import psycopg2, os
from dotenv import load_dotenv
load_dotenv()
conn = psycopg2.connect(host='localhost', database='aigg_insights', user='aigg_user', password=os.getenv('DB_PASSWORD'))
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM polymarket_markets;')
print(f'Markets: {cur.fetchone()[0]}')
conn.close()
"
```

### 9. Open Firewall Ports

```bash
sudo ufw allow 8001/tcp
sudo ufw allow 8003/tcp
sudo ufw enable
```

### 10. Final Testing

Test the complete flow:
- API endpoints responding
- Database queries working
- Twitter bot can authenticate
- All tmux sessions running

## Migration Checklist

- [ ] New server prepared with dependencies
- [ ] Code transferred and extracted
- [ ] Database exported and imported
- [ ] Python environment created
- [ ] Environment variables configured
- [ ] Cron jobs scheduled
- [ ] All services started in tmux
- [ ] APIs responding correctly
- [ ] Database connection verified
- [ ] Firewall configured
- [ ] Complete system tested

## Emergency Rollback

If anything goes wrong:
1. Keep old server running during migration
2. Can revert external references back to 37.27.54.184
3. Debug new server while old handles traffic
4. Only shutdown old server after 24h+ of stable operation

**Estimated time**: 2-4 hours
**Expected downtime**: Minimal (parallel setup)

The migration is designed to be reversible and low-risk. Take your time with each step and verify before proceeding! 