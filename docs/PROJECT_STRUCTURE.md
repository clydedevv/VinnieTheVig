# 🏗️ AIGG Insights - Project Structure (Updated)

**DSPy-enhanced AI Twitter bot for prediction market analysis with clean, organized structure**

## 📁 **Current Directory Structure**

```
aigg/
├── 📄 **Root Files (Essential Only)**
│   ├── README.md                    # Main project documentation
│   ├── CLAUDE.md                    # Claude AI instructions
│   ├── main.py                      # Central CLI interface
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Environment template
│   └── .gitignore                   # Git ignore rules
│
├── 🤖 **Source Code**
│   └── src/
│       ├── twitter/
│       │   ├── bot.py               # Twitter bot orchestrator (30-sec cycles)
│       │   ├── client.py            # Twitter API v2 integration (X Premium)
│       │   └── whitelist_manager.py # 4-tier access control system
│       ├── api_wrapper/
│       │   └── twitter_wrapper.py   # FastAPI wrapper (Port 8003)
│       ├── flows/
│       │   ├── dspy_enhanced_aigg_flow.py  # 🌟 Main DSPy flow
│       │   ├── llm_market_matcher.py       # LLM-based market matching
│       │   ├── enhanced_aigg_flow.py       # Legacy flow
│       │   ├── api_first_flow.py           # Alternative flows
│       │   └── database_first_flow.py      # Alternative flows
│       ├── utils/
│       │   ├── dspy_utilities.py    # DSPy configuration
│       │   └── check_market_dates.py # Market date utilities
│       └── tests/                   # Legacy test location
│
├── 🌐 **Market API**
│   └── api/
│       ├── main.py                  # FastAPI server (Port 8001)
│       ├── insights.py              # Market insights module
│       ├── llm_search_endpoint.py   # LLM search endpoint
│       └── output_logs/             # API logs (gitignored)
│
├── 🧪 **Testing Suite**
│   └── tests/
│       ├── unit/
│       │   ├── test_llm_market_matching.py
│       │   └── test_market_matching_standalone.py
│       └── integration/
│           ├── test_pipeline_2025_queries.py  # Realistic query tests
│           ├── test_market_matching_real.py
│           └── [other integration tests]
│
├── 📋 **Configuration**
│   └── config/
│       ├── whitelist.json           # Access control list
│       ├── personas/
│       │   └── vinnie.json          # Bot persona config
│       └── aigg-api.service         # Service configuration
│
├── 🛠️ **Scripts & Tools**
│   ├── scripts/
│   │   ├── populate_polymarket_data_clob.py  # Market data sync
│   │   ├── cleanup_inactive_markets.py       # Database cleanup
│   │   ├── manage_whitelist.py               # Access management
│   │   ├── check_status.sh                   # Status checker
│   │   ├── run_streamlit.sh                  # Streamlit runner
│   │   ├── start_services.sh                 # Service starter
│   │   └── continuous_improvement.py         # Improvement script
│   ├── tools/
│   │   └── streamlit_test_app.py    # Streamlit testing UI
│   └── examples/
│       ├── external_client.py       # Example client
│       ├── hierarchal_agents.py     # Agent examples
│       └── research_agent.py        # Research examples
│
├── 📚 **Documentation**
│   └── docs/
│       ├── api/                     # API documentation
│       ├── improvements/            # Feature improvements
│       ├── legal/                   # Privacy & terms
│       ├── migration/               # Migration guides
│       ├── setup/                   # Setup instructions
│       ├── testing/                 # Testing protocols
│       ├── archive/                 # Old documentation
│       └── PROJECT_STRUCTURE.md     # This file
│
├── 🗄️ **Database & Services**
│   ├── migrations/
│   │   └── 001_initial_schema.sql   # Database schema
│   ├── services/
│   │   ├── market_research_service.py
│   │   └── research_service.py
│   └── systemd/
│       ├── aigg-twitter-bot.service
│       └── aigg-wrapper.service
│
└── 📁 **Other Directories**
    ├── logs/                        # Runtime logs (gitignored)
    ├── db/                          # Database files
    ├── reference/                   # Reference implementations
    └── langsearch/                  # Legacy search code
```

## 🚀 **Key Components**

### **DSPy-Enhanced Analysis Pipeline**
```
1. Query Understanding (DSPy)
   ├── Extract key entities and search terms
   ├── Understand temporal context
   └── Identify market type

2. LLM Market Matching
   ├── Pure semantic search (no hardcoded rules)
   ├── Score all markets with LLM
   └── Select best match intelligently

3. Research Phase
   ├── Perplexity Sonar for real-time data
   ├── Structured research queries
   └── Current event analysis

4. Analysis Generation (DSPy)
   ├── Structured output signatures
   ├── Consistent quality
   └── Professional recommendations

5. Twitter Formatting
   ├── Smart truncation
   ├── URL preservation
   └── Character optimization
```

### **AI Technology Stack**
- **DSPy Framework**: Structured prompting and consistent outputs
- **Fireworks AI**: Qwen 3.5 72B for fast inference
- **Perplexity Sonar**: Real-time research and news
- **LLM Market Matcher**: Semantic search without hardcoded rules

## 📊 **Production Configuration**

### **Service Ports**
- `8001`: Market API (public access)
- `8003`: Twitter Wrapper API (internal)

### **Environment Variables**
```bash
# Database
DB_NAME=aigg_insights
DB_USER=postgres
DB_PASSWORD=***
DB_HOST=localhost
DB_PORT=5432

# Twitter API (X Premium)
TWITTER_BEARER_TOKEN=***
TWITTER_API_KEY=***
TWITTER_API_SECRET=***
TWITTER_ACCESS_TOKEN=***
TWITTER_ACCESS_TOKEN_SECRET=***

# AI Services
PERPLEXITY_API_KEY=***
FIREWORKS_API_KEY=***
```

## 🛠️ **Development Commands**

### **Main Entry Points**
```bash
# CLI Commands
python main.py twitter-bot --interval 30 --disable-whitelist
python main.py api-server --port 8001
python main.py wrapper-api --port 8003
python main.py analyze "Bitcoin 200k?"
python main.py status

# Direct Testing
python src/flows/dspy_enhanced_aigg_flow.py
python tests/integration/test_pipeline_2025_queries.py
```

### **Service Management**
```bash
# Using scripts
./scripts/start_services.sh
./scripts/check_status.sh

# Using tmux
tmux new-session -d -s aigg-twitter-bot 'python main.py twitter-bot --interval 30'
tmux new-session -d -s twitter-wrapper 'python src/api_wrapper/twitter_wrapper.py'
tmux new-session -d -s aigg-api 'uvicorn api.main:app --host 0.0.0.0 --port 8001'
```

## 📈 **Recent Changes**

### **Architectural Updates**
1. **DSPy Integration**: Structured prompting for consistent outputs
2. **LLM Market Matching**: Replaced hardcoded rules with AI
3. **Fireworks AI**: Added for faster inference
4. **Repository Cleanup**: Organized structure with clear categories

### **File Organization**
- Moved all tests to `tests/` directory
- Organized documentation in `docs/` with subdirectories
- Moved scripts to `scripts/`
- Created `tools/` for development utilities
- Cleaned root directory (only essential files remain)

## 🔧 **Maintenance Notes**

### **Regular Tasks**
- Database cleanup runs daily at 3 AM
- Market sync runs hourly via cron
- Log rotation configured for all services

### **Key Files to Monitor**
- `src/flows/dspy_enhanced_aigg_flow.py` - Main analysis logic
- `src/flows/llm_market_matcher.py` - Market matching algorithm
- `api/main.py` - Market API endpoints
- `src/twitter/bot.py` - Twitter bot logic

## 🎯 **Production Status**

The system is production-ready with:
- ✅ DSPy framework for quality control
- ✅ LLM-based intelligent market matching
- ✅ Clean, organized repository structure
- ✅ Comprehensive test coverage
- ✅ Automated maintenance
- ✅ Professional documentation

*Built with DSPy for the future of prediction market intelligence* 🤖