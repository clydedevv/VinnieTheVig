#!/usr/bin/env python3
"""
DSPy Enhanced AIGG Flow - Production Ready with Structured Prompting
Uses DSPy for consistent, structured inputs and outputs
"""
import os
import json
import requests
import dspy
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.utils.dspy_utilities import lm as fireworks_lm
from src.flows.llm_market_matcher_v2 import LLMMarketMatcherV2, MarketData

load_dotenv()

@dataclass
class Market:
    """Market data structure"""
    id: str
    title: str
    category: str = ""
    active: bool = True
    end_date: Optional[str] = None
    relevance_score: float = 0.0
    market_slug: str = ""

class MarketAnalysis(BaseModel):
    """Structured output for market analysis"""
    analysis: str = Field(description="Concise analysis with specific data points (80-120 chars)")
    recommendation: str = Field(description="BUY/SELL/HOLD with reason (max 40 chars)")
    confidence: float = Field(description="Confidence level between 0.5-0.9", ge=0.5, le=0.9)
    reasoning: str = Field(description="Detailed reasoning behind the analysis")

class MarketSelection(BaseModel):
    """Structured output for market selection"""
    selected_index: int = Field(description="Index of selected market (1-based)")
    reasoning: str = Field(description="Why this market was selected")

class AnalyzeMarket(dspy.Signature):
    """Analyze a prediction market with structured output"""
    
    market_title: str = dspy.InputField(description="The market question to analyze")
    category: str = dspy.InputField(description="Market category")
    research_summary: str = dspy.InputField(description="Research findings about this market")
    current_date: str = dspy.InputField(description="Current date for time-sensitive analysis")
    
    analysis: str = dspy.OutputField(description="Concise analysis mentioning specific factors like institutions, price levels, policy changes (80-120 chars)")
    recommendation: str = dspy.OutputField(description="Clear BUY/SELL/HOLD decision with specific reason (max 40 chars)")
    confidence: float = dspy.OutputField(description="Confidence level between 0.5-0.9")

class UnderstandQuery(dspy.Signature):
    """Extract key entities and intent from user query"""
    
    query: str = dspy.InputField(description="User's original query about prediction markets")
    
    key_entities: str = dspy.OutputField(description="Most important unique entities (names, specific events) - max 3 words")
    topic: str = dspy.OutputField(description="Main topic in 2-5 words (e.g., 'Epstein documents release', 'Bitcoin price prediction')")
    search_terms: str = dspy.OutputField(description="1-3 most distinctive search terms that would uniquely identify relevant markets")

class SelectBestMarket(dspy.Signature):
    """Select the most relevant market from candidates"""
    
    query: str = dspy.InputField(description="User's original query")
    market_options: str = dspy.InputField(description="List of market options with scores")
    
    selected_number: int = dspy.OutputField(description="Number of the most relevant market (1-10)")
    reasoning: str = dspy.OutputField(description="Why this market is most relevant")

class ExtractResearchTopic(dspy.Signature):
    """Extract the core topic to research from a prediction market question"""
    
    market_question: str = dspy.InputField(description="The prediction market question (e.g., 'Will Bitcoin reach $200k by 2025?')")
    
    research_topic: str = dspy.OutputField(description="Core topic to research WITHOUT mentioning predictions (e.g., 'Bitcoin price trends and factors influencing valuation')")
    key_aspects: str = dspy.OutputField(description="Specific aspects to investigate (e.g., 'institutional adoption, regulatory changes, macroeconomic factors')")

class ResearchMarket(dspy.Signature):
    """Research a topic comprehensively without revealing it's for prediction markets"""
    
    research_topic: str = dspy.InputField(description="Topic to research (NOT phrased as a prediction)")
    key_aspects: str = dspy.InputField(description="Specific aspects to investigate")
    category: str = dspy.InputField(description="General category (crypto, politics, sports, etc)")
    current_date: str = dspy.InputField(description="Current date for temporal context")
    
    current_situation: str = dspy.OutputField(description="What's happening RIGHT NOW with this topic? Latest developments from past 48 hours")
    key_data_points: str = dspy.OutputField(description="Specific numbers, statistics, expert opinions, polls, or measurable indicators")
    upcoming_catalysts: str = dspy.OutputField(description="Scheduled events or known future developments that could impact this topic")
    market_dynamics: str = dspy.OutputField(description="Supply/demand factors, sentiment indicators, or market-specific mechanics")
    research_summary: str = dspy.OutputField(description="Executive summary connecting all findings")

@dataclass
class DSPyAIGGResult:
    """Final AIGG analysis result using DSPy"""
    selected_market: Market
    research_summary: str
    analysis: str
    recommendation: str
    confidence: float
    polymarket_url: str
    reasoning: str

class DSPyEnhancedAIGGFlow:
    """DSPy Enhanced AIGG Flow with structured prompting"""
    
    def __init__(self):
        self.api_base = "http://localhost:8001"
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        self.current_date = datetime.now(timezone.utc)
        
        # Configure DSPy with Fireworks for general inference
        dspy.configure(lm=fireworks_lm)
        
        # Keep Perplexity for search operations
        self.perplexity_lm = None
        if self.perplexity_key:
            self.perplexity_lm = dspy.LM(
                model="perplexity/sonar",
                api_key=self.perplexity_key,
                api_base="https://api.perplexity.ai"
            )
        
        # Initialize DSPy modules with Fireworks LM
        self.query_understander = dspy.Predict(UnderstandQuery)
        self.market_selector = dspy.Predict(SelectBestMarket)
        self.market_analyzer = dspy.Predict(AnalyzeMarket)
        self.topic_extractor = dspy.ChainOfThought(ExtractResearchTopic)
        
        # Initialize LLM-based market matcher V2
        self.llm_market_matcher = LLMMarketMatcherV2()
        print("   📂 Using category-based market matching")
        
        # For market researcher, we'll use Perplexity since it needs search
        if self.perplexity_lm:
            # Create a separate context for research that uses Perplexity
            with dspy.context(lm=self.perplexity_lm):
                self.market_researcher = dspy.ChainOfThought(ResearchMarket)
        else:
            # Fallback to Fireworks if no Perplexity key
            self.market_researcher = dspy.ChainOfThought(ResearchMarket)
        
        print(f"🚀 DSPy Enhanced AIGG Flow initialized")
        print(f"🗓️ Current date: {self.current_date.strftime('%Y-%m-%d %H:%M UTC')}")
        print(f"🌐 Market API: {self.api_base}")
        print(f"🧠 Inference: Fireworks AI (qwen3)")
        print(f"🔍 Search: Perplexity {'✅' if self.perplexity_lm else '❌'}")
    
    def dspy_understand_query(self, query: str) -> tuple[str, str, str]:
        """Use DSPy to understand the query and extract search terms"""
        try:
            print("🧠 Using DSPy to understand query...")
            result = self.query_understander(query=query)
            print(f"   📌 Topic: {result.topic}")
            print(f"   🔑 Entities: {result.key_entities}")
            print(f"   🔍 Search terms: {result.search_terms}")
            return result.search_terms, result.topic, result.key_entities
        except Exception as e:
            print(f"⚠️ DSPy query understanding failed: {e}")
            # Fallback to basic extraction
            search_terms = self.preprocess_search_query(query)
            return search_terms, "", ""
    
    def preprocess_search_query(self, query: str) -> str:
        """Preprocess user query for better market search results"""
        query_lower = query.lower()
        
        # Iran/Nuclear deal queries - specific handling
        if any(word in query_lower for word in ['iran', 'nuclear', 'deal', 'sanctions', 'jcpoa']):
            if any(word in query_lower for word in ['us', 'america', 'deal', 'agreement', 'sanctions']):
                return "Iran nuclear deal US sanctions JCPOA agreement diplomacy"
        
        # Election queries - extract key terms
        if any(word in query_lower for word in ['election', 'win', 'mayor', 'president']):
            if 'nyc' in query_lower or 'new york' in query_lower:
                if 'mayor' in query_lower:
                    return "NYC mayoral 2025"
            if 'irish' in query_lower or 'ireland' in query_lower:
                return "Irish presidential election"
            if 'trump' in query_lower or 'biden' in query_lower or 'us president' in query_lower:
                return "US presidential election 2024"
        
        # Bitcoin/Crypto queries - preserve price levels
        if any(word in query_lower for word in ['bitcoin', 'btc', 'crypto']):
            # Extract price levels if mentioned
            import re
            price_match = re.search(r'(\d+)k|(\$\d+,?\d*)', query_lower)
            if price_match:
                # Keep the query mostly intact for price-specific queries
                return query.replace('?', '').replace('reaching', 'reach').strip()
            elif any(word in query_lower for word in ['price', 'reach', '$', 'hit']):
                return "Bitcoin price cryptocurrency"
        
        # Fed/Interest rate queries - be more specific
        if 'federal reserve' in query_lower or 'fed' in query_lower:
            if 'interest' in query_lower and 'rate' in query_lower:
                # Keep phrase intact for better matching
                return "Federal Reserve interest rates"
            elif 'rate cut' in query_lower or 'cut rate' in query_lower:
                return "Fed rate cut FOMC"
            elif 'march' in query_lower:
                return "Fed March FOMC rate cut"
            else:
                return "Federal Reserve interest rates FOMC monetary policy"
        
        # Geopolitical queries
        if any(word in query_lower for word in ['ukraine', 'russia', 'war', 'ceasefire']):
            if 'ceasefire' in query_lower:
                return "Russia Ukraine ceasefire"
            elif 'peace' in query_lower:
                return "Russia Ukraine peace agreement"
            else:
                return "Ukraine Russia war conflict"
        
        # Sports queries - preserve team/league names
        if any(word in query_lower for word in ['champions league', 'premier league', 'nba']):
            # Keep sports queries mostly intact
            return query.replace('?', '').replace('who will win', '').replace('winner', '').strip()
        
        # Epstein/Maxwell queries - preserve full context
        if any(word in query_lower for word in ['epstein', 'maxwell', 'ghislaine']):
            # Keep the essential parts of the query
            return query.replace('?', '').replace('Will', '').replace('will', '').strip()
        
        # Diddy/P.Diddy queries
        if any(word in query_lower for word in ['diddy', 'combs', 'sean combs', 'p.diddy']):
            return query.replace('?', '').replace('Will', '').replace('will', '').strip()
        
        # Default: return expanded key words
        import re
        # Remove question words and extract key terms
        key_terms = re.sub(r'\b(who|what|when|where|will|should|i|the|a|an|for|to|on|in|of)\b', '', query_lower)
        key_terms = re.sub(r'\s+', ' ', key_terms).strip()
        
        return key_terms if key_terms else query
    
    def get_top_markets(self, query: str, limit: int = 10) -> List[Market]:
        """Get top relevant markets using category-based matching"""
        try:
            # Use the SEARCH endpoint to get relevant markets
            url = f"{self.api_base}/markets/search"
            params = {"q": query, "limit": 30}  # Reduced from 50 to speed up scoring
            
            print(f"🔍 Searching for markets matching: '{query}'")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            markets_data = data.get('markets', [])
            
            # Convert to MarketData objects for LLM matcher
            market_candidates = []
            for market_data in markets_data:
                market_candidates.append(MarketData(
                    id=str(market_data.get('id', market_data.get('market_id', ''))),
                    title=market_data.get('title', ''),
                    category=market_data.get('category', ''),
                    end_date=market_data.get('end_date'),
                    active=market_data.get('active', True),
                    market_slug=market_data.get('market_slug', '')
                ))
            
            if not market_candidates:
                print("❌ No active markets found")
                return []
            
            print(f"📊 Found {len(market_candidates)} active markets")
            
            # Use LLM to find best matches
            best_matches = self.llm_market_matcher.find_best_markets(
                query=query,
                markets=market_candidates,
                top_k=limit
            )
            
            # Convert back to Market objects with scores
            markets = []
            for market_data, score, reasoning in best_matches:
                market = Market(
                    id=market_data.id,
                    title=market_data.title,
                    category=market_data.category,
                    active=market_data.active,
                    end_date=market_data.end_date,
                    relevance_score=score,
                    market_slug=market_data.market_slug
                )
                markets.append(market)
            
            return markets
            
        except Exception as e:
            print(f"❌ Error getting markets: {e}")
            return []
    
    def _get_top_markets_v2(self, query: str, limit: int = 10) -> List[Market]:
        """V2: Category-based market search with two-stage filtering"""
        try:
            print(f"🔍 V2 Matcher: Getting markets for '{query}'")
            
            # Step 1: Get all unique categories
            url = f"{self.api_base}/markets"
            params = {"limit": 1, "active": True}  # Just to get categories
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            # Get categories from a larger sample
            params = {"limit": 100, "active": True}
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            # Extract unique categories
            categories_set = set()
            for market in data.get('markets', []):
                if market.get('category'):
                    categories_set.add(market['category'])
            
            available_categories = sorted(list(categories_set))
            print(f"   📂 Found {len(available_categories)} categories")
            
            # Step 2: Organize markets by category
            # For efficiency, use search API to get relevant markets first
            search_url = f"{self.api_base}/markets/search"
            search_params = {"q": query, "limit": 100}  # Get more for category organization
            response = requests.get(search_url, params=search_params, timeout=10)
            response.raise_for_status()
            
            search_data = response.json()
            all_markets = search_data.get('markets', [])
            
            # Organize by category
            markets_by_category = {}
            for market_data in all_markets:
                category = market_data.get('category', 'Uncategorized')
                if category not in markets_by_category:
                    markets_by_category[category] = []
                markets_by_category[category].append(market_data)
            
            print(f"   📊 Markets in {len(markets_by_category)} categories from search")
            
            # Step 3: Use V2 matcher to find best markets
            best_matches = self.llm_market_matcher_v2.find_best_markets(
                query=query,
                markets_by_category=markets_by_category,
                available_categories=available_categories,
                top_k=limit
            )
            
            # Convert to Market objects
            markets = []
            for match in best_matches:
                # Find the full market data
                market_data = None
                for mkt in all_markets:
                    if mkt.get('market_id', mkt.get('id')) == match.market_id:
                        market_data = mkt
                        break
                
                if market_data:
                    market = Market(
                        id=match.market_id,
                        title=match.title,
                        category=match.category,
                        active=market_data.get('active', True),
                        end_date=market_data.get('end_date'),
                        relevance_score=match.relevance_score,
                        market_slug=market_data.get('market_slug', '')
                    )
                    markets.append(market)
            
            return markets
            
        except Exception as e:
            print(f"⚠️ V2 matcher error: {e}, falling back to V1")
            return self._get_top_markets_v1(query, limit)
    
    def dspy_select_best_market(self, query: str, markets: List[Market]) -> Optional[Market]:
        """Use DSPy to intelligently select the most relevant market"""
        if not markets:
            return None
            
        if not self.perplexity_key:
            print("⚠️ No Perplexity key, using top market")
            return markets[0]
        
        # If we only have one market, return it
        if len(markets) == 1:
            return markets[0]
        
        try:
            print("🤖 Using DSPy to select best market...")
            
            # Prepare market options string
            market_options = []
            for i, market in enumerate(markets[:10], 1):  # Limit to 10 for LLM
                market_options.append(f"{i}. {market.title}")
            market_options_str = "\n".join(market_options)
            
            # Use DSPy signature
            result = self.market_selector(
                query=query,
                market_options=market_options_str
            )
            
            # Extract the selected number
            try:
                selected_idx = int(result.selected_number) - 1
                if 0 <= selected_idx < len(markets):
                    selected_market = markets[selected_idx]
                    print(f"🎯 DSPy selected: {selected_market.title}")
                    print(f"   📝 Reasoning: {result.reasoning}")
                    return selected_market
            except (ValueError, AttributeError):
                print(f"⚠️ Could not parse selection: {result.selected_number}")
                
        except Exception as e:
            print(f"⚠️ DSPy selection error: {e}")
            
        # Fallback to direct API call if DSPy fails
        try:
            print("🔄 Trying direct Perplexity API...")
            
            market_list = []
            for i, market in enumerate(markets[:10], 1):
                market_list.append(f"{i}. {market.title}")
            
            selection_prompt = f"""User Query: "{query}"

Available Markets:
{chr(10).join(market_list)}

Select the market number that BEST matches what the user is asking about.
Consider the specific entities, events, and timeframes mentioned.

Respond with ONLY the number (1-{min(len(markets), 10)})."""

            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.perplexity_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "sonar",
                    "messages": [{"role": "user", "content": selection_prompt}],
                    "max_tokens": 10,
                    "temperature": 0.1
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                selection_text = result['choices'][0]['message']['content'].strip()
                
                # Extract number from response
                import re
                number_match = re.search(r'\b(\d+)\b', selection_text)
                if number_match:
                    selected_idx = int(number_match.group(1)) - 1  # Convert to 0-based
                    if 0 <= selected_idx < len(markets):
                        selected_market = markets[selected_idx]
                        print(f"🎯 LLM selected: {selected_market.title}")
                        print(f"   📝 Selection: {selection_text}")
                        return selected_market
            else:
                print(f"⚠️ Perplexity API error: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
            
            print("⚠️ LLM selection failed, using top market")
            return markets[0]
                
        except Exception as e:
            print(f"⚠️ LLM selection error: {e}, using top market")
            return markets[0]
    
    def dspy_research_market(self, market: Market, original_query: str = "") -> str:
        """Use DSPy for structured market research WITHOUT revealing it's for predictions"""
        if not self.perplexity_lm:
            return f"Research summary for: {market.title} (No Perplexity key available)"
        
        try:
            # Step 1: Extract the research topic without mentioning predictions
            print("🎯 Extracting research topic from market question...")
            topic_result = self.topic_extractor(market_question=market.title)
            print(f"   📚 Topic: {topic_result.research_topic}")
            print(f"   🔍 Aspects: {topic_result.key_aspects}")
            
            # Step 2: Research the topic with Perplexity (without revealing it's for prediction markets)
            print("🔬 Researching topic with Perplexity (no prediction context)...")
            with dspy.context(lm=self.perplexity_lm):
                result = self.market_researcher(
                    research_topic=topic_result.research_topic,
                    key_aspects=topic_result.key_aspects,
                    category=market.category,
                    current_date=self.current_date.strftime('%B %d, %Y')
                )
            
            # Step 3: Compile comprehensive research
            research_output = f"""
📊 MARKET RESEARCH: {market.title}

🔄 CURRENT SITUATION (Last 48 hours):
{result.current_situation}

📈 KEY DATA POINTS:
{result.key_data_points}

📅 UPCOMING CATALYSTS:
{result.upcoming_catalysts}

⚖️ MARKET DYNAMICS:
{result.market_dynamics}

📝 SUMMARY:
{result.research_summary}
"""
            
            print("✅ DSPy research complete")
            return research_output
            
        except Exception as e:
            print(f"⚠️ DSPy research error: {e}")
            return f"Research failed for: {market.title}"
    
    def dspy_generate_analysis(self, market: Market, research: str, original_query: str = "") -> tuple[str, str, float, str]:
        """Use DSPy for structured analysis generation"""
        try:
            print("💡 Generating DSPy analysis with Fireworks...")
            
            result = self.market_analyzer(
                market_title=market.title,
                category=market.category,
                research_summary=research[:1500],
                current_date=self.current_date.strftime('%B %d, %Y')
            )
            
            # Clean and validate outputs
            analysis = result.analysis.strip()
            recommendation = result.recommendation.strip()
            
            # Ensure recommendation format
            if not recommendation.upper().startswith(('BUY', 'SELL', 'HOLD')):
                if 'bullish' in recommendation.lower() or 'positive' in recommendation.lower():
                    recommendation = f"BUY - {recommendation[:35]}"
                elif 'bearish' in recommendation.lower() or 'negative' in recommendation.lower():
                    recommendation = f"SELL - {recommendation[:34]}"
                else:
                    recommendation = f"HOLD - {recommendation[:34]}"
            
            # Validate confidence
            try:
                confidence = float(result.confidence)
                confidence = max(0.5, min(0.9, confidence))
            except:
                confidence = 0.6
            
            print("✅ DSPy analysis complete")
            return analysis, recommendation, confidence, "DSPy structured analysis"
            
        except Exception as e:
            print(f"⚠️ DSPy analysis error: {e}")
            # Fallback to market-specific defaults
            if 'bitcoin' in market.title.lower():
                analysis = "Crypto market showing institutional adoption trends with regulatory uncertainty"
                recommendation = "HOLD - mixed signals"
            elif 'ukraine' in market.title.lower() or 'russia' in market.title.lower():
                analysis = "Geopolitical situation remains complex with ongoing diplomatic efforts"
                recommendation = "HOLD - monitoring developments"
            else:
                analysis = "Market conditions show mixed indicators requiring careful analysis"
                recommendation = "HOLD - awaiting clarity"
            
            return analysis, recommendation, 0.6, "Fallback analysis"
    
    def generate_polymarket_url(self, market: Market) -> str:
        """Generate proper Polymarket URL using market slug"""
        if market.market_slug:
            return f"https://polymarket.com/event/{market.market_slug}"
        else:
            return f"https://polymarket.com/search?q={market.title.replace(' ', '%20')}"
    
    def analyze_query(self, query: str) -> Optional[DSPyAIGGResult]:
        """Run complete DSPy enhanced AIGG analysis"""
        print(f"\n{'='*80}")
        print(f"🚀 DSPY ENHANCED AIGG ANALYSIS: '{query}'")
        print(f"{'='*80}")
        
        # Step 1: Get top 10 relevant markets
        top_markets = self.get_top_markets(query, limit=10)
        if not top_markets:
            print("❌ No relevant markets found")
            return None
        
        # Step 2: DSPy selects best market
        selected_market = self.dspy_select_best_market(query, top_markets)
        if not selected_market:
            print("❌ No market selected")
            return None
        
        # Step 3: DSPy research the selected market
        research = self.dspy_research_market(selected_market, query)
        
        # Step 4: DSPy generate analysis and recommendation
        analysis, recommendation, confidence, reasoning = self.dspy_generate_analysis(selected_market, research, query)
        
        # Step 5: Generate proper Polymarket URL
        polymarket_url = self.generate_polymarket_url(selected_market)
        
        return DSPyAIGGResult(
            selected_market=selected_market,
            research_summary=research,
            analysis=analysis,
            recommendation=recommendation,
            confidence=confidence,
            polymarket_url=polymarket_url,
            reasoning=reasoning
        )
    
    def print_result(self, result: DSPyAIGGResult):
        """Print formatted DSPy enhanced result"""
        print(f"\n{'='*90}")
        print("🎯 DSPY ENHANCED AIGG ANALYSIS RESULT")
        print(f"{'='*90}")
        print(f"🏆 Selected Market: {result.selected_market.title}")
        print(f"📂 Category: {result.selected_market.category}")
        print(f"🎯 Relevance Score: {result.selected_market.relevance_score:.3f}")
        print(f"📅 End Date: {result.selected_market.end_date}")
        print(f"🔍 Research Summary:")
        print(f"   {result.research_summary[:300]}...")
        print(f"💡 Analysis: {result.analysis}")
        print(f"📈 Recommendation: {result.recommendation}")
        print(f"🧠 Confidence: {result.confidence:.1%}")
        print(f"🔗 Polymarket URL: {result.polymarket_url}")
        print(f"🎯 Method: {result.reasoning}")
        print(f"{'='*90}")

def test_dspy_enhanced_flow():
    """Test the DSPy enhanced flow"""
    flow = DSPyEnhancedAIGGFlow()
    
    test_queries = [
        "Bitcoin reaching $200k this year",
        "Russia Ukraine ceasefire before July",
        "Federal Reserve interest rate cut"
    ]
    
    for query in test_queries:
        print(f"\n{'🔄'*50}")
        print(f"TESTING: {query}")
        print(f"{'🔄'*50}")
        
        result = flow.analyze_query(query)
        if result:
            flow.print_result(result)
        else:
            print("❌ No result generated")
        
        print("\n⏱️ Next test in 3 seconds...")
        import time
        time.sleep(3)

if __name__ == "__main__":
    test_dspy_enhanced_flow() 