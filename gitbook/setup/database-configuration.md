# Database Configuration

Detailed guide for configuring PostgreSQL database for AIGG Insights.

## Initial Database Setup

### 1. Create Database Structure

Run the initialization script:

```bash
python main.py database init
```

This command will:
- Create all required tables
- Set up indexes
- Configure constraints
- Initialize default data

### 2. Manual Schema Creation

If you prefer manual setup, run these SQL commands:

```sql
-- Connect to database
psql -U aigg_user -d aigg_insights

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Run schema creation script
\i scripts/database/create_schema.sql
```

## Loading Market Data

### 1. Initial Market Import

Load Polymarket markets from API:

```bash
python main.py database load-markets --full
```

Options:
- `--full`: Load all available markets
- `--active`: Load only active markets (~3K)
- `--category [name]`: Load specific category

### 2. Incremental Updates

Set up automatic market updates:

```bash
# Add to crontab for hourly updates
0 * * * * cd /path/to/aigg-insights && python main.py database update-markets
```

### 3. Market Data Validation

```bash
python main.py database validate-markets
```

Checks for:
- Duplicate market IDs
- Invalid probabilities
- Missing required fields
- Expired but active markets

## Connection Pool Configuration

### 1. Database URL Format

```bash
# Standard format
postgresql://username:password@host:port/database

# With connection pool settings
postgresql://username:password@host:port/database?pool_size=20&max_overflow=40

# SSL enabled
postgresql://username:password@host:port/database?sslmode=require
```

### 2. Pool Settings

Configure in `.env`:

```bash
# Connection pool
DB_POOL_SIZE=20           # Number of persistent connections
DB_MAX_OVERFLOW=40        # Maximum overflow connections
DB_POOL_TIMEOUT=30        # Connection timeout in seconds
DB_POOL_RECYCLE=3600     # Recycle connections after 1 hour

# Query settings
DB_STATEMENT_TIMEOUT=30000  # 30 seconds
DB_LOCK_TIMEOUT=10000       # 10 seconds
```

### 3. Python Configuration

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True,  # Test connections
    echo_pool=True       # Log pool checkouts
)
```

## Performance Tuning

### 1. PostgreSQL Configuration

Edit `postgresql.conf`:

```ini
# Memory Configuration
shared_buffers = 25% of RAM       # e.g., 4GB for 16GB system
effective_cache_size = 75% of RAM # e.g., 12GB for 16GB system
work_mem = RAM / max_connections  # e.g., 50MB
maintenance_work_mem = RAM / 16   # e.g., 1GB

# Checkpoint Settings
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1  # For SSD

# Connection Settings
max_connections = 200
superuser_reserved_connections = 3

# Parallel Query
max_worker_processes = 8
max_parallel_workers = 8
max_parallel_workers_per_gather = 4
```

### 2. Index Optimization

Create optimized indexes:

```sql
-- Text search optimization
CREATE INDEX CONCURRENTLY idx_markets_text_search
ON polymarket_markets
USING gin(to_tsvector('english', question || ' ' || COALESCE(category, '')));

-- Category-based queries
CREATE INDEX CONCURRENTLY idx_markets_category_active_volume
ON polymarket_markets(category, active, volume_24h DESC)
WHERE active = true;

-- Time-based queries
CREATE INDEX CONCURRENTLY idx_analysis_created_date
ON analysis(date_trunc('day', created_at), created_at DESC);

-- User interaction queries
CREATE INDEX CONCURRENTLY idx_interactions_user_created
ON twitter_interactions(user_id, created_at DESC);
```

### 3. Query Optimization

Use EXPLAIN ANALYZE to optimize queries:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT m.*,
       ts_rank(to_tsvector('english', question), query) as relevance
FROM polymarket_markets m,
     plainto_tsquery('english', 'bitcoin 200k') query
WHERE to_tsvector('english', question) @@ query
  AND active = true
ORDER BY relevance DESC, volume_24h DESC
LIMIT 10;
```

## Backup Configuration

### 1. Automated Backups

Create backup script (`scripts/backup_database.sh`):

```bash
#!/bin/bash

BACKUP_DIR="/var/backups/aigg"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="aigg_insights"
DB_USER="aigg_user"

# Create backup directory
mkdir -p $BACKUP_DIR

# Full backup
pg_dump -U $DB_USER -d $DB_NAME -Fc > $BACKUP_DIR/aigg_$DATE.dump

# Keep only last 7 days
find $BACKUP_DIR -name "*.dump" -mtime +7 -delete

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/aigg_$DATE.dump s3://aigg-backups/
```

### 2. Schedule Backups

```bash
# Add to crontab
0 2 * * * /path/to/scripts/backup_database.sh
```

### 3. Restore from Backup

```bash
# Restore full database
pg_restore -U aigg_user -d aigg_insights -c /backups/aigg_20250127.dump

# Restore specific tables
pg_restore -U aigg_user -d aigg_insights -t polymarket_markets /backups/aigg_20250127.dump
```

## Monitoring Setup

### 1. Enable Statistics

```sql
-- Enable query statistics
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Configure in postgresql.conf
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.max = 10000
pg_stat_statements.track = all
```

### 2. Monitoring Queries

Create monitoring views:

```sql
-- Database size monitoring
CREATE VIEW v_database_sizes AS
SELECT
    datname as database,
    pg_size_pretty(pg_database_size(datname)) as size
FROM pg_database
ORDER BY pg_database_size(datname) DESC;

-- Table sizes
CREATE VIEW v_table_sizes AS
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) as indexes_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Slow queries
CREATE VIEW v_slow_queries AS
SELECT
    substring(query, 1, 100) as query_preview,
    calls,
    round(mean_exec_time::numeric, 2) as avg_ms,
    round(total_exec_time::numeric, 2) as total_ms
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;
```

### 3. Health Check Script

```python
# scripts/database_health.py
import psycopg2
import json
from datetime import datetime

def check_database_health():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    health = {
        "timestamp": datetime.now().isoformat(),
        "status": "healthy",
        "metrics": {}
    }

    # Check connection count
    cur.execute("""
        SELECT count(*) FROM pg_stat_activity
        WHERE datname = 'aigg_insights'
    """)
    health["metrics"]["connections"] = cur.fetchone()[0]

    # Check table counts
    cur.execute("SELECT count(*) FROM polymarket_markets WHERE active = true")
    health["metrics"]["active_markets"] = cur.fetchone()[0]

    # Check recent analyses
    cur.execute("""
        SELECT count(*) FROM analysis
        WHERE created_at > NOW() - INTERVAL '1 hour'
    """)
    health["metrics"]["recent_analyses"] = cur.fetchone()[0]

    # Check database size
    cur.execute("""
        SELECT pg_size_pretty(pg_database_size('aigg_insights'))
    """)
    health["metrics"]["database_size"] = cur.fetchone()[0]

    return health

if __name__ == "__main__":
    health = check_database_health()
    print(json.dumps(health, indent=2))
```

## Maintenance Tasks

### 1. Vacuum and Analyze

```bash
# Manual vacuum
psql -U aigg_user -d aigg_insights -c "VACUUM ANALYZE;"

# Automated vacuum script
#!/bin/bash
vacuumdb -U aigg_user -d aigg_insights -z -v
```

### 2. Reindex Tables

```sql
-- Reindex all tables (during maintenance window)
REINDEX DATABASE aigg_insights;

-- Reindex specific table concurrently
REINDEX TABLE CONCURRENTLY polymarket_markets;
```

### 3. Clean Old Data

```python
# scripts/cleanup_old_data.py
def cleanup_old_data():
    """Remove old data to maintain performance"""

    queries = [
        # Archive old analyses
        """
        DELETE FROM analysis
        WHERE created_at < NOW() - INTERVAL '30 days'
        """,

        # Remove expired research
        """
        DELETE FROM research
        WHERE expires_at < NOW()
        """,

        # Clean old interactions
        """
        DELETE FROM twitter_interactions
        WHERE created_at < NOW() - INTERVAL '90 days'
        """
    ]

    for query in queries:
        execute_query(query)
        print(f"Cleaned: {query[:50]}...")
```

## Troubleshooting

### Connection Issues

```bash
# Test connection
psql -U aigg_user -d aigg_insights -c "SELECT 1;"

# Check connection limits
psql -U postgres -c "SHOW max_connections;"
psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"
```

### Performance Issues

```sql
-- Find blocking queries
SELECT
    pid,
    usename,
    pg_blocking_pids(pid) as blocked_by,
    query as blocked_query
FROM pg_stat_activity
WHERE cardinality(pg_blocking_pids(pid)) > 0;

-- Kill blocking query
SELECT pg_terminate_backend(pid);
```

### Disk Space Issues

```bash
# Check disk usage
df -h

# Find large tables
psql -U aigg_user -d aigg_insights -c "
SELECT tablename,
       pg_size_pretty(pg_total_relation_size(tablename::regclass))
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(tablename::regclass) DESC;"
```

## Security Configuration

### 1. User Permissions

```sql
-- Create read-only user
CREATE USER aigg_readonly WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE aigg_insights TO aigg_readonly;
GRANT USAGE ON SCHEMA public TO aigg_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO aigg_readonly;

-- Create application user
CREATE USER aigg_app WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE aigg_insights TO aigg_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO aigg_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO aigg_app;
```

### 2. SSL Configuration

```bash
# In postgresql.conf
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'

# In pg_hba.conf
hostssl all all 0.0.0.0/0 md5
```

### 3. Connection Security

```python
# Use SSL in connection
DATABASE_URL = "postgresql://user:pass@host/db?sslmode=require"
```