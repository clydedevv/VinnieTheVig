#!/usr/bin/env python3
"""
Simple test script to check what's working in the AIGG repo
"""
import os
import sys
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

def test_environment_variables() -> Dict[str, Any]:
    """Test if required environment variables are set"""
    results = {}
    required_vars = [
        "OPENAI_API_KEY",
        "PERPLEXITY_API_KEY",
        "DATABASE_URL"
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        results[var] = {
            "exists": bool(value),
            "value": value[:10] + "..." if value else None
        }
    
    return results

def test_imports() -> Dict[str, Any]:
    """Test if key modules can be imported"""
    results = {}
    
    # Test standard libraries
    try:
        import requests
        results["requests"] = "✅ Available"
    except ImportError:
        results["requests"] = "❌ Missing"
    
    try:
        import psycopg2
        results["psycopg2"] = "✅ Available"
    except ImportError:
        results["psycopg2"] = "❌ Missing"
    
    try:
        import fastapi
        results["fastapi"] = "✅ Available"
    except ImportError:
        results["fastapi"] = "❌ Missing"
    
    try:
        import openai
        results["openai"] = "✅ Available"
    except ImportError:
        results["openai"] = "❌ Missing"
    
    # Test custom modules
    try:
        from agno.agent import Agent
        results["agno"] = "✅ Available"
    except ImportError:
        results["agno"] = "❌ Missing"
    
    return results

def test_polymarket_api() -> Dict[str, Any]:
    """Test if we can reach the Polymarket API"""
    try:
        import requests
        url = "https://clob.polymarket.com/markets"
        params = {"limit": 1}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'data' in data:
                sample_question = data['data'][0].get('question', 'No question') if data['data'] else 'No markets'
            else:
                sample_question = "Data structure changed"
                
            return {
                "status": f"✅ API reachable (status: {response.status_code})",
                "sample_market": sample_question
            }
        else:
            return {"status": f"❌ HTTP {response.status_code}"}
    except Exception as e:
        return {"status": f"❌ API failed: {str(e)}"}

def test_perplexity_api() -> Dict[str, Any]:
    """Test if we can reach the Perplexity API"""
    try:
        import requests
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            return {"status": "❌ No Perplexity API key found"}
        
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "sonar",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return {
            "status": f"✅ Perplexity API reachable (status: {response.status_code})",
            "models": "Sonar + R1-1776 available"
        }
    except Exception as e:
        return {"status": f"❌ Perplexity API failed: {str(e)}"}

def test_database_connection() -> Dict[str, Any]:
    """Test database connectivity"""
    try:
        import psycopg2
        # Try different connection methods
        try:
            conn = psycopg2.connect(
                dbname="aigg_dev",
                user="cosmos", 
                password="mypassword",
                host="localhost"
            )
            conn.close()
            return {"status": "✅ Database connected"}
        except Exception as e:
            return {"status": f"❌ Database failed: {str(e)}"}
    except ImportError:
        return {"status": "❌ psycopg2 not available"}

def main():
    """Run all tests and print results"""
    print("🧪 AIGG Repository Health Check")
    print("=" * 50)
    
    print("\n📋 Environment Variables:")
    env_results = test_environment_variables()
    for var, info in env_results.items():
        status = "✅" if info["exists"] else "❌"
        print(f"  {status} {var}: {'Set' if info['exists'] else 'Missing'}")
    
    print("\n📦 Package Dependencies:")
    import_results = test_imports()
    for package, status in import_results.items():
        print(f"  {status} {package}")
    
    print("\n🌐 Polymarket API:")
    api_results = test_polymarket_api()
    for key, value in api_results.items():
        print(f"  {value}")
    
    print("\n🤖 Perplexity AI API:")
    perplexity_results = test_perplexity_api()
    for key, value in perplexity_results.items():
        print(f"  {value}")
    
    print("\n🗄️ Database Connection:")
    db_results = test_database_connection()
    print(f"  {db_results['status']}")
    
    print("\n" + "=" * 50)
    print("✨ Test complete! Check the results above.")

if __name__ == "__main__":
    main() 