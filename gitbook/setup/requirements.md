# System Requirements

## Minimum Requirements

### Hardware
- **CPU**: 4+ cores (Intel/AMD x64)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 20GB SSD space
- **Network**: Stable internet connection (100+ Mbps)

### Operating System
- **Ubuntu**: 20.04 LTS or newer
- **Debian**: 11 or newer
- **macOS**: 12.0+ (Monterey or newer)
- **WSL2**: Windows 10/11 with Ubuntu

### Software Dependencies

#### Python
```bash
# Python 3.11 or newer required
python3 --version
# Output: Python 3.11.x
```

#### PostgreSQL
```bash
# PostgreSQL 14+ required
psql --version
# Output: psql (PostgreSQL) 14.x
```

#### System Packages
```bash
# Required system packages
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-contrib \
    git \
    curl \
    build-essential \
    libpq-dev
```

## Python Dependencies

### Core Libraries
```txt
# Framework & API
fastapi==0.115.0
uvicorn==0.32.0
pydantic==2.10.0

# Database
psycopg2-binary==2.9.10
sqlalchemy==2.0.36
alembic==1.14.0

# AI/ML
dspy-ai==2.5.43
openai==1.57.0
anthropic==0.40.0
fireworks-ai==0.15.7

# Twitter Integration
tweepy==4.14.0
python-twitter==3.5

# Utilities
python-dotenv==1.0.1
requests==2.32.3
aiohttp==3.11.0
tenacity==9.0.0
```

### Development Dependencies
```txt
# Testing
pytest==8.3.4
pytest-asyncio==0.25.0
pytest-mock==3.14.0

# Linting & Formatting
black==24.10.0
flake8==7.1.1
mypy==1.13.0

# Documentation
mkdocs==1.6.1
mkdocs-material==9.5.0
```

## API Keys & Services

### Required API Access

#### Twitter/X API
- **Tier**: Basic or Pro ($100-$5000/month)
- **Endpoints**: Mentions timeline, Tweet creation
- **Rate Limits**:
  - Basic: 10 requests/min
  - Pro: 300 requests/min
- **Setup**: [developer.twitter.com](https://developer.twitter.com)

#### Fireworks AI
- **Model**: Qwen-3.5-72B
- **Pricing**: $0.004 per 1K tokens
- **Speed**: 300+ tokens/second
- **Setup**: [fireworks.ai](https://fireworks.ai)

#### Perplexity API
- **Model**: Sonar-small
- **Pricing**: $0.005 per request
- **Usage**: Real-time research
- **Setup**: [perplexity.ai/api](https://perplexity.ai/api)

#### OpenAI (Optional)
- **Models**: GPT-4o, GPT-4o-mini
- **Pricing**: $0.01-0.03 per 1K tokens
- **Fallback**: Secondary LLM provider
- **Setup**: [platform.openai.com](https://platform.openai.com)

### Optional Services

#### Redis (Caching)
```bash
# For production scaling
sudo apt-get install redis-server
redis-cli --version
```

#### Docker (Containerization)
```bash
# For deployment
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
docker --version
```

## Network Requirements

### Ports
| Port | Service | Required |
|------|---------|----------|
| 8001 | Market API | Yes |
| 8003 | Twitter Wrapper | Yes |
| 5432 | PostgreSQL | Yes |
| 6379 | Redis | Optional |

### Firewall Configuration
```bash
# Open required ports
sudo ufw allow 8001/tcp
sudo ufw allow 8003/tcp
sudo ufw allow 5432/tcp
```

### Domain & SSL (Production)
- Domain name for API access
- SSL certificate (Let's Encrypt)
- Reverse proxy (Nginx/Caddy)

## Performance Recommendations

### Database Optimization
```sql
-- Recommended PostgreSQL settings
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '6GB';
ALTER SYSTEM SET maintenance_work_mem = '512MB';
ALTER SYSTEM SET random_page_cost = 1.1;
```

### Python Environment
```bash
# Use virtual environment
python3 -m venv venv
source venv/bin/activate

# Install with optimizations
pip install --upgrade pip
pip install -r requirements.txt --use-pep517
```

### System Limits
```bash
# Increase file descriptors
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# Increase system memory limits
echo "vm.max_map_count=262144" >> /etc/sysctl.conf
sysctl -p
```

## Scaling Considerations

### Small Scale (< 100 requests/day)
- Single server deployment
- SQLite or PostgreSQL
- Basic Twitter API tier

### Medium Scale (100-1000 requests/day)
- Dedicated database server
- Redis caching layer
- Pro Twitter API tier

### Large Scale (1000+ requests/day)
- Load balanced API servers
- PostgreSQL replication
- Queue system (RabbitMQ/Kafka)
- Enterprise Twitter API

## Development Environment

### VS Code Extensions
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-azuretools.vscode-docker",
    "mtxr.sqltools",
    "redhat.vscode-yaml"
  ]
}
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.10.0
    hooks:
      - id: black
  - repo: https://github.com/PyCQA/flake8
    rev: 7.1.1
    hooks:
      - id: flake8
```

## Verification Checklist

### System Check Script
```bash
#!/bin/bash
# save as check_requirements.sh

echo "Checking AIGG Requirements..."

# Python version
python3 -c "import sys; assert sys.version_info >= (3,11)" \
  && echo "✓ Python 3.11+" \
  || echo "✗ Python 3.11+ required"

# PostgreSQL
pg_config --version &>/dev/null \
  && echo "✓ PostgreSQL installed" \
  || echo "✗ PostgreSQL missing"

# Required Python packages
python3 -c "import fastapi, dspy, tweepy" 2>/dev/null \
  && echo "✓ Core packages installed" \
  || echo "✗ Core packages missing"

# Port availability
netstat -tuln | grep -q ":8001 " \
  && echo "⚠ Port 8001 in use" \
  || echo "✓ Port 8001 available"

netstat -tuln | grep -q ":8003 " \
  && echo "⚠ Port 8003 in use" \
  || echo "✓ Port 8003 available"

echo "Check complete!"
```

## Next Steps

Once requirements are met:
1. [Environment Setup](environment-setup.md)
2. [Database Configuration](database-configuration.md)
3. [API Keys Setup](api-keys.md)