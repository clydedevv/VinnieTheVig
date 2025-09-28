# Environment Setup

Complete guide to setting up your development environment for AIGG Insights.

## System Requirements

### Minimum Requirements
- **OS**: Ubuntu 20.04+, macOS 12+, or Windows 10+ (WSL2)
- **Python**: 3.11 or higher
- **PostgreSQL**: 14.0 or higher
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space
- **CPU**: 4 cores recommended

### Network Requirements
- Stable internet connection for API calls
- Ports 8001, 8003 available for local services
- PostgreSQL default port 5432

## Python Environment Setup

### 1. Install Python 3.11+

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev
```

**macOS (using Homebrew):**
```bash
brew install python@3.11
```

**Windows:**
Download from [python.org](https://www.python.org/downloads/) or use:
```powershell
winget install Python.Python.3.11
```

### 2. Create Virtual Environment

```bash
# Navigate to project directory
cd aigg-insights

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3. Upgrade pip and Install Tools

```bash
python -m pip install --upgrade pip
pip install wheel setuptools
```

## PostgreSQL Setup

### 1. Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt install postgresql-14 postgresql-client-14
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS:**
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Windows:**
Download installer from [postgresql.org](https://www.postgresql.org/download/windows/)

### 2. Create Database and User

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL shell:
CREATE USER aigg_user WITH PASSWORD 'your_secure_password';
CREATE DATABASE aigg_insights OWNER aigg_user;
GRANT ALL PRIVILEGES ON DATABASE aigg_insights TO aigg_user;
\q
```

### 3. Configure PostgreSQL

Edit PostgreSQL configuration for optimal performance:

```bash
# Find config location
sudo -u postgres psql -c "SHOW config_file;"

# Edit postgresql.conf
sudo nano /etc/postgresql/14/main/postgresql.conf
```

Recommended settings:
```ini
# Memory settings
shared_buffers = 256MB
work_mem = 4MB
maintenance_work_mem = 64MB

# Connection settings
max_connections = 100

# Performance
effective_cache_size = 1GB
random_page_cost = 1.1
```

## Environment Variables

### 1. Create .env File

```bash
cp .env.example .env
nano .env
```

### 2. Configure Environment Variables

```bash
# Database
DATABASE_URL=postgresql://aigg_user:your_secure_password@localhost:5432/aigg_insights
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40

# OpenAI (for fallback)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Fireworks AI (primary LLM)
FIREWORKS_API_KEY=fw_...
FIREWORKS_MODEL=accounts/fireworks/models/qwen2p5-72b-instruct

# Perplexity (for research)
PERPLEXITY_API_KEY=pplx-...
PERPLEXITY_MODEL=llama-3.1-sonar-large-128k-online

# Twitter API (optional)
TWITTER_API_KEY=...
TWITTER_API_SECRET=...
TWITTER_ACCESS_TOKEN=...
TWITTER_ACCESS_TOKEN_SECRET=...
TWITTER_BEARER_TOKEN=...

# Redis (optional, for caching)
REDIS_URL=redis://localhost:6379/0

# Application settings
ENV=development
DEBUG=true
LOG_LEVEL=INFO
```

## Install Dependencies

### 1. Core Dependencies

```bash
pip install -r requirements.txt
```

### 2. Development Dependencies

```bash
pip install -r requirements-dev.txt
```

### 3. Verify Installation

```bash
# Check Python packages
pip list

# Test database connection
python -c "import psycopg2; print('PostgreSQL OK')"

# Test API imports
python -c "import fastapi; import dspy; print('APIs OK')"
```

## IDE Configuration

### VS Code

1. Install Python extension
2. Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

### PyCharm

1. Set Project Interpreter: `File → Settings → Project → Python Interpreter`
2. Select virtual environment: `venv/bin/python`
3. Mark directories:
   - `src` as Sources Root
   - `tests` as Test Sources Root

## Docker Setup (Optional)

### 1. Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run application
CMD ["python", "main.py", "api-server", "--port", "8001"]
```

### 2. Docker Compose

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_USER: aigg_user
      POSTGRES_PASSWORD: your_secure_password
      POSTGRES_DB: aigg_insights
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  api:
    build: .
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql://aigg_user:your_secure_password@postgres:5432/aigg_insights
    ports:
      - "8001:8001"
    volumes:
      - .:/app

volumes:
  postgres_data:
```

## System Services Setup

### 1. Create systemd Service (Linux)

```ini
# /etc/systemd/system/aigg-api.service
[Unit]
Description=AIGG Insights API Server
After=network.target postgresql.service

[Service]
Type=simple
User=aigg
WorkingDirectory=/home/aigg/aigg-insights
Environment="PATH=/home/aigg/aigg-insights/venv/bin"
ExecStart=/home/aigg/aigg-insights/venv/bin/python main.py api-server --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
```

### 2. Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable aigg-api
sudo systemctl start aigg-api
sudo systemctl status aigg-api
```

## Verify Environment

### Run Environment Check Script

```bash
python scripts/check_environment.py
```

Expected output:
```
Python version: 3.11.7
PostgreSQL connection: OK
OpenAI API: OK
Fireworks API: OK
Perplexity API: OK
Twitter API: OK
All dependencies installed
Database tables created
Environment ready!
```

## Common Issues

### Python Version Mismatch
```bash
# Check Python version
python --version

# Use specific version
python3.11 -m venv venv
```

### PostgreSQL Connection Refused
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -U aigg_user -d aigg_insights -h localhost
```

### Module Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Clear pip cache
pip cache purge
```

### Permission Errors
```bash
# Fix ownership
sudo chown -R $USER:$USER .

# Fix permissions
chmod -R 755 .
```

## Next Steps

1. [Configure Database](database-configuration.md)
2. [Set Up API Keys](api-keys.md)
3. [Run the System](running-the-system.md)