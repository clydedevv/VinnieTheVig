import streamlit as st
import time
import os
import sys
from datetime import datetime

# Add the parent directory to the path to import from src
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Set production API URL if specified
if os.getenv('USE_PRODUCTION_API', 'false').lower() == 'true':
    os.environ['MARKET_API_URL'] = 'http://65.108.231.245:8001'

from src.flows.dspy_enhanced_aigg_flow import DSPyEnhancedAIGGFlow

# Monkey patch to use production API if needed
if os.getenv('USE_PRODUCTION_API', 'false').lower() == 'true':
    original_get_markets = DSPyEnhancedAIGGFlow.get_top_markets
    
    def patched_get_markets(self, query: str, limit: int = 10):
        original_base = self.api_base
        self.api_base = "http://65.108.231.245:8001"
        try:
            # The production API should now properly search
            print(f"🔍 Using production search API for: '{query}'")
            results = original_get_markets(self, query, limit)
            if results and len(results) > 0:
                print(f"📊 Got {len(results)} results from search, top 3:")
                for i, market in enumerate(results[:3]):
                    print(f"   {i+1}. {market.relevance_score:.3f}: {market.title[:60]}...")
            else:
                print(f"❌ No markets found for query: '{query}'")
            return results
        finally:
            self.api_base = original_base
    
    DSPyEnhancedAIGGFlow.get_top_markets = patched_get_markets

# Page configuration
st.set_page_config(
    page_title="AIGG Insights Test Interface",
    page_icon="🎯",
    layout="wide"
)

# Title and description
st.title("🎯 AIGG Insights Test Interface")
if os.getenv('USE_PRODUCTION_API', 'false').lower() == 'true':
    st.markdown("Test the AI-powered prediction market analysis using **production server**")
    st.info("📡 Connected to production server at 65.108.231.245")
else:
    st.markdown("Test the AI-powered prediction market analysis using **local server**")
    st.warning("⚠️ Using local API - make sure Market API is running on port 8001")

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []

# Create two columns
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Query Analysis")
    
    # Query input
    query = st.text_input(
        "Enter your prediction market query:",
        placeholder="e.g., Will Bitcoin reach $150k by end of 2025?",
        help="Ask any question about future events that might have a prediction market"
    )
    
    # Analyze button
    if st.button("🔍 Analyze", type="primary", disabled=not query):
        with st.spinner("Analyzing your query..."):
            try:
                start_time = time.time()
                
                # Initialize the flow
                flow = DSPyEnhancedAIGGFlow()
                
                # Show debug info
                with st.expander("🔍 Debug Info", expanded=True):
                    st.write(f"API Base: {flow.api_base}")
                    st.write(f"Perplexity Key: {'✅ Set' if flow.perplexity_key else '❌ Missing'}")
                    st.write(f"LLM Matcher: {'✅ v2 Ready' if hasattr(flow, 'llm_market_matcher') else '❌ Missing'}")
                    
                    # Show query understanding
                    try:
                        search_terms, topic, entities = flow.dspy_understand_query(query)
                        st.write(f"**Original Query:** {query}")
                        st.write(f"**Topic:** {topic}")
                        st.write(f"**Entities:** {entities}")
                        st.write(f"**Search Terms:** {search_terms}")
                    except:
                        # Fallback to simple preprocessing
                        preprocessed = flow.preprocess_search_query(query)
                        st.write(f"**Original Query:** {query}")
                        st.write(f"**Preprocessed Query:** {preprocessed}")
                
                # Run analysis
                result = flow.analyze_query(query)
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                # Check if result is valid
                if result is None:
                    st.error("Analysis failed. Please check that the Market API is running and the database is accessible.")
                    st.info("To start the Market API: `python main.py api-server --port 8001`")
                    st.info("Make sure PostgreSQL is running on localhost:5432")
                else:
                    # Display results
                    st.success(f"Analysis completed in {processing_time:.2f} seconds")
                    
                    # Market Information
                    st.subheader("📊 Market Information")
                    if result.selected_market:
                        st.write(f"**Market:** {result.selected_market.title}")
                        st.write(f"**Category:** {result.selected_market.category}")
                        st.write(f"**Relevance Score:** {result.selected_market.relevance_score:.3f}")
                        if result.polymarket_url:
                            st.markdown(f"[View on Polymarket]({result.polymarket_url})")
                    
                    # Analysis Results
                    st.subheader("🤖 AI Analysis")
                    st.write(f"**Analysis:** {result.analysis}")
                    st.write(f"**Recommendation:** {result.recommendation}")
                    st.write(f"**Confidence:** {result.confidence * 100:.0f}%")
                    
                    # Research Summary with enhanced sections
                    with st.expander("📚 Enhanced Research Summary", expanded=True):
                        if "CURRENT SITUATION" in result.research_summary:
                            # Parse the structured research output
                            sections = result.research_summary.split('\n\n')
                            for section in sections:
                                if section.strip():
                                    st.markdown(section)
                        else:
                            # Fallback for old format
                            st.write(result.research_summary)
                    
                    # Twitter Preview
                    st.subheader("🐦 Twitter Response Preview")
                    # Format as Twitter would see it
                    twitter_response = f"{result.analysis} {result.recommendation} (Confidence: {result.confidence * 100:.0f}%) {result.polymarket_url}"
                    st.text_area("Response:", value=twitter_response, height=100, disabled=True)
                    st.caption(f"Character count: {len(twitter_response)}/280")
                    
                    # Add to history
                    st.session_state.history.append({
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'query': query,
                        'market': result.selected_market.title if result.selected_market else 'N/A',
                        'recommendation': result.recommendation,
                        'confidence': f"{result.confidence * 100:.0f}",
                        'time': f"{processing_time:.2f}s"
                    })
                
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
                st.exception(e)

with col2:
    st.header("Test History")
    
    if st.session_state.history:
        for i, item in enumerate(reversed(st.session_state.history[-10:])):  # Show last 10
            with st.expander(f"{item['timestamp']} - {item['time']}"):
                st.write(f"**Query:** {item['query']}")
                st.write(f"**Market:** {item['market']}")
                st.write(f"**Rec:** {item['recommendation']} ({item['confidence']}%)")
    else:
        st.info("No queries analyzed yet")

# Example queries section
st.divider()
st.subheader("📝 Example Queries")

# Updated with realistic 2025 Twitter-style queries
example_queries = [
    "yo is btc finally hitting 200k or nah",
    "china taiwan situation getting spicy 👀",
    "fed cutting rates or jerome powell cappin",
    "taylor swift engaged yet? my gf keeps asking",
    "trump winning 2024 ez clap or what",
    "gpt-5 dropping soon? need that 10x improvement"
]

cols = st.columns(3)
for i, example in enumerate(example_queries):
    with cols[i % 3]:
        if st.button(example, key=f"example_{i}"):
            st.rerun()

# Twitter Wrapper API test section
st.divider()
with st.expander("🔧 Test Twitter Wrapper API Directly"):
    st.markdown("Test the full analysis pipeline via the Twitter Wrapper API (port 8003)")
    
    wrapper_query = st.text_input("Query for wrapper API:", key="wrapper_query")
    
    col1, col2 = st.columns(2)
    with col1:
        user_id = st.text_input("User ID:", value="test_user", key="user_id")
    with col2:
        user_handle = st.text_input("User Handle:", value="test_user", key="user_handle")
    
    if st.button("Test Wrapper API", disabled=not wrapper_query):
        import requests
        
        wrapper_url = "http://65.108.231.245:8003/analyze" if os.getenv('USE_PRODUCTION_API', 'false').lower() == 'true' else "http://localhost:8003/analyze"
        
        with st.spinner("Calling Twitter Wrapper API..."):
            try:
                response = requests.post(
                    wrapper_url,
                    json={
                        "query": wrapper_query,
                        "user_id": user_id,
                        "user_handle": user_handle
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ Wrapper API Response:")
                    st.json(result)
                else:
                    st.error(f"❌ Error: {response.status_code}")
                    st.text(response.text)
                    
            except Exception as e:
                st.error(f"❌ Failed to connect: {str(e)}")

# Show improvements made
st.divider()
with st.expander("✨ Recent Improvements", expanded=False):
    st.markdown("""
    **Market Matching V2:**
    - ✅ Two-stage category filtering for 51K+ markets
    - ✅ Strict relevance checking (no more China→Bitcoin)
    - ✅ Proper score differentiation (HIGH/MEDIUM/LOW)
    
    **Enhanced Perplexity Research:**
    - ✅ Extracts topics WITHOUT revealing prediction context
    - ✅ Gets actual news/data instead of speculation
    - ✅ Structured output: Current Situation, Key Data, Upcoming Catalysts
    
    **Better for Twitter:**
    - ✅ Handles casual queries ("btc 200k or nah")
    - ✅ No hashtags needed (2025 style)
    - ✅ Concise, actionable responses
    """)

# Footer
st.divider()
st.caption("AIGG Insights Test Interface - Enhanced with V2 Market Matching & Better Research")