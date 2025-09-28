"""
DSPy Enhanced AIGG Flow - Clean architecture with no hallucination risk
Uses DSPy framework for structured AI analysis of prediction markets
"""
import os
import sys
import requests
from datetime import datetime, timezone
from typing import List, Optional
from enum import Enum
import dspy
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.utils.dspy_utilities import lm as fireworks_lm

load_dotenv()

# Pydantic Models with proper validation
class Recommendation(str, Enum):
    """Valid recommendation types"""
    BUY_YES = "BUY_YES"
    BUY_NO = "BUY_NO"
    HOLD = "HOLD"

class MarketRecord(BaseModel):
    """Validated market record from database"""
    market_id: str
    title: str
    category: str
    market_slug: str = ""
    active: bool = True
    end_date: Optional[datetime] = None
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    yes_price: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    no_price: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    
    class Config:
        frozen = True  # Immutable after creation

# Clean DSPy Signatures - no hallucination possible
class OptimizeSearchQuery(dspy.Signature):
    """Optimize user query for better market search"""
    query: str = dspy.InputField(description="User's original query")
    
    search_keywords: str = dspy.OutputField(description="3-5 key search terms (not sentences)")

class SelectMarketFromList(dspy.Signature):
    """Select most relevant market from validated options only"""
    query: str = dspy.InputField(description="User's query")
    market_ids: str = dspy.InputField(description="Comma-separated list of market IDs")
    market_titles: str = dspy.InputField(description="Numbered list of market titles")
    
    selected_id: str = dspy.OutputField(description="The exact market ID from the provided list")
    confidence: float = dspy.OutputField(description="Confidence 0.0-1.0")
    reasoning: str = dspy.OutputField(description="Brief reasoning for selection")

class ExtractResearchTopic(dspy.Signature):
    """Extract the core topic to research from a prediction market question"""
    market_question: str = dspy.InputField(description="The prediction market question")
    
    research_topic: str = dspy.OutputField(description="Core topic to research WITHOUT mentioning predictions")
    key_aspects: str = dspy.OutputField(description="Specific aspects to investigate")

class ResearchMarket(dspy.Signature):
    """Research a topic comprehensively without revealing it's for prediction markets"""
    research_topic: str = dspy.InputField(description="Topic to research (NOT phrased as a prediction)")
    key_aspects: str = dspy.InputField(description="Specific aspects to investigate")
    category: str = dspy.InputField(description="General category")
    current_date: str = dspy.InputField(description="Current date for temporal context")
    
    current_situation: str = dspy.OutputField(description="What's happening RIGHT NOW with this topic? Latest developments from past 48 hours")
    key_data_points: str = dspy.OutputField(description="Specific numbers, statistics, expert opinions, polls, or measurable indicators")
    upcoming_catalysts: str = dspy.OutputField(description="Scheduled events or known future developments that could impact this topic")
    market_dynamics: str = dspy.OutputField(description="Supply/demand factors, sentiment indicators, or market-specific mechanics")
    research_summary: str = dspy.OutputField(description="Executive summary connecting all findings")

class AnalyzeMarket(dspy.Signature):
    """Generate final trading analysis and recommendation
    
    Examples of Vinnie's voice for short_analysis:
    - High confidence: "Trust me on this one - sharp money's moving heavy on the yes side. My cousin's cousin knows a guy, capisce?"
    - Medium confidence: "Something's cooking here, the vig's telling a story. Numbers don't lie, kid - decent value play"
    - Low confidence: "Fuggedaboutit for now - too murky for my taste. Even my nonna's confused on this action"
    - Sports: "The line's screaming value - smart money's all over the under. That's the word from Brooklyn"
    - Crypto: "Bitcoin at 200k? The wise ones are talking, but watch the juice - whales playing games here"
    
    IMPORTANT: If KEY RECENT NEWS is mentioned in research_summary, Vinnie should reference it naturally:
    - "Word is [recent development]. Smart money's already moving on this."
    - "Just heard [news]. The line's gonna shift, get in now."
    - "With [recent event], the juice is obvious - take the [position]."
    """
    market_title: str = dspy.InputField(description="Market question")
    category: str = dspy.InputField(description="Market category")
    research_summary: str = dspy.InputField(description="Research findings including KEY RECENT NEWS")
    current_date: str = dspy.InputField(description="Current date")
    
    analysis: str = dspy.OutputField(description="Clear, actionable analysis (max 280 chars)")
    recommendation: str = dspy.OutputField(description="BUY_YES, BUY_NO, or HOLD")
    confidence: float = dspy.OutputField(description="Confidence level 0.0-1.0")
    short_analysis: str = dspy.OutputField(description="Twitter-ready analysis as Vinnie 'The Vig' Lombardi - a Brooklyn bookmaker. If research mentions KEY RECENT NEWS, reference it naturally. Use betting slang: 'the vig', 'smart money', 'action', 'the line', 'juice'. Write 200-250 chars MAX, end with complete sentence!")

class AnalysisResult(BaseModel):
    """Validated analysis result"""
    selected_market: MarketRecord
    research_summary: str
    analysis: str = Field(max_length=280)
    recommendation: Recommendation
    confidence: float = Field(ge=0.0, le=1.0)
    short_analysis: str = Field(max_length=280)  # Twitter Premium allows longer
    polymarket_url: str
    
    class Config:
        frozen = True

class DSPyEnhancedAIGGFlow:
    """Clean DSPy flow with strict validation and no hallucination risk"""
    
    def __init__(self):
        self.api_base = os.getenv("MARKET_API_URL", "http://localhost:8001")
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        self.current_date = datetime.now(timezone.utc)
        
        # Configure DSPy with Fireworks
        dspy.configure(lm=fireworks_lm)
        
        # Initialize Perplexity for research
        self.perplexity_lm = None
        if self.perplexity_key:
            self.perplexity_lm = dspy.LM(
                model="perplexity/sonar",
                api_key=self.perplexity_key,
                api_base="https://api.perplexity.ai"
            )
        
        # Initialize DSPy modules with clean signatures
        self.query_optimizer = dspy.Predict(OptimizeSearchQuery)
        self.market_selector = dspy.Predict(SelectMarketFromList)
        self.market_analyzer = dspy.Predict(AnalyzeMarket)
        self.topic_extractor = dspy.ChainOfThought(ExtractResearchTopic)
        
        # Market researcher with Perplexity
        if self.perplexity_lm:
            with dspy.context(lm=self.perplexity_lm):
                self.market_researcher = dspy.ChainOfThought(ResearchMarket)
        else:
            self.market_researcher = dspy.ChainOfThought(ResearchMarket)
        
        print(f"🚀 Clean DSPy Flow initialized")
        print(f"🌐 Market API: {self.api_base}")
        print(f"🧠 Inference: Fireworks AI")
        print(f"🔍 Search: Perplexity {'✅' if self.perplexity_lm else '❌'}")
    
    def search_markets(self, query: str, limit: int = 10) -> List[MarketRecord]:
        """Search for real markets from database API - no LLM generation"""
        try:
            # Special handling for U.S. Open queries to avoid political market confusion
            query_lower = query.lower()
            if ("u.s. open" in query_lower or "us open" in query_lower) and any(
                name in query_lower for name in ["alcaraz", "tennis", "sinner", "djokovic", "medvedev"]
            ):
                # Force tennis context for U.S. Open tennis queries
                search_terms = query.replace("U.S.", "US").replace("u.s.", "us")
                print(f"🔍 Searching: '{query}'")
                print(f"   🎾 Tennis context detected - using: '{search_terms}'")
            else:
                # Optimize query for better search
                optimized = self.query_optimizer(query=query)
                search_terms = optimized.search_keywords.strip()
                
                print(f"🔍 Searching: '{query}'")
                if search_terms != query:
                    print(f"   🎯 Optimized: '{search_terms}'")
            
            # Direct API search - only real markets
            search_url = f"{self.api_base}/markets/search"
            # Always use LLM for better matching on names/entities
            # Only skip LLM for very generic single words like "bitcoin" or "trump"
            generic_keywords = ["bitcoin", "trump", "fed", "rate", "election"]
            use_llm = not (len(search_terms.split()) == 1 and search_terms.lower() in generic_keywords)
            timeout = 30 if use_llm else 10
            params = {"q": search_terms, "limit": limit * 3, "use_llm": use_llm}
            response = requests.get(search_url, params=params, timeout=timeout)
            response.raise_for_status()
            
            data = response.json()
            markets_data = data.get('markets', [])
            
            # Convert to validated Pydantic models
            markets = []
            for market_data in markets_data[:limit]:
                try:
                    market = MarketRecord(
                        market_id=market_data.get('market_id', market_data.get('id')),
                        title=market_data.get('title', ''),
                        category=market_data.get('category', 'Unknown'),
                        market_slug=market_data.get('market_slug', ''),
                        active=market_data.get('active', True),
                        end_date=market_data.get('end_date'),
                        relevance_score=market_data.get('relevance_score', 0.0),
                        yes_price=market_data.get('yes_price'),
                        no_price=market_data.get('no_price')
                    )
                    markets.append(market)
                except Exception as e:
                    print(f"   ⚠️ Skipping invalid market: {e}")
                    continue
            
            print(f"   📊 Found {len(markets)} valid markets")
            return markets
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def select_best_market(self, query: str, markets: List[MarketRecord]) -> Optional[MarketRecord]:
        """Select from real markets only - no hallucination possible"""
        if not markets:
            return None
            
        if len(markets) == 1:
            # Still check confidence even for single market
            try:
                result = self.market_selector(
                    query=query,
                    market_ids=markets[0].market_id,
                    market_titles=f"1. {markets[0].title}"
                )
                confidence = min(1.0, max(0.0, float(result.confidence)))
                if confidence < 0.3:
                    print(f"❌ Single market confidence too low: {confidence:.1%}")
                    print(f"   📝 Reasoning: {result.reasoning}")
                    return None
                return markets[0]
            except:
                return markets[0]  # Fallback if selection fails
        
        try:
            print("🤖 Selecting best market from database results...")
            
            # Prepare validated inputs
            market_ids = ",".join([m.market_id for m in markets[:10]])
            market_titles = "\n".join([f"{i}. {m.title}" for i, m in enumerate(markets[:10], 1)])
            
            # LLM can only select from provided IDs
            result = self.market_selector(
                query=query,
                market_ids=market_ids,
                market_titles=market_titles
            )
            
            # Check confidence threshold FIRST
            confidence = min(1.0, max(0.0, float(result.confidence)))
            if confidence < 0.3:
                print(f"❌ Market selection confidence too low: {confidence:.1%}")
                print(f"   📝 Reasoning: {result.reasoning}")
                print(f"   🚫 No relevant markets for query: '{query}'")
                return None
            
            # Validate selection is from input list
            selected_id = result.selected_id.strip()
            for market in markets:
                if market.market_id == selected_id:
                    print(f"🎯 Selected: {market.title}")
                    print(f"   📊 Confidence: {confidence:.1%}")
                    print(f"   📝 Reasoning: {result.reasoning}")
                    return market
            
            # If LLM returned invalid ID but confidence was high, use first market
            print("⚠️ LLM returned invalid market ID, using top result")
            return markets[0]
            
        except Exception as e:
            print(f"⚠️ Selection error: {e}, using top market")
            return markets[0]
    
    def research_market(self, market: MarketRecord) -> str:
        """Research market topic WITHOUT revealing it's for predictions"""
        if not self.perplexity_lm:
            return f"Research unavailable (No Perplexity key)"
        
        try:
            # Extract research topic
            print("🎯 Extracting research topic...")
            topic_result = self.topic_extractor(market_question=market.title)
            print(f"   📚 Topic: {topic_result.research_topic}")
            print(f"   🔍 Aspects: {topic_result.key_aspects}")
            
            # Research with Perplexity
            print("🔬 Researching topic...")
            with dspy.context(lm=self.perplexity_lm):
                result = self.market_researcher(
                    research_topic=topic_result.research_topic,
                    key_aspects=topic_result.key_aspects,
                    category=market.category,
                    current_date=self.current_date.strftime('%B %d, %Y')
                )
            
            # Format research
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
            
            print("✅ Research complete")
            return research_output
            
        except Exception as e:
            print(f"⚠️ Research error: {e}")
            return f"Research failed: {e}"
    
    def generate_analysis(self, market: MarketRecord, research: str) -> tuple[str, Recommendation, float, str]:
        """Generate final analysis and recommendation"""
        try:
            print("💡 Generating analysis...")
            
            # Extract key recent developments from research if available
            recent_news = ""
            if "CURRENT SITUATION" in research and "Last 48 hours" in research:
                # Extract the current situation section
                start = research.find("CURRENT SITUATION")
                end = research.find("KEY DATA POINTS") if "KEY DATA POINTS" in research else len(research)
                current_section = research[start:end]
                
                # Get first significant fact
                lines = current_section.split('\n')
                for line in lines:
                    if len(line) > 50 and not line.startswith('🔄'):
                        recent_news = line.strip()[:150]
                        break
            
            # Pass recent news to analyzer for Vinnie to reference
            enhanced_research = f"{research}\n\nKEY RECENT NEWS TO MENTION: {recent_news}" if recent_news else research
            
            result = self.market_analyzer(
                market_title=market.title,
                category=market.category,
                research_summary=enhanced_research,
                current_date=self.current_date.strftime('%B %d, %Y')
            )
            
            # Extract and validate
            analysis = result.analysis[:280]
            try:
                recommendation = Recommendation(result.recommendation)
            except ValueError:
                recommendation = Recommendation.HOLD
            confidence = max(0.0, min(1.0, float(result.confidence)))
            # Ensure complete sentences - find last sentence ending
            short_analysis = result.short_analysis[:280]
            if short_analysis and short_analysis[-1] not in '.!?':
                # Find last complete sentence
                for end_char in ['.', '!', '?']:
                    last_end = short_analysis.rfind(end_char)
                    if last_end > 0:
                        short_analysis = short_analysis[:last_end + 1]
                        break
            
            print("✅ Analysis complete")
            return analysis, recommendation, confidence, short_analysis
            
        except Exception as e:
            print(f"⚠️ Analysis error: {e}")
            return "Analysis unavailable", Recommendation.HOLD, 0.5, "Error generating analysis"
    
    def get_polymarket_url(self, market: MarketRecord) -> str:
        """Generate Polymarket URL with corrections"""
        from src.utils.polymarket_url_fixer import get_polymarket_url
        
        # Use the URL fixer to get correct URL
        url = get_polymarket_url(
            market_slug=market.market_slug,
            market_title=market.title,
            market_id=market.market_id
        )
        
        print(f"   🔗 URL: {url}")
        return url
    
    def analyze_query(self, query: str) -> Optional[AnalysisResult]:
        """Run complete analysis pipeline"""
        print(f"\n{'='*80}")
        print(f"🚀 DSPY ENHANCED AIGG ANALYSIS: '{query}'")
        print(f"{'='*80}")
        
        
        # Step 1: Search for real markets
        top_markets = self.search_markets(query, limit=10)
        if not top_markets:
            print("❌ No relevant markets found")
            return None
        
        print(f"📊 Found {len(top_markets)} relevant markets")
        
        # Step 2: Select best market
        selected_market = self.select_best_market(query, top_markets)
        if not selected_market:
            print("❌ No sufficiently relevant market found for query")
            return None
        
        # Step 3: Research the market
        research = self.research_market(selected_market)
        
        # Step 4: Generate analysis
        analysis, recommendation, confidence, short_analysis = self.generate_analysis(
            selected_market, research
        )
        
        # Step 5: Get Polymarket URL
        polymarket_url = self.get_polymarket_url(selected_market)
        
        # Create validated result
        result = AnalysisResult(
            selected_market=selected_market,
            research_summary=research,
            analysis=analysis,
            recommendation=recommendation,
            confidence=confidence,
            short_analysis=short_analysis,
            polymarket_url=polymarket_url
        )
        
        print(f"\n{'='*80}")
        print(f"✅ ANALYSIS COMPLETE")
        print(f"📊 Market: {selected_market.title}")
        print(f"💡 Recommendation: {recommendation} (Confidence: {confidence:.1%})")
        print(f"🐦 Tweet: {short_analysis}")
        print(f"🔗 {polymarket_url}")
        print(f"{'='*80}\n")
        
        return result
    
    def print_result(self, result: AnalysisResult) -> None:
        """Print analysis result in formatted output"""
        print(f"\n{'='*80}")
        print(f"📊 MARKET: {result.selected_market.title}")
        print(f"📂 Category: {result.selected_market.category}")
        print(f"\n💡 RECOMMENDATION: {result.recommendation.value}")
        print(f"📈 Confidence: {result.confidence:.1%}")
        print(f"\n📝 ANALYSIS:")
        print(result.analysis)
        print(f"\n🐦 TWEET:")
        print(result.short_analysis)
        print(f"\n🔗 POLYMARKET:")
        print(result.polymarket_url)
        print(f"{'='*80}\n")