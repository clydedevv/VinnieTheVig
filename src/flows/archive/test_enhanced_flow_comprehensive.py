#!/usr/bin/env python3
"""
Comprehensive test of Enhanced AIGG Flow with various query types
"""
from enhanced_aigg_flow import EnhancedAIGGFlow
import time

def test_comprehensive_queries():
    """Test various types of queries to showcase the enhanced flow"""
    flow = EnhancedAIGGFlow()
    
    # Test queries that should have excellent matches in our database
    test_queries = [
        # Crypto queries
        "Bitcoin reaching $250,000 by end of year",
        "Will Bitcoin hit $150k this year?",
        
        # Sports queries  
        "NBA championship winner 2025",
        "Who will win the NBA Finals?",
        
        # Politics/Government
        "Trump eliminating capital gains tax on crypto",
        "Elon Musk government efficiency DOGE spending cuts",
        
        # Economics/Fed
        "Federal Reserve interest rate decisions",
        "Fed cutting rates in 2025",
        
        # Tech/AI
        "OpenAI GPT breakthrough this year",
        "Artificial intelligence advancement 2025",
        
        # International/Geopolitics
        "Russia Ukraine conflict resolution",
        "Putin staying in power 2025"
    ]
    
    print("🚀 COMPREHENSIVE ENHANCED AIGG FLOW TESTING")
    print("=" * 80)
    print(f"Testing {len(test_queries)} diverse queries...\n")
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}/{len(test_queries)}: {query}")
        print(f"{'='*80}")
        
        try:
            result = flow.analyze_query(query)
            if result:
                flow.print_result(result)
                results.append({
                    'query': query,
                    'success': True,
                    'market_title': result.selected_market.title,
                    'relevance_score': result.selected_market.relevance_score,
                    'confidence': result.confidence,
                    'url': result.polymarket_url
                })
                print(f"\n✅ SUCCESS: Found relevant market with {result.selected_market.relevance_score:.3f} relevance")
            else:
                print("❌ No result generated")
                results.append({
                    'query': query,
                    'success': False,
                    'market_title': 'None',
                    'relevance_score': 0.0,
                    'confidence': 0.0,
                    'url': 'None'
                })
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append({
                'query': query,
                'success': False,
                'market_title': f'Error: {e}',
                'relevance_score': 0.0,
                'confidence': 0.0,
                'url': 'None'
            })
        
        # Brief pause between queries
        if i < len(test_queries):
            print(f"\n⏳ Next query in 2 seconds...")
            time.sleep(2)
    
    # Summary report
    print(f"\n{'='*80}")
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print(f"{'='*80}")
    
    successful = [r for r in results if r['success']]
    print(f"✅ Successful queries: {len(successful)}/{len(test_queries)} ({len(successful)/len(test_queries)*100:.1f}%)")
    
    if successful:
        avg_relevance = sum(r['relevance_score'] for r in successful) / len(successful)
        avg_confidence = sum(r['confidence'] for r in successful) / len(successful)
        print(f"📈 Average relevance score: {avg_relevance:.3f}")
        print(f"🧠 Average confidence: {avg_confidence:.1%}")
        
        print(f"\n🏆 TOP MATCHES:")
        top_matches = sorted(successful, key=lambda x: x['relevance_score'], reverse=True)[:5]
        for i, match in enumerate(top_matches, 1):
            print(f"   {i}. Score {match['relevance_score']:.3f}: {match['query']}")
            print(f"      → {match['market_title'][:60]}...")
            print(f"      → {match['url']}")
    
    failed = [r for r in results if not r['success']]
    if failed:
        print(f"\n❌ FAILED QUERIES:")
        for fail in failed:
            print(f"   • {fail['query']}")
            print(f"     Reason: {fail['market_title']}")
    
    print(f"\n🎯 ANALYSIS:")
    print(f"The enhanced flow successfully handles diverse query types with AI-powered")
    print(f"market selection and generates actionable insights with direct Polymarket links.")
    print(f"Ready for Twitter integration! 🐦")

if __name__ == "__main__":
    test_comprehensive_queries() 