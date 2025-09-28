# AIGG Twitter Bot Setup Guide

## Overview

The AIGG Twitter Bot provides DSPy-enhanced AI-powered prediction market analysis directly on Twitter. Users can mention the bot with prediction market questions and receive instant analysis with Polymarket links.

## Architecture

```
Twitter API → Bot Client → Wrapper API → DSPy Enhanced AIGG Flow → Response
                ↓                              ↓
         Query Extraction              LLM Market Matching + Analysis
```

## Components

### 1. Twitter Client (`src/twitter/client.py`)
- Monitors mentions using Twitter API v2
- Extracts prediction market queries from tweets
- Handles rate limiting (5 minutes between responses per user)
- Posts formatted responses

### 2. Wrapper API (`src/api_wrapper/twitter_wrapper.py`)
- FastAPI service optimized for Twitter integration
- Formats responses to fit 280-character limit
- Provides caching and additional rate limiting
- Runs on port 8003

### 3. Main Bot (`src/twitter/bot.py`)
- Orchestrates the entire flow
- Monitors mentions every 30 seconds (X Premium)
- Integrates client with wrapper API
- Handles errors gracefully

## Setup Instructions

### Step 1: Twitter API Credentials

Create a `.env` file in the project root with your Twitter API credentials:

```bash
# Twitter API v2 Credentials
TWITTER_BEARER_TOKEN=your_bearer_token_here
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
```

**How to get credentials:**
1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create a new app or use existing one
3. Generate API keys and access tokens
4. Ensure you have "Read and Write" permissions

### Step 2: Install Dependencies

```bash
pip install tweepy fastapi uvicorn
```

### Step 3: Test the System

```bash
# Test all components
python src/tests/test_twitter_system.py

# Test without Twitter credentials (should show graceful failure)
python src/twitter/bot.py --test-only
```

### Step 4: Setup Whitelist System

**Configure Whitelist Settings:**

Add to your `.env` file:
```bash
# Whitelist Configuration
WHITELIST_ENABLED=true
MAX_REQUESTS_PER_DAY=10

# Your personal Twitter account (admin)
ADMIN_USER_ID=your_personal_user_id
ADMIN_USERNAME=your_personal_username
```

**Get Your Twitter User ID:**
1. Go to [tweeterid.com](https://tweeterid.com)
2. Enter your Twitter username
3. Copy the numeric user ID
4. Add it to your `.env` file as `ADMIN_USER_ID`

**Add Yourself as Admin:**
```bash
# Replace with your actual ID and username
python scripts/manage_whitelist.py add 1234567890 your_username --level admin --notes "Bot administrator"
```

**Whitelist Management Commands:**

```bash
# Add beta testers
python scripts/manage_whitelist.py add USER_ID USERNAME --level whitelist --notes "Beta tester"

# Add VIP users (no rate limits)
python scripts/manage_whitelist.py add USER_ID USERNAME --level vip --notes "VIP access"

# List all users
python scripts/manage_whitelist.py list

# Show statistics
python scripts/manage_whitelist.py stats

# Remove user
python scripts/manage_whitelist.py remove USER_ID
```

**Access Levels:**
- **admin**: Full access, no rate limits, can manage bot
- **vip**: Full access, no rate limits
- **whitelist**: Normal access with daily rate limits (10/day)
- **blocked**: No access

### Step 5: Start the Services

**Terminal 1 - Start Wrapper API:**
```bash
python src/api_wrapper/twitter_wrapper.py
```

**Terminal 2 - Start Twitter Bot:**
```bash
python src/twitter/bot.py
```

## Usage Examples

### User Experience

**User tweets:**
```
@aigg_bot Will Bitcoin reach $150k this year?
```

**Bot responds:**
```
🔍 Will Bitcoin reach $150k this year?
📊 Bitcoin shows strong institutional adoption with ETF inflows...
📈 BUY (75% confidence)
🔗 https://polymarket.com/event/will-bitcoin-reach-150k-in-june
```

### Supported Query Types

The bot recognizes these types of prediction market queries:

✅ **Price Predictions**
- "Will Bitcoin reach $150k?"
- "What's the price target for Tesla?"

✅ **Election Questions**
- "Who will win the election?"
- "What are Trump's odds?"

✅ **Sports Betting**
- "Will the Lakers win the championship?"
- "NBA Finals predictions?"

✅ **Economic Events**
- "When will the Fed raise rates?"
- "Will there be a recession?"

❌ **Not Recognized**
- "Hello world"
- "Just had lunch"
- Generic conversations

## Technical Details

### Query Extraction Algorithm

The bot uses a sophisticated pattern matching system:

1. **Pattern Recognition** - Detects question structures like "Will X happen?"
2. **Keyword Matching** - Identifies market-relevant terms (crypto, election, sports)
3. **Confidence Scoring** - Assigns confidence score (0.5+ threshold)

### Response Formatting

Responses are carefully formatted for Twitter:

```
🔍 [Query - max 50 chars]
📊 [Analysis - max 80 chars]  
📈 [Recommendation + confidence]
🔗 [Polymarket URL]
```

Total length is always ≤ 280 characters.

### Rate Limiting

**Per User:**
- 5 minutes between responses
- Prevents spam and API overuse

**Global:**
- 10 mentions processed per check
- 60-second check intervals

## Monitoring & Logs

### Log Files

- `logs/twitter_bot.log` - Main bot operations
- `logs/twitter_wrapper.log` - API wrapper requests
- `logs/aigg_flow.log` - Analysis pipeline

### Key Metrics

- Mentions processed
- Queries detected vs. total mentions
- Response success rate
- API response times

## Troubleshooting

### Common Issues

**1. "Twitter API authentication failed"**
- Check credentials in `.env` file
- Verify API key permissions
- Ensure bearer token is valid

**2. "Wrapper API not available"**
- Check if wrapper API is running on port 8002
- Verify no port conflicts
- Check API health endpoint: `curl http://localhost:8002/health`

**3. "No prediction query detected"**
- Review query extraction patterns
- Check confidence threshold (0.5)
- Add new patterns if needed

**4. "Tweet too long"**
- Wrapper API automatically truncates
- Check formatting logic
- Verify character counting

### Debug Mode

Run with verbose logging:

```bash
python src/twitter/bot.py --check-interval 30
```

### Test Mode

Test without posting to Twitter:

```bash
python src/twitter/bot.py --test-only
```

## Production Deployment

### Systemd Service

Create `/etc/systemd/system/aigg-twitter-bot.service`:

```ini
[Unit]
Description=AIGG Twitter Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/aigg-insights
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/python src/twitter/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable aigg-twitter-bot
sudo systemctl start aigg-twitter-bot
```

### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "src/twitter/bot.py"]
```

### Monitoring

Use tools like:
- **Prometheus** - Metrics collection
- **Grafana** - Dashboards
- **Sentry** - Error tracking

## Security Considerations

1. **API Keys** - Store in environment variables, never commit
2. **Rate Limiting** - Prevent abuse and API quota exhaustion
3. **Input Validation** - Sanitize user queries
4. **Error Handling** - Don't expose internal errors to users

## Performance Optimization

1. **Caching** - Cache market searches for common queries
2. **Async Processing** - Process multiple mentions concurrently
3. **Database Indexing** - Optimize market search queries
4. **Response Time** - Target <30s total response time

## Next Steps

1. **Enhanced NLP** - Improve query extraction with ML models
2. **Multi-language** - Support non-English queries  
3. **User Profiles** - Track user preferences and history
4. **Advanced Analytics** - Market sentiment analysis
5. **DM Support** - Handle direct messages
6. **Thread Support** - Multi-tweet responses for complex analysis

## Support

For issues and questions:
- Check logs first
- Review this guide
- Test individual components
- Check GitHub issues

The bot is designed to be robust and handle various edge cases gracefully. Most issues can be resolved by checking logs and ensuring all services are running correctly. 