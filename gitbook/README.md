# What is AIGG?

AIGG is a Twitter-native companion for Polymarket that transforms market discovery from a research rabbit hole into a 30-second decision. Mention @VigVinnie with any market question and receive an actionable trading recommendation with the exact Polymarket link.

> [Visit @VigVinnie on Twitter](https://x.com/VigVinnie/highlights)

## The Problem We're Tackling

Prediction markets are growing rapidly, but discovering and researching relevant markets remains inconvenient:

* **Market Discovery**: It's unclear if markets even exist for specific events you're curious about
* **Research Overhead**: Doing proper research across thousands of markets is time-intensive  
* **Fragmented Information**: Market data, news context, and analysis are scattered across different sources

People want to know "Is there a market for X?" and "What's the latest context?" but doing this research manually for each question is tedious and slow.

## The Solution

AIGG eliminates this friction with three key innovations:

### 1. Custom, Clean Market Index

We maintain an "active only" index that dramatically improves search performance:

* **Before**: 115,000+ total markets (many expired, duplicates, low volume)  
* **After**: ~6,800 active markets (94% reduction)
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

## How The Technology Works

AIGG has the technical foundation to index active markets, semantically match incoming queries, and run a Perplexity DSPy-powered backend search to compile the best sources and research.

**Current Implementation:** The bot replies with a condensed single paragraph followed by a preview of the relevant market.

**Scalability Potential:** This could easily be upscaled to include more professional premium research, KOL opinions, institutional analysis, or multi-tiered intelligence levels.

The flow combines three core technologies:

**Market Indexing** → We maintain ~6,800 active markets from 115,000+ total, updated daily

**Semantic Matching** → LLM-powered search understands natural language queries and ranks results by relevance

**Research Engine** → Perplexity integration provides real-time context and news for time-sensitive markets

## Technical Foundation

VigVinnie is powered by AIGG's technical stack:

 * **Database**: Indexing ~6,800 active polymarket markets daily
* **AI Models**: Fireworks (Qwen 3.0 235B) + Perplexity Sonar
* **Framework**: DSPy for structured analysis generation
* **Architecture**: 3-service microservices (Bot, Wrapper, Market API)
* **Response Time**: 30-90 seconds end-to-end

## Key Innovations

### 1. Clean Market Index

* Filters thousands of markets down to ~6,800 active daily
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

Built with the emergent prediction markets community in mind.
