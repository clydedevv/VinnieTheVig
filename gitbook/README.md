# What is AIGG?

AIGG is a Twitter-native companion for Polymarket that transforms market discovery from a research rabbit hole into a 30-second decision. Mention @VigVinnie with any market question and receive an actionable trading recommendation with the exact Polymarket link.

> [Visit @VigVinnie on Twitter](https://x.com/VigVinnie/highlights)

<figure><img src=".gitbook/assets/image.png" alt=""><figcaption></figcaption></figure>

## The Problem We're Tackling

Prediction markets are growing rapidly, but discovering and researching relevant markets remains inconvenient:

* **Market Discovery**: It's unclear if markets even exist for specific events you're curious about
* **Research Overhead**: Doing proper research across thousands of markets is time-intensive  
* **Fragmented Information**: Market data, news context, and analysis are scattered across different sources

People want to know "Is there a market for X?" and "What's the latest context?" but doing this research manually for each question is tedious and slow.

## The Solution

AIGG eliminates this friction with three key innovations:

### 1. Real-Time Market Indexing

We maintain a live database of active Polymarket events with hourly refresh cycles:

* **Active-Only Focus**: Constantly filtering out expired markets as they close
* **Live Data**: Indexing current odds, volume, and key market information  
* **Performance**: Optimized for fast semantic search across active events
* **Architecture**: Built for real-time market discovery and analysis

### 2. AI-Powered Market Matching

Our AI workflow intelligently connects queries to the right markets:

* **Smart Shortlisting**: AI first identifies potential market candidates
* **Semantic Understanding**: Grasps meaning beyond exact keyword matches
* **Context Awareness**: Considers timing, entities, and market relevance
* **Final Selection**: AI ranks and selects the best match from shortlist

### 3. Structured Analysis with Real-Time Research

The key innovation is our DSPy flow that combines market odds with up-to-the-minute news research:

* **Market Data**: Current odds, volume, and activity
* **Perplexity Search**: Latest news and context for time-sensitive events  
* **Structured Generation**: Consistent analysis format with confidence scores
* **Multi-Level Research**: Basic context vs deep research for breaking news

## Who is VigVinnie?


**@VigVinnie** is the Brooklyn bookmaker character who brings AIGG's technical analysis to life on Twitter.

### The Character

* **Personality**: Italian-American Brooklyn bookmaker with street-smart betting wisdom
* **Voice**: Uses classic mafia gambling terminology ("the line's wobbling", "smart money's drifting")
* **Style**: Direct, opinionated analysis with confidence percentages

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

**Example 2: Live Tweet**

<blockquote class="twitter-tweet"><p lang="en" dir="ltr">Word is Mamdani&#39;s pulling early traction with 26%-50% in the books, and the line's wobbling. Adams and Cuomo split the Dem vote, so the smart money's drifting toward the progressive yes side. With debates near and the juice shifting, there's value before the late action hits.…</p>&mdash; Vinnie the Vig (@VigVinnie) <a href="https://twitter.com/VigVinnie/status/1972204098754670903?ref_src=twsrc%5Etfw">September 28, 2025</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>

[See the full thread here](https://x.com/VigVinnie/status/1972204098754670903)

This demonstrates VigVinnie's signature style: market analysis in authentic bookmaker voice, followed by the direct Polymarket link.

> **Disclaimer:** This is not investment advice. Prediction markets are volatile and markets/odds change frequently. Examples are illustrative; links may resolve or become unavailable.

## How The Technology Works

AIGG has the technical foundation to index active markets, semantically match incoming queries, and run a Perplexity DSPy-powered backend search to compile the best sources and research.

**Current Implementation:** The bot replies with a condensed single paragraph followed by a preview of the relevant market.

**Scalability Potential:** This could easily be upscaled to include more professional premium research, KOL opinions, institutional analysis, or multi-tiered intelligence levels.

The flow combines three core technologies:

**Market Indexing** → Live database of active Polymarket events, refreshed hourly

**AI Matching** → Semantic understanding with intelligent shortlisting and final selection

**Research Engine** → Perplexity integration for real-time news and market context

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   TWITTER BOT   │───>│  WRAPPER API    │───>│   MARKET API    │
│   (Monitor)     │    │   (Analysis)    │    │   (Database)    │
│   Port: N/A     │    │   Port: 8003    │    │   Port: 8001    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
    Twitter API            DSPy + Perplexity       PostgreSQL DB
   (Mentions/Replies)      (AI Analysis)         (Active Markets)
```

**Core Stack:**
* **AI Models**: Fireworks (Qwen3-235B-A22B) + Perplexity Sonar/Sonar Pro
* **Framework**: DSPy for structured analysis generation
* **Database**: PostgreSQL with active market indexing
* **Response Time**: Typically 30-90 seconds end-to-end

## Getting Started

### For Users

1. **Follow**: [@VigVinnie](https://x.com/VigVinnie/highlights) on Twitter
2. **Tweet**: Any market question mentioning @VigVinnie
3. **Trade**: Get analysis + direct Polymarket access

### For Developers

Want to understand the technical architecture or deploy your own instance? Explore the documentation sections below:

* [**Quick Start Guide**](getting-started/quick-start.md) - Get AIGG running locally
* [**System Architecture**](architecture/system-overview.md) - Infrastructure overview
* [**Deployment Guide**](deployment/deployment-guide.md) - Production setup
* [**AI Pipeline**](ai-pipeline/analysis-pipeline.md) - How insights are generated


## Resources

* **Twitter**: [@VigVinnie](https://x.com/VigVinnie/highlights) - Follow for live analysis
* **GitHub**: [clydedevv/VinnieTheVig](https://github.com/clydedevv/VinnieTheVig) - Source code
* **Documentation**: Technical guides and API reference below

---

