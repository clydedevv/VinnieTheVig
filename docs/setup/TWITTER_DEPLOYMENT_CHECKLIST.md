# AIGG Twitter Bot Deployment Checklist

## 🎯 Pre-Deployment Setup

### 1. Twitter Account & API Setup
- [ ] Create dedicated bot account (e.g., `@aigg_insights`)
- [ ] Apply for Twitter Developer account with bot account
- [ ] Create Twitter app with Read/Write permissions
- [ ] Generate all API credentials
- [ ] Test API access with credentials

### 2. Environment Configuration
- [ ] Copy `.env.sample` to `.env`
- [ ] Add Twitter API credentials to `.env`
- [ ] Set `BOT_HANDLE` to your bot's Twitter username
- [ ] Configure `WHITELIST_ENABLED=true` for beta
- [ ] Set `MAX_REQUESTS_PER_DAY=10` (or desired limit)

### 3. Whitelist Setup
- [ ] Get your personal Twitter user ID from [tweeterid.com](https://tweeterid.com)
- [ ] Add yourself as admin: `python scripts/manage_whitelist.py add YOUR_ID YOUR_USERNAME --level admin`
- [ ] Add initial beta testers
- [ ] Test whitelist with: `python scripts/manage_whitelist.py stats`

### 4. System Testing
- [ ] Run: `python src/tests/test_twitter_system.py` (should pass all tests)
- [ ] Run: `python src/twitter/bot.py --test-only` (test setup)
- [ ] Test wrapper API: `curl http://localhost:8003/health`
- [ ] Verify database has active markets: `curl http://localhost:8001/health`

## 🚀 Deployment Process

### Phase 1: Private Testing (1-2 days)
- [ ] Set bot account to **private/protected** initially
- [ ] Start services: wrapper API (port 8003) + Twitter bot
- [ ] Test with your personal account mentioning the bot
- [ ] Verify AI analysis responses work correctly
- [ ] Check logs for any errors

**Test Commands:**
```bash
# Start wrapper API
python src/api_wrapper/twitter_wrapper.py &

# Start bot in one terminal
python src/twitter/bot.py

# In another terminal, monitor logs
tail -f logs/twitter_bot.log logs/twitter_wrapper.log
```

### Phase 2: Beta Testing (1 week)
- [ ] Make bot account **public**
- [ ] Add 5-10 beta testers to whitelist
- [ ] Monitor performance and fix issues
- [ ] Collect feedback and iterate

**Beta Tester Management:**
```bash
# Add beta testers
python scripts/manage_whitelist.py add USER_ID USERNAME --level whitelist --notes "Beta tester from [source]"

# Monitor activity
python scripts/manage_whitelist.py stats
```

### Phase 3: VIP Launch (2 weeks)
- [ ] Add crypto/prediction market influencers as VIP
- [ ] Increase rate limits for VIP users
- [ ] Create announcement content
- [ ] Monitor for viral growth

### Phase 4: Public Launch
- [ ] Set `WHITELIST_ENABLED=false` for public access
- [ ] Announce on Twitter, Reddit, Discord
- [ ] Monitor performance under load
- [ ] Have scaling plan ready

## 📋 Production Configuration

### Required Services
- [ ] Main AIGG API (port 8001) - Market data and analysis
- [ ] Twitter Wrapper API (port 8003) - Twitter-optimized responses  
- [ ] Twitter Bot - Monitoring and response service
- [ ] PostgreSQL Database - Market data (55k+ markets)

### Monitoring Setup
- [ ] Log rotation configured
- [ ] Disk space monitoring (logs can grow large)
- [ ] API response time monitoring
- [ ] Error rate alerting
- [ ] Daily whitelist stats review

### Security Checklist
- [ ] API keys in environment variables (never committed)
- [ ] Rate limiting enabled and tested
- [ ] Input validation for all user queries
- [ ] Error messages don't expose internal details
- [ ] Database access properly secured

## 🛠️ Operational Commands

### Daily Operations
```bash
# Check bot status
python src/twitter/bot.py --whitelist-stats

# View recent activity
tail -100 logs/twitter_bot.log

# Add new users
python scripts/manage_whitelist.py add USER_ID USERNAME --level whitelist

# Monitor API health
curl http://localhost:8003/health
curl http://localhost:8001/health
```

### Weekly Maintenance
```bash
# Review user statistics
python scripts/manage_whitelist.py stats

# Check database sync
python scripts/populate_polymarket_data_clob.py --dry-run

# Review error logs
grep ERROR logs/*.log | tail -50
```

## 🚨 Troubleshooting

### Common Issues & Solutions

**"Twitter API authentication failed"**
- Verify credentials in `.env`
- Check API permissions (Read/Write)
- Ensure bearer token is valid

**"User not in whitelist"**
- Add user: `python scripts/manage_whitelist.py add USER_ID USERNAME --level whitelist`
- Or disable whitelist: Set `WHITELIST_ENABLED=false`

**"Wrapper API not available"**
- Check if running: `ps aux | grep twitter_wrapper`
- Restart: `python src/api_wrapper/twitter_wrapper.py &`
- Check port conflicts: `netstat -tlnp | grep 8003`

**"No response generated"**
- Check main API: `curl http://localhost:8001/health`
- Verify database has markets: Check `/search` endpoint
- Review AIGG flow logs

### Emergency Procedures

**Stop Bot Immediately:**
```bash
pkill -f "python src/twitter/bot.py"
pkill -f "python src/api_wrapper/twitter_wrapper.py"
```

**Temporary User Block:**
```bash
python scripts/manage_whitelist.py add PROBLEMATIC_USER_ID username --level blocked --notes "Emergency block"
```

**Disable Public Access:**
```bash
# Set in .env file
WHITELIST_ENABLED=true
# Restart services
```

## 📈 Success Metrics

### Week 1 Targets
- [ ] 10+ successful bot interactions
- [ ] Zero critical errors
- [ ] <30 second average response time
- [ ] 5+ beta testers engaged

### Month 1 Targets  
- [ ] 100+ successful interactions
- [ ] 50+ unique users
- [ ] 95%+ uptime
- [ ] Positive user feedback

### Growth Metrics
- [ ] Daily active mentions
- [ ] Click-through rate to Polymarket
- [ ] User retention (return users)
- [ ] Query accuracy (prediction relevance)

## 🔄 Rollback Plan

If major issues occur:

1. **Stop Services:** Kill bot and wrapper API
2. **Revert Code:** `git checkout` to last working commit
3. **Restart Services:** Use previous stable configuration
4. **Notify Users:** Tweet about temporary maintenance
5. **Debug Offline:** Fix issues in development environment

## 📞 Support Contacts

- **Technical Issues:** Check GitHub issues
- **Twitter API Problems:** Twitter Developer Support
- **Database Issues:** Check PostgreSQL logs
- **Monitoring:** Review all log files in `logs/` directory

---

**Ready for Launch? ✅**

When all checkboxes are completed, your AIGG Twitter Bot is ready for production deployment! 🚀 