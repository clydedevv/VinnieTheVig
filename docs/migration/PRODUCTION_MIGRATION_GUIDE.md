# 🚀 AIGG Insights - Production Migration Guide

**Complete production system migration for the AI-powered Twitter bot ecosystem**

---

## 🎯 **Production System Overview**

### **Current Live Production Setup**
- 🤖 **Twitter Bot**: @aigginsights (live on Twitter, 15-minute cycles)
- 🌐 **Market API**: Port 8001 (51K+ markets, public access)
- 🔗 **Twitter Wrapper API**: Port 8003 (internal AI analysis)
- 🗄️ **PostgreSQL**: 3,168 active markets (optimized from 51K)
- 🧠 **AI Pipeline**: R1-1776 reasoning with Perplexity integration
- ⚡ **Background Services**: Tmux sessions + cron automation
- 🔐 **Access Control**: 4-tier whitelist system

### **Services Architecture**
```
Twitter Mentions → Twitter Bot → Wrapper API → Enhanced AI Flow
     ↓               ↓             ↓              ↓
Rate Limiting    Market Search   R1-1776      Professional
Management      (3.2K markets)   Analysis      Responses
```

---

## 📋 **Pre-Migration Production Inventory**

### **🤖 Live Twitter Bot Services**
- [ ] **Main Bot**: `tmux session: aigg-twitter-bot`
  - Command: `python main.py twitter-bot --interval 900 --disable-whitelist`
  - Rate limiting: 15-minute cycles (Twitter Free tier)
  - Status: Live monitoring @aigginsights mentions
  
- [ ] **Twitter Wrapper API**: `tmux session: twitter-wrapper`
  - Command: `python src/api_wrapper/twitter_wrapper.py`
  - Port: 8003 (internal)
  - Status: FastAPI service for AI analysis

- [ ] **Market API**: `tmux session: market-api`
  - Command: `uvicorn api.main:app --host 0.0.0.0 --port 8001`
  - Port: 8001 (public)
  - Status: Live market search service

### **🗄️ Enhanced Database Status**
- [ ] **Optimized Markets**: 3,168 active (from 51,093 total)
- [ ] **Performance**: 10x faster after 94% cleanup
- [ ] **Automation**: Daily cleanup at 3 AM
- [ ] **Indexes**: Enhanced for fuzzy + semantic search

### **⏰ Production Automation**
- [ ] **Hourly Sync**: Market data from Polymarket CLOB API
- [ ] **Daily Cleanup**: Removes expired markets (3 AM)
- [ ] **Auto-Recovery**: Twitter rate limit handling
- [ ] **Health Monitoring**: Automatic service restart

### **🔐 Twitter API Configuration**
- [ ] **Rate Limits**: 1 search per 15 minutes (Free tier)
- [ ] **Bot Info**: Hard-coded (ID: 1929305566611947520)
- [ ] **Access Control**: 4-tier whitelist system
- [ ] **Error Handling**: Comprehensive tweepy integration

---

## 🔧 **Complete Environment Configuration**

### **Production Environment Variables**
```bash
# Database (Production PostgreSQL)
DB_NAME=aigg_insights
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Twitter API (Free Tier Optimized)
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret

# AI Services (Production)
PERPLEXITY_API_KEY=your_perplexity_key

# API Configuration
API_HOST=0.0.0.0
API_PORT=8001
WRAPPER_API_PORT=8003

# Bot Configuration
BOT_USERNAME=aigginsights
BOT_USER_ID=1929305566611947520
ADMIN_USER_ID=195487174
ADMIN_USERNAME=clydedevv
```

### **Production Dependencies (Current)**
```txt
# Core Framework
fastapi==0.104.1
uvicorn==0.24.0

# Database
psycopg2-binary==2.9.7
sqlalchemy==2.0.23

# Twitter Integration
tweepy==4.14.0

# AI Services
openai==1.3.6
requests==2.31.0

# Utilities
python-dotenv==1.0.0
pydantic==2.4.2
python-multipart==0.0.6
schedule==1.2.0
```

---

## 🗄️ **Enhanced Database Migration**

### **Production Database Schema (Current)**
```sql
-- Optimized polymarket_markets table
CREATE TABLE polymarket_markets (
    market_id VARCHAR(255) PRIMARY KEY,
    title TEXT NOT NULL,
    category VARCHAR(255),
    end_date TIMESTAMP WITH TIME ZONE,
    active BOOLEAN DEFAULT true,
    last_refreshed TIMESTAMP DEFAULT NOW(),
    market_slug VARCHAR(500) NOT NULL,  -- CRITICAL for Polymarket URLs
    yes_price DECIMAL(10,6),
    no_price DECIMAL(10,6),
    volume DECIMAL(15,2),
    liquidity DECIMAL(15,2),
    outcome_prices JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Enhanced performance indexes
CREATE INDEX idx_polymarket_markets_active ON polymarket_markets(active);
CREATE INDEX idx_polymarket_markets_category ON polymarket_markets(category);
CREATE INDEX idx_polymarket_markets_end_date ON polymarket_markets(end_date);
CREATE INDEX idx_polymarket_markets_slug ON polymarket_markets(market_slug);
CREATE INDEX idx_polymarket_markets_title_gin ON polymarket_markets USING gin(to_tsvector('english', title));
CREATE INDEX idx_polymarket_markets_volume ON polymarket_markets(volume DESC);

-- Whitelist table for access control
CREATE TABLE user_whitelist (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) UNIQUE NOT NULL,
    username VARCHAR(100),
    tier VARCHAR(20) DEFAULT 'whitelist', -- admin, vip, whitelist, blocked
    created_at TIMESTAMP DEFAULT NOW(),
    last_active TIMESTAMP,
    request_count INTEGER DEFAULT 0,
    daily_limit INTEGER DEFAULT 10
);

-- Insert production users
INSERT INTO user_whitelist (user_id, username, tier, daily_limit) VALUES
('195487174', 'clydedevv', 'admin', 1000),
('2163943230', 'AnkMister', 'vip', 50),
('1420819293894287364', '0xTraiano', 'vip', 50);
```

### **Database Backup & Restore (Production)**
```bash
# Complete production backup
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME \
  --verbose --clean --create \
  > aigg_production_backup_$(date +%Y%m%d_%H%M%S).sql

# Backup only active markets (recommended)
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME \
  --table=polymarket_markets \
  --table=user_whitelist \
  --where="active = true OR tier IS NOT NULL" \
  > aigg_active_data_$(date +%Y%m%d_%H%M%S).sql

# Restore on new server
createdb -h $NEW_DB_HOST -U $NEW_DB_USER $NEW_DB_NAME
psql -h $NEW_DB_HOST -U $NEW_DB_USER -d $NEW_DB_NAME < aigg_production_backup_*.sql

# Verify migration
psql -h $NEW_DB_HOST -U $NEW_DB_USER -d $NEW_DB_NAME -c "
  SELECT 
    COUNT(*) as total_markets,
    COUNT(*) FILTER (WHERE active = true) as active_markets,
    COUNT(*) FILTER (WHERE market_slug IS NOT NULL) as markets_with_slugs
  FROM polymarket_markets;
"
```

---

## 🤖 **Twitter Bot System Migration**

### **Current Production Configuration**
```json
{
  "bot": {
    "username": "aigginsights",
    "user_id": "1929305566611947520",
    "interval_seconds": 900,
    "rate_limit_strategy": "twitter_free_tier",
    "whitelist_enabled": false
  },
  "admin": {
    "username": "clydedevv",
    "user_id": "195487174"
  },
  "apis": {
    "market_search": "http://localhost:8001",
    "twitter_wrapper": "http://localhost:8003",
    "perplexity": "https://api.perplexity.ai"
  }
}
```

### **Tmux Session Migration**
```bash
# 1. Stop current production services
tmux kill-session -t aigg-twitter-bot 2>/dev/null
tmux kill-session -t twitter-wrapper 2>/dev/null
tmux kill-session -t market-api 2>/dev/null

# 2. Setup new server tmux sessions
# Twitter Bot (Main service)
tmux new-session -d -s aigg-twitter-bot \
  'cd /new/path/aigg-insights && source venv/bin/activate && python main.py twitter-bot --interval 900 --disable-whitelist'

# Twitter Wrapper API
tmux new-session -d -s twitter-wrapper \
  'cd /new/path/aigg-insights && source venv/bin/activate && python src/api_wrapper/twitter_wrapper.py'

# Market API
tmux new-session -d -s market-api \
  'cd /new/path/aigg-insights && source venv/bin/activate && uvicorn api.main:app --host 0.0.0.0 --port 8001'

# 3. Verify all sessions running
tmux list-sessions
```

### **Service Health Verification**
```bash
# Check Twitter bot logs
tmux capture-pane -t aigg-twitter-bot -p | tail -20

# Check wrapper API
curl http://localhost:8003/health

# Check market API
curl http://localhost:8001/health

# Test complete pipeline
python external_client.py analyze "Bitcoin 200k prediction"
```

---

## 🧠 **AI Analysis Pipeline Migration**

### **Enhanced Flow Components**
1. **Query Processing**: Natural language understanding
2. **Market Discovery**: Fuzzy + semantic search 
3. **AI Research**: Perplexity Sonar real-time news
4. **Analysis Generation**: R1-1776 reasoning model
5. **Response Formatting**: Twitter-optimized output

### **AI Service Configuration**
```python
# Enhanced AI flow settings
AI_CONFIG = {
    "perplexity": {
        "model": "llama-3.1-sonar-large-128k-online",
        "reasoning_model": "llama-3.1-sonar-huge-128k-online", # R1-1776
        "max_tokens": 2000,
        "temperature": 0.1
    },
    "market_selection": {
        "max_candidates": 10,
        "ai_selection": True,
        "fuzzy_threshold": 0.6
    },
    "response_formatting": {
        "max_length": 280,
        "preserve_urls": True,
        "sentence_boundary": True
    }
}
```

---

## ⏰ **Production Automation Migration**

### **Enhanced Cron Jobs (Current)**
```bash
# Hourly market sync (enhanced CLOB API)
0 * * * * cd /new/path/aigg-insights && source venv/bin/activate && \
python scripts/populate_polymarket_data_clob.py >> logs/polymarket_cron.log 2>&1

# Daily database cleanup (3 AM) - Removes expired markets
0 3 * * * cd /new/path/aigg-insights && source venv/bin/activate && \
python scripts/cleanup_inactive_markets.py --execute >> logs/cleanup.log 2>&1

# Weekly whitelist cleanup (Sunday 2 AM)
0 2 * * 0 cd /new/path/aigg-insights && source venv/bin/activate && \
python scripts/manage_whitelist.py cleanup >> logs/whitelist.log 2>&1
```

### **Systemd Services (Production Alternative)**
```ini
# /etc/systemd/system/aigg-twitter-bot.service
[Unit]
Description=AIGG Twitter Bot
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=cosmos
WorkingDirectory=/home/cosmos/aigg-insights
Environment=PATH=/home/cosmos/aigg-insights/venv/bin
ExecStart=/home/cosmos/aigg-insights/venv/bin/python main.py twitter-bot --interval 900
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# /etc/systemd/system/aigg-wrapper-api.service
[Unit]
Description=AIGG Twitter Wrapper API
After=network.target

[Service]
Type=simple
User=cosmos
WorkingDirectory=/home/cosmos/aigg-insights
Environment=PATH=/home/cosmos/aigg-insights/venv/bin
ExecStart=/home/cosmos/aigg-insights/venv/bin/python src/api_wrapper/twitter_wrapper.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

## ✅ **Complete Production Migration Steps**

### **Phase 1: System Preparation (30 minutes)**
1. [ ] Stop current production services gracefully
   ```bash
   tmux kill-session -t aigg-twitter-bot
   tmux kill-session -t twitter-wrapper
   tmux kill-session -t market-api
   ```

2. [ ] Create complete backup
   ```bash
   pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > full_backup.sql
   tar -czf aigg_backup_$(date +%Y%m%d).tar.gz . --exclude=venv --exclude=logs
   ```

3. [ ] Document current state
   ```bash
   crontab -l > current_crontab.txt
   tmux list-sessions > current_sessions.txt
   env | grep -E "(TWITTER|DB|PERPLEXITY)" > current_env.txt
   ```

### **Phase 2: New Server Setup (45 minutes)**
1. [ ] Clone repository to new server
   ```bash
   git clone https://github.com/your-repo/aigg-insights
   cd aigg-insights
   ```

2. [ ] Setup Python environment
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. [ ] Configure environment variables
   ```bash
   cp .env.example .env
   # Fill in production values
   ```

4. [ ] Setup PostgreSQL
   ```bash
   sudo apt install postgresql postgresql-contrib
   sudo -u postgres createuser -s aigg_user
   sudo -u postgres createdb aigg_insights
   ```

### **Phase 3: Database Migration (20 minutes)**
1. [ ] Restore database
   ```bash
   psql -h $NEW_DB_HOST -U $NEW_DB_USER -d $NEW_DB_NAME < full_backup.sql
   ```

2. [ ] Verify data integrity
   ```bash
   python -c "
   from api.database import get_db_connection
   conn = get_db_connection()
   cursor = conn.cursor()
   cursor.execute('SELECT COUNT(*) FROM polymarket_markets WHERE active = true')
   print(f'Active markets: {cursor.fetchone()[0]}')
   "
   ```

### **Phase 4: Service Migration (30 minutes)**
1. [ ] Start market API
   ```bash
   tmux new-session -d -s market-api \
     'uvicorn api.main:app --host 0.0.0.0 --port 8001'
   ```

2. [ ] Start wrapper API
   ```bash
   tmux new-session -d -s twitter-wrapper \
     'python src/api_wrapper/twitter_wrapper.py'
   ```

3. [ ] Start Twitter bot
   ```bash
   tmux new-session -d -s aigg-twitter-bot \
     'python main.py twitter-bot --interval 900 --disable-whitelist'
   ```

### **Phase 5: Automation Setup (15 minutes)**
1. [ ] Setup cron jobs
   ```bash
   crontab -e
   # Add production cron entries
   ```

2. [ ] Configure log rotation
   ```bash
   sudo nano /etc/logrotate.d/aigg-insights
   ```

### **Phase 6: Production Validation (30 minutes)**
1. [ ] Test all APIs
   ```bash
   curl http://localhost:8001/health
   curl http://localhost:8003/health
   ```

2. [ ] Test Twitter bot pipeline
   ```bash
   python external_client.py analyze "Test migration query"
   ```

3. [ ] Monitor logs for 24 hours
   ```bash
   tail -f logs/aigg_twitter_bot.log
   tail -f logs/twitter_wrapper.log
   ```

---

## 🔍 **Production Testing Checklist**

### **Core Functionality Tests**
```bash
# 1. Database connectivity
python -c "from api.database import get_db_connection; print('DB OK' if get_db_connection() else 'DB FAIL')"

# 2. Market search performance
time curl "http://localhost:8001/markets/search?q=bitcoin&limit=10"

# 3. AI analysis pipeline
python external_client.py analyze "Will Bitcoin hit 200k in 2025?"

# 4. Twitter API connection
python -c "
from src.twitter.client import TwitterClient
client = TwitterClient()
print('Twitter OK' if client.api else 'Twitter FAIL')
"

# 5. Whitelist system
python scripts/manage_whitelist.py stats

# 6. Complete AI flow
python main.py analyze "Russia Ukraine ceasefire before July"
```

### **Performance Benchmarks**
- **Market Search**: < 1 second for 10 results
- **AI Analysis**: 13-25 seconds total response time
- **Database Queries**: < 500ms for complex searches
- **Twitter Response**: Within 15-minute rate limit cycle

---

## 🚨 **Rollback Plan & Emergency Procedures**

### **Immediate Rollback (if migration fails)**
1. [ ] **Stop new services**
   ```bash
   tmux kill-session -t aigg-twitter-bot
   tmux kill-session -t twitter-wrapper
   tmux kill-session -t market-api
   ```

2. [ ] **Restart old services**
   ```bash
   cd /old/path/aigg-insights
   # Use old tmux sessions or manual startup
   ```

3. [ ] **Verify old system operational**
   ```bash
   curl http://old-server:8001/health
   ```

### **Data Recovery**
```bash
# If database corruption
psql -h $OLD_DB_HOST -U $OLD_DB_USER -d $OLD_DB_NAME < full_backup.sql

# If partial data loss
python scripts/populate_polymarket_data_clob.py --force-refresh
```

---

## 📊 **Post-Migration Monitoring**

### **24-Hour Monitoring Checklist**
- [ ] **Twitter Bot**: Responding to mentions within 15-minute cycles
- [ ] **Database**: Auto-updating hourly, cleanup running daily
- [ ] **APIs**: Both port 8001 and 8003 responding
- [ ] **AI Analysis**: Professional quality responses (no generic text)
- [ ] **Rate Limits**: No Twitter API violations
- [ ] **Performance**: Response times within benchmarks

### **Weekly Health Checks**
```bash
# System stats
python main.py status

# Database health
python -c "
from api.database import get_db_connection
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute('''
  SELECT 
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE active = true) as active,
    COUNT(*) FILTER (WHERE last_refreshed > NOW() - INTERVAL \'24 hours\') as recent
  FROM polymarket_markets
''')
print(cursor.fetchone())
"

# Log analysis
grep -c "SUCCESS" logs/aigg_twitter_bot.log | tail -7  # Last 7 days
```

---

## 🎯 **Migration Success Criteria**

### **✅ Production Ready When:**
- [ ] All tmux sessions running stably
- [ ] Twitter bot responding to mentions (test with admin account)
- [ ] Database showing 3,000+ active markets
- [ ] APIs returning < 1 second response times
- [ ] AI analysis producing professional insights (no generic responses)
- [ ] Cron jobs running automatically
- [ ] Logs showing no critical errors
- [ ] Rate limiting properly configured (15-minute intervals)

### **🚀 Go-Live Confirmation**
Tweet from admin account: `@aigginsights Test migration - Bitcoin 200k?`

Expected response within 15 minutes:
```
Q: Bitcoin 200k?
💡 ETF inflows up 40%, Fed rate cuts boost risk appetite, but $45k 
resistance remains key level for sustained breakout
📈 BUY - technical momentum (72%)
https://polymarket.com/event/will-bitcoin-reach-200000-by-december-31-2025
```

---

**🎉 Migration Complete! Production system ready for scale!** 🚀

*Total migration time: ~2.5 hours with proper preparation* 