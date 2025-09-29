# AIGG - A Polymarket Companion

AIGG is a Twitter-native companion for Polymarket that transforms market discovery from a research rabbit hole into a 30-second decision. Mention @VigVinnie with any market question and receive an actionable trading recommendation with the exact Polymarket link.

> [Visit @VigVinnie on Twitter](https://x.com/VigVinnie/highlights)

## The Problem We're Tackling

Prediction markets are exploding in popularity, but the user experience remains fragmented:

* **Discovery is noisy**: 114,450+ markets across different categories
* **Naming is inconsistent**: Same events titled differently  
* **Timing matters**: Markets move fast, research takes time
* **Generic bots fail**: Vague responses that don't help trading decisions

Most traders either can't find the right market quickly or don't have time to research it properly. This friction prevents confident participation and creates missed opportunities.

## The Solution

AIGG eliminates this friction with three key innovations:

### 1. Custom, Clean Market Index

We maintain an "active only" index that dramatically improves search performance:

* **Before**: 114,450 total markets (many expired, duplicates, low volume)
* **After**: 6,991 active markets (94% reduction)
* **Result**: 10× faster search, more relevant results
* **Updates**: Daily cleanup at 03:00 UTC

### 2. AI Matcher That Understands Real Questions

Our matching engine combines multiple techniques for accuracy:

* **Fuzzy Matching**: Handles typos, abbreviations, variations
* **Semantic Matching**: Understands meaning and context  
* **Entity Recognition**: Identifies people, dates, events
* **Relevance Ranking**: Prioritizes by volume, recency, status

### 3. Structured Analysis with Real-Time Research

The key innovation is our DSPy flow that combines market odds with up-to-the-minute news research:

* **Market Data**: Current odds, volume, and activity
* **Perplexity Search**: Latest news and context for time-sensitive events  
* **Structured Generation**: Consistent analysis format with confidence scores
* **Multi-Level Research**: Basic context vs deep research for breaking news

## Who is VigVinnie?

<figure><img src=".gitbook/assets/image.png" alt=""><figcaption></figcaption></figure>

**@VigVinnie** is the Brooklyn bookmaker character who brings AIGG's technical analysis to life on Twitter.

### The Character

* **Personality**: Italian-American Brooklyn bookmaker with street-smart betting wisdom
* **Voice**: Uses gambling terminology ("the line's wobbling", "smart money's drifting")
* **Style**: Direct, opinionated analysis with confidence percentages
* **Avatar**: Pepe profile picture that's become iconic in prediction markets

### The VigVinnie Experience

1. **Ask**: Tweet any market question to @VigVinnie
2. **Analysis**: Get Brooklyn bookmaker-style analysis with current context
3. **Action**: Receive clear BUY/SELL/HOLD with confidence score
4. **Trade**: Direct Polymarket link for immediate action

**What makes VigVinnie special:**

* **Real-Time Intelligence**: Each response includes the very latest news and context
* **Market Understanding**: Combines technical odds analysis with current events
* **Authentic Voice**: Brooklyn bookmaker personality that cuts through noise
* **Threaded Responses**: Analysis tweet followed by clean preview link

## Example Interaction

<figure><img src=".gitbook/assets/image (1).png" alt=""><figcaption></figcaption></figure>

**Example 2:**&#x20;

**User:** "@VigVinnie NYC mayoral election thoughts?"

**VigVinnie's Response:**

> Word is Mamdani's pulling early traction with 26%-50% in the books, and the line's wobbling. Adams and Cuomo split the Dem vote, so the smart money's drifting toward the progressive yes side. With debates near and the juice shifting, there's value before the late action hits.

**Follow-up Tweet with Link:**

> https://polymarket.com/event/nyc-mayor-2025

This two-tweet pattern delivers both analysis and market access.

## How The DSPy Flow Works

The magic happens in our structured analysis pipeline:

### Step 1: Smart Market Matching
* Parse natural language queries ("Fed cutting rates?")
* Search 6,991 active markets semantically
* Rank by relevance, volume, and recency

### Step 2: Real-Time Research Engine  
* Detect time-sensitive topics automatically
* Query Perplexity Sonar for breaking news
* Gather market context and sentiment

### Step 3: Structured Analysis Generation
* Combine market data with fresh research
* Generate Brooklyn bookmaker-style analysis
* Include confidence scores and clear recommendations

### Step 4: Multi-Level Research Depth
* **Basic**: Market odds + recent context
* **Enhanced**: Breaking news + sentiment analysis  
* **Deep**: Full research for major events

This structured approach ensures every response is both timely and actionable.

## Technical Foundation

VigVinnie is powered by AIGG's technical stack:

* **Database**: Sifting through \~100k Polymarket markets weekly, 6,991 active on a daily basis
* **AI Models**: Fireworks (Qwen 3.0 235B) + Perplexity Sonar
* **Framework**: DSPy for structured analysis generation
* **Architecture**: 3-service microservices (Bot, Wrapper, Market API)
* **Response Time**: 30-90 seconds end-to-end

## Key Innovations

### 1. Clean Market Index

* Filters thousands of markets down to 6,991 active daily
* Daily cleanup removes expired/inactive markets
* 10× faster search with better results

### 2. Smart Matching

* LLM-based semantic search understands real questions
* Handles typos, abbreviations, and context
* Ranks by relevance, volume, and recency

### 3. Consistent Format

* Brooklyn bookmaker personality in every response
* Clear BUY/SELL/HOLD with confidence scores
* Twitter-optimized threading for analysis + links

## Getting Started

### For Users

1. **Follow**: [@VigVinnie](https://x.com/VigVinnie/highlights) on Twitter
2. **Tweet**: Any market question mentioning @VigVinnie
3. **Trade**: Get analysis + direct Polymarket access

### For Developers

Want to understand the technical architecture or deploy your own instance? Explore the documentation sections below:

* [**What is AIGG?**](getting-started/what-is-aigg.md) - Technical deep dive
* [**System Architecture**](architecture/system-overview.md) - Infrastructure overview
* [**Deployment Guide**](deployment/deployment-guide.md) - Production setup
* [**AI Pipeline**](ai-pipeline/analysis-pipeline.md) - How insights are generated

## Why VigVinnie Works

Traditional prediction market bots produce generic, unhelpful responses. VigVinnie succeeds because:

* **Technical Depth**: AIGG's sophisticated matching and analysis
* **Action-Oriented**: Every response includes clear trading signals
* **Fast Execution**: 30-90 second response times
* **Real Markets**: Direct links to actual Polymarket events

## Resources

* **Twitter**: [@VigVinnie](https://x.com/VigVinnie/highlights) - Follow for live analysis
* **GitHub**: [clydedevv/VinnieTheVig](https://github.com/clydedevv/VinnieTheVig) - Source code
* **Documentation**: Technical guides and API reference below

Built with the prediction markets community in mind.
