# AIGG Insights Migration Guide

**Complete checklist and instructions for migrating database and API infrastructure**

## 🎯 **Migration Overview**

This guide covers migrating the entire AIGG Insights system including:
- PostgreSQL database with 51K+ markets
- FastAPI service on port 8001
- Cron jobs for automated data sync
- Environment configurations

---

## 📋 **Pre-Migration Checklist**

### **Current System Inventory**
- [ ] Database: PostgreSQL with `polymarket_markets` table (51,093 markets)
- [ ] API: FastAPI service running on `http://37.27.54.184:8001`
- [ ] Cron: Hourly CLOB API sync (`populate_polymarket_data_clob.py`)
- [ ] Environment: Python 3.8+ with virtual environment
- [ ] Dependencies: Listed in `requirements.txt`

### **Critical Data to Backup**
- [ ] Full database dump
- [ ] Environment variables (`.env` file)
- [ ] Cron job configurations
- [ ] SSL certificates (if any)
- [ ] Log files for debugging

---

## 🗄️ **Database Migration**

### **1. Current Database Schema**
```sql
-- polymarket_markets table structure
CREATE TABLE polymarket_markets (
    market_id VARCHAR(255) PRIMARY KEY,
    title TEXT NOT NULL,
    category VARCHAR(255),
    end_date TIMESTAMP WITH TIME ZONE,
    active BOOLEAN DEFAULT true,
    last_refreshed TIMESTAMP DEFAULT NOW(),
    market_slug VARCHAR(500),  -- CRITICAL: For Polymarket URLs
    yes_price DECIMAL(10,6),
    no_price DECIMAL(10,6)
);

-- Indexes for performance
CREATE INDEX idx_polymarket_markets_active ON polymarket_markets(active);
CREATE INDEX idx_polymarket_markets_category ON polymarket_markets(category);
CREATE INDEX idx_polymarket_markets_end_date ON polymarket_markets(end_date);
CREATE INDEX idx_polymarket_markets_title ON polymarket_markets USING gin(to_tsvector('english', title));
```

### **2. Database Backup Commands**
```bash
# Full database dump
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > aigg_insights_backup_$(date +%Y%m%d_%H%M%S).sql

# Schema only (for new setup)
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME --schema-only > aigg_insights_schema.sql

# Data only (for data migration)
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME --data-only > aigg_insights_data.sql
```

### **3. Database Restore Commands**
```bash
# Create new database
createdb -h $NEW_DB_HOST -U $NEW_DB_USER $NEW_DB_NAME

# Restore full backup
psql -h $NEW_DB_HOST -U $NEW_DB_USER -d $NEW_DB_NAME < aigg_insights_backup_YYYYMMDD_HHMMSS.sql

# Or restore schema + data separately
psql -h $NEW_DB_HOST -U $NEW_DB_USER -d $NEW_DB_NAME < aigg_insights_schema.sql
psql -h $NEW_DB_HOST -U $NEW_DB_USER -d $NEW_DB_NAME < aigg_insights_data.sql
```

---

## 🔧 **Environment Configuration**

### **Required Environment Variables**
```bash
# Database Configuration
DB_NAME=aigg_insights_production
DB_USER=your_username
DB_PASSWORD=your_secure_password
DB_HOST=your_new_host
DB_PORT=5432

# API Keys
PERPLEXITY_API_KEY=your_perplexity_key

# Optional: API Configuration
API_HOST=0.0.0.0
API_PORT=8001
```

### **Environment Setup Script**
```bash
#!/bin/bash
# setup_environment.sh

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (fill in actual values)
cat > .env << EOF
DB_NAME=aigg_insights_production
DB_USER=your_username
DB_PASSWORD=your_secure_password
DB_HOST=your_new_host
DB_PORT=5432
PERPLEXITY_API_KEY=your_perplexity_key
EOF

# Create logs directory
mkdir -p logs

# Set permissions
chmod +x scripts/*.py
chmod 644 .env
```

---

## 📦 **Application Dependencies**

### **Current requirements.txt**
```txt
fastapi==0.104.1
uvicorn==0.24.0
psycopg2-binary==2.9.7
python-dotenv==1.0.0
requests==2.31.0
pydantic==2.4.2
python-multipart==0.0.6
```

### **System Dependencies**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv postgresql-client

# CentOS/RHEL
sudo yum install -y python3 python3-pip postgresql

# Python version requirement
python3 --version  # Should be 3.8+
```

---

## 🚀 **API Service Migration**

### **Current API Configuration**
- **Port**: 8001
- **Host**: 0.0.0.0 (all interfaces)
- **CORS**: Enabled for all origins
- **Endpoints**: `/health`, `/markets/search`, `/markets`, `/categories`

### **API Startup Commands**
```bash
# Development
uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload

# Production
uvicorn api.main:app --host 0.0.0.0 --port 8001

# Background process
nohup uvicorn api.main:app --host 0.0.0.0 --port 8001 > logs/api.log 2>&1 &
```

### **Systemd Service (Production)**
```ini
# /etc/systemd/system/aigg-api.service
[Unit]
Description=AIGG Insights API
After=network.target

[Service]
Type=simple
User=cosmos
WorkingDirectory=/home/cosmos/aigg-insights
Environment=PATH=/home/cosmos/aigg-insights/venv/bin
ExecStart=/home/cosmos/aigg-insights/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
```

### **Firewall Configuration**
```bash
# Open API port
sudo ufw allow 8001/tcp

# Check status
sudo ufw status
```

---

## ⏰ **Cron Job Migration**

### **Current Cron Configuration**
```bash
# Enhanced Polymarket data population using CLOB API - runs every hour
0 * * * * cd /home/cosmos/aigg-insights && source venv/bin/activate && python scripts/populate_polymarket_data_clob.py >> /home/cosmos/aigg-insights/logs/polymarket_cron.log 2>&1
```

### **Cron Setup Commands**
```bash
# Backup current crontab
crontab -l > crontab_backup.txt

# Edit crontab
crontab -e

# Add the line:
0 * * * * cd /PATH/TO/NEW/LOCATION/aigg-insights && source venv/bin/activate && python scripts/populate_polymarket_data_clob.py >> /PATH/TO/NEW/LOCATION/aigg-insights/logs/polymarket_cron.log 2>&1

# Verify cron is running
service cron status
```

---

## 🔄 **Data Sync Process**

### **CLOB API Sync Script**
- **File**: `scripts/populate_polymarket_data_clob.py`
- **Function**: Fetches all markets from Polymarket CLOB API
- **Features**: Pagination, market slug extraction, automatic cleanup
- **Runtime**: ~5-10 minutes for full sync

### **Testing Data Sync**
```bash
# Test manual sync
cd /path/to/aigg-insights
source venv/bin/activate
python scripts/populate_polymarket_data_clob.py

# Check database after sync
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT COUNT(*) FROM polymarket_markets;"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT COUNT(*) FROM polymarket_markets WHERE active = true;"
```

---

## ✅ **Migration Steps**

### **Phase 1: Preparation**
1. [ ] Backup current database completely
2. [ ] Document current environment variables
3. [ ] Export cron job configuration
4. [ ] Test backup restoration on local environment
5. [ ] Prepare new server environment

### **Phase 2: Database Migration**
1. [ ] Set up new PostgreSQL instance
2. [ ] Create database and user
3. [ ] Restore schema to new database
4. [ ] Restore data to new database
5. [ ] Verify data integrity and indexes
6. [ ] Test database connectivity

### **Phase 3: Application Migration**
1. [ ] Clone repository to new server
2. [ ] Set up Python virtual environment
3. [ ] Install dependencies
4. [ ] Configure environment variables
5. [ ] Test database connection
6. [ ] Start API service
7. [ ] Verify all endpoints working

### **Phase 4: Automation Setup**
1. [ ] Configure cron job for data sync
2. [ ] Set up systemd service (if production)
3. [ ] Configure firewall rules
4. [ ] Set up log rotation
5. [ ] Test automated data sync

### **Phase 5: Validation**
1. [ ] Test all API endpoints
2. [ ] Verify enhanced AIGG flow works
3. [ ] Check database auto-updates
4. [ ] Monitor logs for errors
5. [ ] Performance testing

### **Phase 6: DNS/Traffic Switch**
1. [ ] Update DNS records (if applicable)
2. [ ] Update client configurations
3. [ ] Monitor new system
4. [ ] Keep old system as backup for 48 hours

---

## 🔍 **Testing Checklist**

### **Database Tests**
```bash
# Test connection
psql -h $NEW_DB_HOST -U $NEW_DB_USER -d $NEW_DB_NAME -c "SELECT 1;"

# Check market count
psql -h $NEW_DB_HOST -U $NEW_DB_USER -d $NEW_DB_NAME -c "SELECT COUNT(*) as total_markets FROM polymarket_markets;"

# Check active markets
psql -h $NEW_DB_HOST -U $NEW_DB_USER -d $NEW_DB_NAME -c "SELECT COUNT(*) as active_markets FROM polymarket_markets WHERE active = true;"

# Check market slugs
psql -h $NEW_DB_HOST -U $NEW_DB_USER -d $NEW_DB_NAME -c "SELECT COUNT(*) as markets_with_slugs FROM polymarket_markets WHERE market_slug IS NOT NULL AND market_slug != '';"
```

### **API Tests**
```bash
# Health check
curl http://NEW_SERVER_IP:8001/health

# Search test
curl "http://NEW_SERVER_IP:8001/markets/search?q=bitcoin&limit=3"

# Market list test
curl "http://NEW_SERVER_IP:8001/markets?limit=5"

# Categories test
curl "http://NEW_SERVER_IP:8001/categories"
```

### **Enhanced AIGG Flow Test**
```bash
# Test the complete AI pipeline
python test_single_query.py

# Test comprehensive flow
python enhanced_aigg_flow.py
```

---

## 🚨 **Rollback Plan**

### **If Migration Fails**
1. [ ] Stop new services immediately
2. [ ] Revert DNS changes (if made)
3. [ ] Restart old services
4. [ ] Investigate issues using logs
5. [ ] Fix issues and retry migration

### **Rollback Commands**
```bash
# Stop new API
pkill -f "uvicorn api.main:app"

# Restart old API (if needed)
cd /old/path/aigg-insights
source venv/bin/activate
uvicorn api.main:app --host 0.0.0.0 --port 8001 &
```

---

## 📞 **Contact Information**

### **Critical System Information**
- **Database**: PostgreSQL with 51,093 markets
- **API Port**: 8001
- **Sync Frequency**: Hourly
- **Dependencies**: Perplexity API key required
- **Performance**: ~3,168 active markets, sub-second search

### **Migration Support**
- Test all endpoints after migration
- Monitor logs for first 24 hours
- Keep backup system running for 48 hours
- Document any issues for future migrations

---

**🎯 This guide ensures zero-downtime migration with full data integrity!** 