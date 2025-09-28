# Frequently Asked Questions

## Using VigVinnie

### How do I use VigVinnie?
Simply mention [@VigVinnie](https://x.com/VigVinnie) on Twitter with any market question. For example:
- "@VigVinnie Will Bitcoin hit 200k?"
- "@VigVinnie Trump 2028 election odds?"
- "@VigVinnie Fed cutting rates soon?"

### How long does VigVinnie take to respond?
VigVinnie typically responds within 30-90 seconds, depending on:
- Market research complexity
- Current Twitter API load
- Whether real-time context is needed

### What makes VigVinnie different from other bots?
VigVinnie has a unique Brooklyn bookmaker personality and provides:
- Authentic gambling terminology and insights
- Direct Polymarket links with clean previews
- Two-tweet threads (analysis + link)
- Real-time market research when needed

## Technical Questions

### What is AIGG?
AIGG is the AI technology that powers VigVinnie. It handles market matching, research, and analysis while VigVinnie provides the personality and voice.

### How accurate are the market matches?
AIGG achieves 98%+ relevance in market matching by combining:
- Semantic search across 114K+ markets
- Fuzzy matching for typos and variations
- Real-time validation of Polymarket URLs

### Can I deploy my own VigVinnie instance?
Yes! The code is open source at [clydedevv/VinnieTheVig](https://github.com/clydedevv/VinnieTheVig). Check the [Quick Start Guide](../getting-started/quick-start.md) for setup instructions.

## Troubleshooting

### VigVinnie didn't respond to my tweet
Possible reasons:
- Your account may be rate-limited (10 requests per day)
- The bot may be temporarily down for maintenance
- Your question might not have been detected as a market query

### The Polymarket link doesn't work
This is rare (99.9% success rate), but if it happens:
- The market may have been recently delisted
- There might be a temporary Polymarket API issue
- Try rephrasing your question for a different market

### Can I contact support?
- **Twitter**: DM [@VigVinnie](https://x.com/VigVinnie)
- **GitHub**: Open an issue on [clydedevv/VinnieTheVig](https://github.com/clydedevv/VinnieTheVig)
- **Email**: Create a GitHub issue for the fastest response

## Market Coverage

### What types of markets does VigVinnie cover?
VigVinnie can find markets for:
- **Crypto**: Bitcoin, Ethereum, other token predictions
- **Politics**: Elections, policy decisions, political events
- **Sports**: Major sporting events and outcomes
- **Economics**: Fed decisions, market movements, economic indicators
- **Geopolitics**: International conflicts, diplomatic events
- **Entertainment**: Award shows, celebrity events, cultural predictions

### How often are markets updated?
- Market database syncs hourly with Polymarket
- Expired markets cleaned daily at 3 AM
- Active market count: ~7K out of 114K+ total markets
