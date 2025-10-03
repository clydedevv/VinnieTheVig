# API Keys & Credentials

Complete guide for obtaining and configuring all required API keys for AIGG Insights.

## Required API Keys

### Priority Levels
- **Essential**: System won't function without these
- **Recommended**: Core functionality requires these
- **Optional**: Enhanced features

## 1. Fireworks AI (Essential)

Primary LLM provider for market matching and analysis.

### Getting Your API Key

1. Visit [Fireworks AI](https://fireworks.ai/)
2. Sign up for an account
3. Navigate to [API Keys](https://fireworks.ai/account/api-keys)
4. Click "Create API Key"
5. Copy the key (starts with `fw_`)

### Configuration

```bash
# .env file
FIREWORKS_API_KEY=fw_your_key_here
FIREWORKS_MODEL=fireworks/qwen3-235b-a22b
FIREWORKS_MAX_TOKENS=4096
FIREWORKS_TEMPERATURE=0.7
```

### Pricing
- See [Fireworks AI pricing](https://fireworks.ai/pricing) for current rates
- **Free tier**: $1 credit on signup

## 2. Perplexity AI (Essential)

Used for real-time web research and current information.

### Getting Your API Key

1. Visit [Perplexity AI](https://www.perplexity.ai/)
2. Go to [API Settings](https://www.perplexity.ai/settings/api)
3. Click "Generate API Key"
4. Copy the key (starts with `pplx-`)

### Configuration

```bash
# .env file
PERPLEXITY_API_KEY=pplx_your_key_here
PERPLEXITY_MODEL=sonar
PERPLEXITY_MAX_TOKENS=2048
```

### Pricing
- See [Perplexity pricing](https://docs.perplexity.ai/getting-started/pricing) for current rates
- **Free tier**: $5 credit monthly

## 3. OpenAI (Recommended)

Fallback LLM provider and enhanced reasoning.

### Getting Your API Key

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Go to [API Keys](https://platform.openai.com/api-keys)
4. Click "Create new secret key"
5. Copy the key (starts with `sk-`)

### Configuration

```bash
# .env file
OPENAI_API_KEY=sk-your_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=4096
OPENAI_TEMPERATURE=0.7

# Optional: Organization ID
OPENAI_ORG_ID=org-your_org_id
```

### Pricing
- **GPT-4o-mini**: $0.15/$0.60 per million tokens (input/output)
- **GPT-4o**: $2.50/$10.00 per million tokens
- **Free tier**: $5 credit on signup

## 4. Twitter API (Optional)

Required only for Twitter bot functionality.

### Getting Your API Keys

1. Visit [Twitter Developer Portal](https://developer.twitter.com/)
2. Apply for developer account
3. Create a new app
4. Generate keys and tokens

### Access Levels
- See [X's developer docs](https://developer.twitter.com/en/products/twitter-api) for current tiers and pricing

### Configuration

```bash
# .env file
# App credentials
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_BEARER_TOKEN=your_bearer_token

# User credentials (for posting)
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret

# Optional settings
TWITTER_USERNAME=VigVinnie
TWITTER_CHECK_INTERVAL=30  # seconds
```

### Required Permissions
- Read tweets
- Write tweets
- Access direct messages (optional)

## 5. Database Credentials

PostgreSQL database connection.

### Local Development

```bash
# .env file
DATABASE_URL=postgresql://aigg_user:password@localhost:5432/aigg_insights
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
```

### Production Database

```bash
# Use environment-specific credentials
DATABASE_URL=postgresql://user:pass@prod-host:5432/aigg_prod
DB_SSL_MODE=require
DB_SSL_CERT=/path/to/cert.pem
```

## 6. Optional Services

### Redis (Caching)

```bash
# .env file
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=your_redis_password  # if required
REDIS_SSL=false
REDIS_CACHE_TTL=3600  # seconds
```

### Sentry (Error Tracking)

```bash
# .env file
SENTRY_DSN=https://your_key@sentry.io/project_id
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
```

### DataDog (Monitoring)

```bash
# .env file
DATADOG_API_KEY=your_dd_api_key
DATADOG_APP_KEY=your_dd_app_key
DATADOG_SITE=datadoghq.com
```

## Environment File Template

Complete `.env.example`:

```bash
# ============================================
# CORE CONFIGURATION
# ============================================
ENV=development
DEBUG=true
LOG_LEVEL=INFO

# ============================================
# DATABASE
# ============================================
DATABASE_URL=postgresql://user:pass@localhost:5432/aigg_insights
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# ============================================
# LLM PROVIDERS
# ============================================

# Fireworks AI (Primary)
FIREWORKS_API_KEY=fw_...
FIREWORKS_MODEL=fireworks/qwen3-235b-a22b
FIREWORKS_MAX_TOKENS=4096
FIREWORKS_TEMPERATURE=0.7
FIREWORKS_TIMEOUT=30

# Perplexity (Research)
PERPLEXITY_API_KEY=pplx_...
PERPLEXITY_MODEL=sonar
PERPLEXITY_MAX_TOKENS=2048
PERPLEXITY_TIMEOUT=30

# OpenAI (Fallback)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=4096
OPENAI_TEMPERATURE=0.7
OPENAI_TIMEOUT=30

# ============================================
# TWITTER API (Optional)
# ============================================
TWITTER_API_KEY=...
TWITTER_API_SECRET=...
TWITTER_BEARER_TOKEN=...
TWITTER_ACCESS_TOKEN=...
TWITTER_ACCESS_TOKEN_SECRET=...
TWITTER_USERNAME=VigVinnie
TWITTER_CHECK_INTERVAL=30

# ============================================
# CACHING (Optional)
# ============================================
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600

# ============================================
# MONITORING (Optional)
# ============================================
SENTRY_DSN=https://...@sentry.io/...
DATADOG_API_KEY=...
```

## Security Best Practices

### 1. Never Commit Keys

Add to `.gitignore`:

```gitignore
.env
.env.*
!.env.example
*.key
*.pem
credentials.json
```

### 2. Use Environment Variables

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Access keys securely
FIREWORKS_KEY = os.getenv("FIREWORKS_API_KEY")
if not FIREWORKS_KEY:
    raise ValueError("FIREWORKS_API_KEY not set")
```

### 3. Rotate Keys Regularly

```bash
# Script to rotate keys
#!/bin/bash

# Backup old keys
cp .env .env.backup.$(date +%Y%m%d)

# Update keys
echo "Update API keys in .env file"
nano .env

# Restart services
systemctl restart aigg-api
systemctl restart aigg-bot
```

### 4. Use Secrets Management

For production, consider:
- **AWS Secrets Manager**
- **HashiCorp Vault**
- **Azure Key Vault**
- **Google Secret Manager**

Example with AWS:

```python
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Usage
secrets = get_secret("aigg/api-keys")
FIREWORKS_KEY = secrets['FIREWORKS_API_KEY']
```

## Testing API Keys

### Validation Script

```python
# scripts/validate_api_keys.py
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_fireworks():
    """Test Fireworks AI API"""
    import requests

    key = os.getenv("FIREWORKS_API_KEY")
    if not key:
        return False, "Key not found"

    response = requests.get(
        "https://api.fireworks.ai/inference/v1/models",
        headers={"Authorization": f"Bearer {key}"}
    )
    return response.status_code == 200, response.text

def test_perplexity():
    """Test Perplexity API"""
    import requests

    key = os.getenv("PERPLEXITY_API_KEY")
    if not key:
        return False, "Key not found"

    response = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={"Authorization": f"Bearer {key}"},
        json={
            "model": "sonar",
            "messages": [{"role": "user", "content": "test"}],
            "max_tokens": 1
        }
    )
    return response.status_code == 200, response.text

def test_openai():
    """Test OpenAI API"""
    import openai

    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        return False, "Key not found"

    try:
        response = openai.models.list()
        return True, "OK"
    except Exception as e:
        return False, str(e)

def main():
    print("Testing API Keys...")

    tests = [
        ("Fireworks AI", test_fireworks),
        ("Perplexity", test_perplexity),
        ("OpenAI", test_openai)
    ]

    for name, test_func in tests:
        success, message = test_func()
        status = "OK" if success else "FAIL"
        print(f"{status} {name}: {message[:100] if not success else 'OK'}")

if __name__ == "__main__":
    main()
```

## Rate Limits & Quotas

### Fireworks AI
- **Rate Limit**: 600 requests/minute
- **Concurrent**: 50 requests
- **Daily Quota**: Based on plan

### Perplexity
- **Rate Limit**: 20 requests/minute
- **Concurrent**: 10 requests
- **Monthly Quota**: Based on plan

### OpenAI
- **Rate Limit**: 500 requests/minute
- **Token Limit**: 150K tokens/minute
- **Daily Quota**: Based on tier

### Twitter
- **Read**: 300 requests/15min
- **Write**: 300 requests/3hours
- **Search**: 180 requests/15min

## Troubleshooting

### Invalid API Key

```python
# Check key format
if not key.startswith(expected_prefix):
    print(f"Invalid key format. Should start with {expected_prefix}")
```

### Rate Limit Exceeded

```python
# Implement exponential backoff
import time

def retry_with_backoff(func, max_retries=5):
    for i in range(max_retries):
        try:
            return func()
        except RateLimitError:
            wait_time = 2 ** i
            time.sleep(wait_time)
    raise Exception("Max retries exceeded")
```

### Connection Errors

```python
# Add timeout and retry
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(total=3, backoff_factor=0.3)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)
```