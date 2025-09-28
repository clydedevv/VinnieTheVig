# Overview

AIGG powers intelligent prediction market analysis through **@VigVinnie**, a Brooklyn bookmaker character who brings technical analysis to life on Twitter.

<blockquote class="twitter-tweet">
<a href="https://x.com/VigVinnie">Visit @VigVinnie on Twitter</a>
</blockquote>

## What is VigVinnie?

**@VigVinnie** combines AIGG's technical capabilities with an authentic Brooklyn bookmaker personality. Users mention @VigVinnie with market questions and get actionable trading insights in seconds.

### The Character
- **Personality**: Italian-American Brooklyn bookmaker with street-smart betting wisdom
- **Voice**: Uses gambling terminology ("the line's wobbling", "smart money's drifting")
- **Style**: Direct, opinionated analysis with confidence percentages
- **Avatar**: Pepe profile picture that's become iconic in prediction markets

### How It Works

1. **Ask**: Tweet any market question to @VigVinnie
2. **Analysis**: Get Brooklyn bookmaker-style analysis with current context
3. **Action**: Receive clear BUY/SELL/HOLD with confidence score
4. **Trade**: Direct Polymarket link for immediate action

## Example Interaction

**User:** "@VigVinnie NYC mayoral election thoughts?"

**VigVinnie's Response:**
> Word is Mamdani's pulling early traction with 26%-50% in the books, and the line's wobbling. Adams and Cuomo split the Dem vote, so the smart money's drifting toward the progressive yes side. With debates near and the juice shifting, there's value before the late action hits.

**Follow-up Tweet with Link:**
> https://polymarket.com/event/nyc-mayor-2025

This two-tweet pattern delivers both analysis and market access.

## The Problem VigVinnie Solves

Prediction markets are exploding, but discovery remains broken:

- **Discovery is noisy**: 114,450+ markets with inconsistent naming
- **Research takes time**: Markets move fast, analysis is slow
- **Generic bots fail**: Vague responses that don't help trading decisions

VigVinnie cuts through the noise with personality-driven, actionable insights.

## Technical Foundation

VigVinnie is powered by AIGG's technical stack:

- **Database**: 114,450 Polymarket markets, 6,991 active
- **AI Models**: Fireworks (Qwen 3.5 72B) + Perplexity Sonar
- **Framework**: DSPy for structured analysis generation
- **Architecture**: 3-service microservices (Bot, Wrapper, Market API)
- **Response Time**: 30-90 seconds end-to-end

## Key Innovations

### 1. Clean Market Index
- Filters 114K markets down to 6,991 active (94% reduction)
- Daily cleanup removes expired/inactive markets
- 10× faster search with better results

### 2. Smart Matching
- LLM-based semantic search understands real questions
- Handles typos, abbreviations, and context
- Ranks by relevance, volume, and recency

### 3. Consistent Format
- Brooklyn bookmaker personality in every response
- Clear BUY/SELL/HOLD with confidence scores
- Twitter-optimized threading for analysis + links

## Getting Started

### For Users
1. **Follow**: [@VigVinnie](https://x.com/VigVinnie) on Twitter
2. **Tweet**: Any market question mentioning @VigVinnie
3. **Trade**: Get analysis + direct Polymarket access

### For Developers
Want to understand the technical architecture or deploy your own instance? Explore the documentation sections below:

- **[What is AIGG?](getting-started/what-is-aigg.md)** - Technical deep dive
- **[System Architecture](architecture/system-overview.md)** - Infrastructure overview
- **[Deployment Guide](deployment/deployment-guide.md)** - Production setup
- **[AI Pipeline](ai-pipeline/analysis-pipeline.md)** - How insights are generated

## Why VigVinnie Works

Traditional prediction market bots produce generic, unhelpful responses. VigVinnie succeeds because:

- **Authentic Personality**: Brooklyn bookmaker voice users trust
- **Technical Depth**: AIGG's sophisticated matching and analysis
- **Action-Oriented**: Every response includes clear trading signals
- **Fast Execution**: 30-90 second response times
- **Real Markets**: Direct links to actual Polymarket events

## Resources

- **Twitter**: [@VigVinnie](https://x.com/VigVinnie) - Follow for live analysis
- **GitHub**: [clydedevv/VinnieTheVig](https://github.com/clydedevv/VinnieTheVig) - Source code
- **Documentation**: Technical guides and API reference below

Built with the prediction markets community in mind.