# AIGG Repository Cleanup Plan

## 🎯 **Working Core Flow**
The essential working flow is now in `simple_flow.py`:
1. Query → Find relevant Polymarket market
2. Research topic (with OpenAI)
3. Analyze & generate recommendation

## 📁 **What to Keep (Essential)**

### Core Working Files:
- `simple_flow.py` - **Main working implementation**
- `test_flow.py` - **Health check script**
- `requirements.txt` - **Dependencies**
- `README.md` - **Project documentation**
- `.env` - **Environment configuration**

### Database & Persistence (KEEP - Working):
- `db/` directory - **Database connection utilities**
- `migrations/001_initial_schema.sql` - **Database schema**
- `scripts/populate_polymarket_data.py` - **Updated market data population**
- `services/` directory - **Research & market services**

### API Infrastructure (Optional):
- `api/` directory - **If you want a web API**

## 🗑️ **What to Remove/Archive**

### Broken Dependencies:
- `plex-engine/polymarket_plex_flow_multi.py` - **Uses missing 'agno' package**
- `plex-engine/polymarket_plex_flow.py` - **Uses missing 'agno' package**
- `plex-engine/plex.py` - **Uses missing 'agno' package**

### Complex/Unused:
- `reference/` directory - **Example code, not essential**
- `langsearch/` directory - **Complex LangChain implementation**
- `migrations/` directory - **Only needed if using database**
- `examples/` directory - **Not essential for core flow**

### Database Notes (Optional):
- `dbnotes.txt` - **Database setup notes** (move to docs)
- `config/aigg-api.service` - **Systemd service config** (move to optional)

## 🧹 **Cleanup Actions**

### 1. Archive Broken Code:
```bash
mkdir archive
mv plex-engine/ archive/
mv reference/ archive/
mv langsearch/ archive/
mv examples/ archive/
```

### 2. Keep Optional But Organize:
```bash
mkdir optional/
mv api/ optional/
mv config/ optional/
mkdir docs/
mv dbnotes.txt docs/
# Keep db/, services/, migrations/, scripts/ in root - they're working!
```

### 3. Clean Root Directory:
```bash
rm count
rm commit_message.txt  
rm dbnotes.txt
```

## 🎯 **Recommended Final Structure**

```
aigg/
├── simple_flow.py          # ✅ Main working flow
├── test_flow.py            # ✅ Health check
├── requirements.txt        # ✅ Dependencies  
├── README.md              # ✅ Documentation
├── .env                   # ✅ Environment config
├── .gitignore            # ✅ Git config
├── optional/             # 📁 Optional features
│   ├── api/              # Web API implementation
│   ├── services/         # Modular services
│   ├── db/               # Database setup
│   └── scripts/          # Utility scripts
└── archive/              # 📁 Non-working code
    ├── plex-engine/      # Original broken implementation
    ├── reference/        # Example code
    └── langsearch/       # Complex LangChain code
```

## 🚀 **Next Steps to Get Fully Working**

1. **Add your OpenAI API key to `.env`**:
   ```bash
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

2. **Test the working flow**:
   ```bash
   python simple_flow.py
   ```

3. **Try different queries**:
   ```python
   # Edit simple_flow.py main() function
   test_query = "Bitcoin price 2024"
   test_query = "Election outcome"
   test_query = "Stock market crash"
   ```

## 🔧 **Optional Enhancements**

- Add Perplexity API for better research
- Set up PostgreSQL for data persistence  
- Create a web interface with FastAPI
- Add more sophisticated market matching
- Implement the "voice" conversion feature

## ✨ **Summary**

You now have a **clean, working core** that does exactly what you wanted:
- Finds relevant prediction markets
- Conducts AI research
- Makes betting recommendations

The cleanup removes all the broken dependencies and complex code that wasn't working. 