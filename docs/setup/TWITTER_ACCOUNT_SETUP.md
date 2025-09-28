# Twitter Account Setup for AIGG Bot

## Create Dedicated Bot Account

### Step 1: Create New Twitter Account
1. Go to [twitter.com](https://twitter.com) 
2. Sign up with a new email (e.g., `aigg.insights.bot@gmail.com`)
3. Choose username like `@aigg_insights` or `@aigg_bot`
4. Set profile:
   - **Name**: "AIGG Insights"
   - **Bio**: "🤖 AI-powered prediction market analysis | Ask me about crypto, politics, sports betting | Powered by @polymarket"
   - **Website**: Link to your main site/github
   - **Profile pic**: AI/bot themed image

### Step 2: Apply for Twitter Developer Account
1. Go to [developer.twitter.com](https://developer.twitter.com)
2. Apply for developer access using the bot account
3. **Use case**: "Building a bot for prediction market analysis"
4. **Description**: 
   ```
   I'm building an educational bot that provides AI-powered analysis 
   of prediction markets. Users can ask questions about market events 
   (elections, crypto prices, sports) and receive research-backed 
   predictions with links to Polymarket for further exploration.
   ```

### Step 3: Create Twitter App
1. Create new app in developer portal
2. **App name**: "AIGG Insights Bot"
3. **Description**: Same as above
4. **Website**: Your project URL
5. **Callback URL**: Not needed for bot
6. **Permissions**: "Read and Write" (to post replies)

### Step 4: Generate API Keys
Generate and save these in your `.env`:
- **API Key** → `TWITTER_API_KEY`
- **API Secret** → `TWITTER_API_SECRET`  
- **Bearer Token** → `TWITTER_BEARER_TOKEN`
- **Access Token** → `TWITTER_ACCESS_TOKEN`
- **Access Token Secret** → `TWITTER_ACCESS_TOKEN_SECRET`

### Step 5: Update Bot Configuration
Update the bot handle in the code:

```python
# In src/twitter/client.py
self.bot_handle = "@aigg_insights"  # Your actual bot username
```

## Testing the Bot

### Phase 1: Private Testing
- Set bot to private/protected initially
- Test with your personal account
- Verify all functionality works

### Phase 2: Limited Beta
- Make bot public
- Add whitelisting (see next section)
- Invite select users for testing

### Phase 3: Public Launch
- Remove whitelist or expand it
- Announce on social media
- Monitor for issues

## Important Notes

⚠️ **Twitter Terms of Service**
- Don't spam or auto-follow
- Respect rate limits
- Provide value to users
- Be transparent about being a bot

⚠️ **Polymarket Compliance**
- Ensure you're compliant with affiliate/referral terms
- Don't provide financial advice (use disclaimers)
- Educational use only

⚠️ **API Limits**
- Twitter API v2 has rate limits
- Start with conservative settings
- Monitor usage carefully 