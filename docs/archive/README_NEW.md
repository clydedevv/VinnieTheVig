# AIGG - AI-Powered Prediction Market Analysis 🎯

**Smart betting recommendations using real-time market data + AI research**

## 🚀 What it Does

AIGG analyzes prediction markets (like Polymarket) and provides intelligent betting recommendations by:

1. **🔍 Finding Relevant Markets** - Matches your query to active prediction markets
2. **🌐 Web Research** - Uses Perplexity Sonar to research the topic with current data  
3. **🧠 AI Analysis** - Applies Perplexity R1-1776 reasoning to generate insights
4. **💡 Smart Recommendations** - Provides "YES/NO/PASS" with confidence & bet sizing

## ⚡ Quick Start

1. **Clone & Setup**:
   ```bash
   git clone <repo>
   cd aigg
   source .venv/bin/activate  # Activate your existing venv
   ```

2. **Add API Keys** to `.env`:
   ```bash
   PERPLEXITY_API_KEY=pplx-your-key-here
   ```

3. **Run Analysis**:
   ```bash
   python simple_flow.py
   ```

## 🎯 Example Flow

```bash
Input: "Trump election 2024"
↓
🔍 Finds: "Will Donald J. Trump win the 2024 Republican nomination?"
↓ 
🌐 Research: Web search on Trump's current polling, endorsements, etc.
↓
🧠 Analysis: AI reasoning on likelihood based on evidence
↓
💡 Result: "PASS - Insufficient confidence (12%)" + reasoning
```

## 🏗️ Core Architecture

### **simple_flow.py** - Main Implementation
- `PolymarketAPI` - Fetches live market data
- `PerplexityResearcher` - Web search + reasoning
- `MarketAnalyzer` - AI-powered recommendations  
- `AIGGFlow` - Orchestrates the complete flow

### **Key Features:**
✅ **Real-time market data** from Polymarket API  
✅ **Advanced web research** with Perplexity Sonar  
✅ **AI reasoning** with Perplexity R1-1776  
✅ **Smart recommendations** with confidence scoring  
✅ **Clean, simple codebase** - no complex dependencies  

## 🧪 Testing

```bash
# Health check - verify all systems work
python test_flow.py

# Test market matching with different queries  
python test_different_queries.py

# Full enhanced flow test
python test_perplexity_flow.py
```

## 📊 Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| Polymarket API | ✅ Working | 500+ active markets |
| Perplexity Search | ✅ Working | Sonar model |
| Perplexity Reasoning | ✅ Working | R1-1776 model |  
| Market Matching | ✅ Working | Keyword-based |
| AI Recommendations | ✅ Working | Structured output |
| Database | ⚠️ Optional | Not needed for core flow |

## 🔧 Configuration

### Required Environment Variables:
```bash
PERPLEXITY_API_KEY=pplx-xxxxx    # Get from perplexity.ai
```

### Optional (for database features):
```bash
DATABASE_URL=postgresql://user:pass@localhost/aigg_dev
```

## 📁 Project Structure

```
aigg/
├── simple_flow.py          # 🎯 Main working implementation
├── test_flow.py            # 🧪 Health check script  
├── test_different_queries.py # 🔍 Market matching tests
├── test_perplexity_flow.py # 🤖 Enhanced flow demo
├── requirements.txt        # 📦 Dependencies
├── .env                   # 🔑 API keys
└── README_NEW.md          # 📖 This documentation
```

## 🎪 Example Queries to Try

- `"Bitcoin will hit $150k in 2024"`
- `"Federal Reserve will cut interest rates"`  
- `"AI will achieve AGI by 2025"`
- `"Trump election 2024"`
- `"Tesla stock price prediction"`

## 🚀 Next Steps / Enhancements

- [ ] **Better market matching** (semantic similarity vs. keywords)
- [ ] **Price analysis** (compare AI prediction to market odds)
- [ ] **Historical tracking** (store predictions & performance)
- [ ] **Web interface** (FastAPI dashboard)
- [ ] **Voice output** (convert recommendations to specific voice/style)

## 🎯 Perfect For

- **Prediction market trading** - Get data-driven betting insights
- **Market research** - AI-powered analysis of current events  
- **Decision making** - Structured analysis with confidence levels
- **Learning** - Understanding how AI can enhance trading decisions

---

**Built with modern AI tools for the modern prediction market era** 🤖⚡ 