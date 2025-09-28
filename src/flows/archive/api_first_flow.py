#!/usr/bin/env python3
"""
API-First AIGG Flow - Uses existing market API with sophisticated search
Main flow: query -> search API for relevant markets -> research -> analysis -> recommendation
"""
import os
import json
import requests
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

@dataclass
class Market:
    """Market data structure matching API response"""
    id: str
    title: str
    description: str = ""
    category: str = ""
    active: bool = True
    end_date: Optional[str] = None
    relevance_score: float = 0.0

@dataclass
class ResearchResult:
    """Research analysis result"""
    topic: str
    summary: str
    key_points: List[str]
    confidence: float
    sources: List[str] = None
    web_research: str = ""

@dataclass
class Recommendation:
    """Final betting recommendation"""
    market: Market
    research: ResearchResult
    recommendation: str  # "yes", "no", "pass"
    confidence: float
    reasoning: str
    bet_size: str  # "small", "medium", "large", "none"

class APIMarketService:
    """Service that uses the existing market API for production"""
    
    def __init__(self):
        self.api_base = "http://37.27.54.184:8001"
        self.current_date = datetime.now(timezone.utc)
        print(f"🗓️ Current date: {self.current_date.strftime('%Y-%m-%d %H:%M UTC')} (June 2025)")
        print(f"🌐 Using market API: {self.api_base}")
    
    def search_markets(self, query: str, limit: int = 10) -> List[Market]:
        """Search markets using the sophisticated API search"""
        try:
            url = f"{self.api_base}/markets/search"
            params = {
                "q": query,
                "limit": limit
            }
            
            print(f"🔍 Searching API for: '{query}'")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            markets_data = data.get('markets', [])
            
            if not markets_data:
                print("⚠️ No markets found via API search")
                return []
            
            markets = []
            for market_data in markets_data:
                market = Market(
                    id=str(market_data.get('id', '')),
                    title=market_data.get('title', ''),
                    description=market_data.get('description', ''),
                    category=market_data.get('category', ''),
                    active=market_data.get('active', True),
                    end_date=market_data.get('end_date'),
                    relevance_score=float(market_data.get('relevance_score', 0.0))
                )
                markets.append(market)
            
            print(f"📊 Found {len(markets)} relevant markets via API")
            return markets
            
        except Exception as e:
            print(f"❌ API search failed: {e}")
            return []
    
    def get_best_market(self, query: str) -> Optional[Market]:
        """Get the best matching market using API search with relevance scoring"""
        markets = self.search_markets(query, limit=10)
        
        if not markets:
            return None
        
        # The API already ranks by relevance, so take the top result
        best_market = markets[0]
        print(f"🎯 Best match (score: {best_market.relevance_score:.3f}): {best_market.title}")
        
        # Show other good matches for context
        if len(markets) > 1:
            print("📋 Other relevant matches:")
            for market in markets[1:4]:  # Show top 3 alternatives
                print(f"   • {market.relevance_score:.3f}: {market.title[:80]}...")
        
        return best_market

class PerplexityResearcher:
    """Research using Perplexity API with context awareness"""
    
    def __init__(self):
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.current_date = datetime.now(timezone.utc)
    
    def _make_perplexity_request(self, messages: List[Dict], model: str = "sonar") -> str:
        """Make a request to Perplexity API"""
        if not self.perplexity_key:
            raise ValueError("PERPLEXITY_API_KEY not found")
        
        headers = {
            "Authorization": f"Bearer {self.perplexity_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.3
        }
        
        response = requests.post(self.base_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
    
    def research_topic(self, market: Market) -> ResearchResult:
        """Conduct time-aware comprehensive research"""
        if not self.perplexity_key:
            return ResearchResult(
                topic=market.title,
                summary="No Perplexity API key available for research",
                key_points=["API key missing"],
                confidence=0.0
            )
        
        try:
            # Create context-aware research prompt
            time_context = f"Current date: {self.current_date.strftime('%B %d, %Y')} (June 2025)"
            if market.end_date:
                time_context += f". Market end date: {market.end_date}"
            
            print("  🌐 Searching web with Perplexity Sonar...")
            web_messages = [
                {
                    "role": "system",
                    "content": f"""You are a research assistant for prediction markets. {time_context}
                    Search for the most recent, relevant information about the given market question.
                    Focus on current developments, recent news, and factors that could influence the outcome.
                    Consider the timeline - if this is a time-sensitive question, prioritize recent events."""
                },
                {
                    "role": "user", 
                    "content": f"Research this prediction market question: {market.title}\n\nCategory: {market.category}\nDescription: {market.description}\n\nProvide comprehensive, up-to-date information that would help predict the outcome."
                }
            ]
            
            web_research = self._make_perplexity_request(web_messages, model="sonar")
            
            print("  🧠 Analyzing with Perplexity reasoning model...")
            analysis_messages = [
                {
                    "role": "system",
                    "content": f"""You are an expert prediction market analyst. {time_context}
                    
                    Analyze the research and provide:
                    1. Current situation summary (2-3 sentences)
                    2. Key factors that could influence the outcome
                    3. Supporting evidence
                    4. Risks/opposing factors
                    5. Confidence assessment (0.0 to 1.0) based on:
                       - Quality of available information
                       - Predictability of the outcome
                       - Time horizon considerations
                    
                    Be objective and consider multiple scenarios."""
                },
                {
                    "role": "user",
                    "content": f"Market: {market.title}\nCategory: {market.category}\nEnd Date: {market.end_date}\n\nResearch:\n{web_research}\n\nProvide structured analysis:"
                }
            ]
            
            analysis = self._make_perplexity_request(analysis_messages, model="r1-1776")
            
            # Parse analysis
            lines = analysis.split('\n')
            summary_lines = []
            key_points = []
            confidence = 0.6  # Default
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Extract confidence score
                if "confidence" in line.lower():
                    confidence_match = re.search(r'(\d*\.?\d+)', line)
                    if confidence_match:
                        try:
                            confidence = float(confidence_match.group(1))
                            if confidence > 1.0:
                                confidence = confidence / 100.0
                        except:
                            pass
                
                # Collect key points
                if line.startswith(('1.', '2.', '3.', '4.', '5.', '-', '•', '*')):
                    key_points.append(line)
                elif len(summary_lines) < 3:
                    summary_lines.append(line)
            
            summary = ' '.join(summary_lines)[:400]
            
            return ResearchResult(
                topic=market.title,
                summary=summary,
                key_points=key_points[:5],
                confidence=max(0.0, min(1.0, confidence)),  # Clamp to valid range
                sources=["Perplexity Sonar", "Perplexity R1-1776"],
                web_research=web_research
            )
            
        except Exception as e:
            print(f"Research error: {e}")
            return ResearchResult(
                topic=market.title,
                summary=f"Research failed: {str(e)}",
                key_points=["Research unavailable"],
                confidence=0.0
            )

class APIFirstAnalyzer:
    """Enhanced analyzer using Perplexity for recommendations"""
    
    def __init__(self):
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        self.base_url = "https://api.perplexity.ai/chat/completions"
    
    def analyze_and_recommend(self, market: Market, research: ResearchResult) -> Recommendation:
        """Generate AI-powered recommendation"""
        
        if self.perplexity_key:
            try:
                print("  🤖 Generating recommendation with Perplexity...")
                
                headers = {
                    "Authorization": f"Bearer {self.perplexity_key}",
                    "Content-Type": "application/json"
                }
                
                messages = [
                    {
                        "role": "system",
                        "content": """You are an expert prediction market trader. Given market data and research, provide a clear betting recommendation.

                        Consider:
                        - Research quality and confidence
                        - Market timing and category
                        - Risk-reward ratio
                        - Information edge potential

                        Output format: DECISION|SIZE|CONFIDENCE|REASON
                        Where:
                        - DECISION: yes/no/pass
                        - SIZE: small/medium/large/none
                        - CONFIDENCE: 0.0-1.0
                        - REASON: brief explanation (1-2 sentences)"""
                    },
                    {
                        "role": "user",
                        "content": f"""Market: {market.title}
Category: {market.category}
Market relevance score: {market.relevance_score}
End date: {market.end_date}

Research summary: {research.summary}
Research confidence: {research.confidence}
Key factors: {'; '.join(research.key_points[:3])}

Recommendation:"""
                    }
                ]
                
                payload = {
                    "model": "r1-1776",
                    "messages": messages,
                    "max_tokens": 300,
                    "temperature": 0.2
                }
                
                response = requests.post(self.base_url, json=payload, headers=headers, timeout=20)
                response.raise_for_status()
                
                ai_response = response.json()["choices"][0]["message"]["content"]
                
                # Parse AI response
                parts = ai_response.split('|')
                if len(parts) >= 4:
                    decision = parts[0].strip().lower()
                    bet_size = parts[1].strip().lower()
                    try:
                        confidence = float(parts[2].strip())
                    except:
                        confidence = research.confidence
                    reasoning = parts[3].strip()
                    
                    return Recommendation(
                        market=market,
                        research=research,
                        recommendation=decision,
                        confidence=confidence,
                        reasoning=reasoning,
                        bet_size=bet_size
                    )
                        
            except Exception as e:
                print(f"  ⚠️ AI recommendation failed: {e}")
        
        # Fallback logic
        confidence = research.confidence
        
        if confidence < 0.4:
            decision = "pass"
            bet_size = "none"
            reasoning = "Research confidence too low for betting"
        elif confidence > 0.8:
            decision = "yes"
            bet_size = "medium"
            reasoning = "High-confidence research supports positive outcome"
        elif confidence > 0.6:
            decision = "yes"
            bet_size = "small"
            reasoning = "Moderate confidence supports cautious position"
        else:
            decision = "pass"
            bet_size = "none"
            reasoning = "Inconclusive research"
        
        return Recommendation(
            market=market,
            research=research,
            recommendation=decision,
            confidence=confidence,
            reasoning=reasoning,
            bet_size=bet_size
        )

class APIFirstFlow:
    """Production-ready flow using existing market API"""
    
    def __init__(self):
        self.market_service = APIMarketService()
        self.researcher = PerplexityResearcher()
        self.analyzer = APIFirstAnalyzer()
    
    def analyze_query(self, query: str) -> Optional[Recommendation]:
        """Run complete analysis using API-first approach"""
        print(f"🔍 Analyzing: '{query}'")
        print("="*60)
        
        # Step 1: Search for relevant markets using sophisticated API
        print("🌐 Searching market API...")
        relevant_market = self.market_service.get_best_market(query)
        if not relevant_market:
            print("❌ No relevant market found via API")
            return None
        
        # Step 2: Conduct research
        print("🔬 Conducting research...")
        research = self.researcher.research_topic(relevant_market)
        
        # Step 3: Generate recommendation
        print("💡 Generating recommendation...")
        recommendation = self.analyzer.analyze_and_recommend(relevant_market, research)
        
        return recommendation
    
    def print_result(self, rec: Recommendation):
        """Print formatted result"""
        print("\n" + "="*70)
        print("🎯 API-FIRST AIGG ANALYSIS RESULT")
        print("="*70)
        print(f"🏆 Market: {rec.market.title}")
        print(f"📂 Category: {rec.market.category}")
        print(f"🎯 Relevance Score: {rec.market.relevance_score:.3f}")
        print(f"📅 End Date: {rec.market.end_date}")
        print(f"🔍 Research Summary: {rec.research.summary[:200]}...")
        print(f"📊 Key Insights:")
        for point in rec.research.key_points[:3]:
            print(f"   • {point}")
        print(f"🎲 Recommendation: {rec.recommendation.upper()}")
        print(f"💵 Bet Size: {rec.bet_size.upper()}")
        print(f"🧠 Confidence: {rec.confidence:.1%}")
        print(f"💭 Reasoning: {rec.reasoning}")
        print("="*70)

def test_api_health():
    """Test API connectivity"""
    try:
        response = requests.get("http://37.27.54.184:8001/health", timeout=5)
        print(f"✅ API Health: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ API Health Check Failed: {e}")
        return False

def test_queries():
    """Test with the provided queries"""
    # Check API health first
    if not test_api_health():
        print("Cannot proceed without API access")
        return
    
    flow = APIFirstFlow()
    
    test_queries = [
        "Which cabinet member will trump fire first?",
        "Will russia bomb Germany", 
        "who will win 2025 nba finals",
        "best AI model by end of the month"
    ]
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"TESTING QUERY: {query}")
        print(f"{'='*80}")
        
        result = flow.analyze_query(query)
        if result:
            flow.print_result(result)
        else:
            print("❌ No result generated")
        
        print("\n" + "🔄 Next query in 3 seconds...")
        import time
        time.sleep(3)

if __name__ == "__main__":
    test_queries() 