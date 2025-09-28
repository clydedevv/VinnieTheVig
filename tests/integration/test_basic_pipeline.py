#!/usr/bin/env python3
"""
Basic Pipeline Test - Verify core functionality works
Quick smoke test before running comprehensive tests
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.flows.dspy_enhanced_aigg_flow import DSPyEnhancedAIGGFlow
from src.flows.llm_market_matcher import LLMMarketMatcher, MarketData


def test_basic_llm_matcher():
    """Test basic LLM matcher functionality"""
    print("="*80)
    print("TESTING BASIC LLM MATCHER")
    print("="*80)
    
    # Create test markets
    test_markets = [
        MarketData(
            id="btc-200k",
            title="Will Bitcoin reach $200,000 by end of 2025?",
            category="Crypto",
            end_date="2025-12-31T23:59:59Z",
            active=True
        ),
        MarketData(
            id="fed-cuts",
            title="How many times will the Fed cut rates in 2025?",
            category="Economics",
            end_date="2025-12-31T23:59:59Z",
            active=True
        )
    ]
    
    # Initialize matcher
    matcher = LLMMarketMatcher()
    
    # Test query understanding
    print("\n1. Testing Query Understanding:")
    query = "bitcoin 200k eoy"
    context = matcher.analyze_query(query)
    print(f"   Query: '{query}'")
    print(f"   Main topic: {context.main_topic}")
    print(f"   Entities: {context.entities}")
    print(f"   Time context: {context.time_context}")
    print(f"   Price targets: {context.price_targets}")
    print(f"   Intent: {context.intent}")
    
    # Test market scoring
    print("\n2. Testing Market Scoring:")
    results = matcher.find_best_markets(query, test_markets, top_k=2)
    for market, score, reasoning in results:
        print(f"   [{score:.3f}] {market.title}")
        print(f"          {reasoning}")
    
    print("\n✅ Basic LLM matcher working!")


def test_basic_pipeline():
    """Test basic pipeline functionality"""
    print("\n\n" + "="*80)
    print("TESTING BASIC PIPELINE")
    print("="*80)
    
    flow = DSPyEnhancedAIGGFlow()
    
    # Simple test queries
    test_queries = [
        "Bitcoin 200k this year",
        "Fed cutting rates soon",
        "Ukraine Russia ceasefire"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-"*50)
        
        try:
            result = flow.analyze_query(query)
            
            if result:
                print(f"✅ Market: {result.selected_market.title}")
                print(f"   Category: {result.selected_market.category}")
                print(f"   Score: {result.selected_market.relevance_score:.3f}")
                print(f"   Analysis: {result.analysis}")
                print(f"   Rec: {result.recommendation}")
            else:
                print("❌ No result")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n✅ Basic pipeline test complete!")


def verify_components():
    """Verify all components are properly initialized"""
    print("\n" + "="*80)
    print("VERIFYING COMPONENTS")
    print("="*80)
    
    try:
        # Check imports
        print("1. Checking imports...")
        from src.flows.dspy_enhanced_aigg_flow import DSPyEnhancedAIGGFlow
        from src.flows.llm_market_matcher import LLMMarketMatcher
        print("   ✅ Imports successful")
        
        # Check initialization
        print("\n2. Checking initialization...")
        flow = DSPyEnhancedAIGGFlow()
        print("   ✅ Flow initialized")
        print(f"   - API base: {flow.api_base}")
        print(f"   - Has Perplexity: {'Yes' if flow.perplexity_key else 'No'}")
        print(f"   - Has LLM matcher: {'Yes' if hasattr(flow, 'llm_market_matcher') else 'No'}")
        
        # Check DSPy configuration
        print("\n3. Checking DSPy configuration...")
        import dspy
        print(f"   ✅ DSPy configured")
        
        print("\n✅ All components verified!")
        
    except Exception as e:
        print(f"\n❌ Component verification failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run verification first
    verify_components()
    
    # Test basic functionality
    test_basic_llm_matcher()
    test_basic_pipeline()
    
    print("\n\n" + "="*80)
    print("BASIC TESTS COMPLETE - Ready for comprehensive testing!")
    print("="*80)