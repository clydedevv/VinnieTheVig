#!/usr/bin/env python3
"""Get unique categories from Polymarket markets"""
import psycopg2
import os
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', '37.27.54.184'),
        port=os.getenv('DB_PORT', 5432),
        database=os.getenv('DB_NAME', 'aigg'),
        user=os.getenv('DB_USER', 'aigg_user'),
        password=os.getenv('DB_PASSWORD', 'ankur98')
    )
    
    cursor = conn.cursor()
    
    # FIRST: Get total counts
    print("=== MARKET COUNTS ===")
    cursor.execute("SELECT COUNT(*) FROM polymarket_markets")
    total = cursor.fetchone()[0]
    print(f"Total markets in database: {total:,}")
    
    cursor.execute("SELECT COUNT(*) FROM polymarket_markets WHERE active = true")
    active = cursor.fetchone()[0]
    print(f"Active markets: {active:,}")
    
    cursor.execute("SELECT COUNT(*) FROM polymarket_markets WHERE active = false")
    inactive = cursor.fetchone()[0]
    print(f"Inactive markets: {inactive:,}")
    
    # Get volume stats
    cursor.execute("""
        SELECT 
            SUM(volume) as total_volume,
            AVG(volume) as avg_volume,
            MAX(volume) as max_volume
        FROM polymarket_markets 
        WHERE active = true
    """)
    vol_stats = cursor.fetchone()
    print(f"\nActive market volume stats:")
    print(f"  Total: ${int(vol_stats[0] or 0):,}")
    print(f"  Average: ${int(vol_stats[1] or 0):,}")
    print(f"  Max: ${int(vol_stats[2] or 0):,}")
    
    # Get all unique categories
    print("\n=== CATEGORIES ===")
    cursor.execute("""
        SELECT DISTINCT category, COUNT(*) as count
        FROM polymarket_markets
        WHERE category IS NOT NULL AND category != ''
        GROUP BY category
        ORDER BY count DESC
    """)
    
    categories = cursor.fetchall()
    
    print(f"Found {len(categories)} unique categories:\n")
    total_markets = 0
    for cat, count in categories[:20]:  # Top 20
        print(f"  {cat:<30} {count:>6} markets")
        total_markets += count
    
    if len(categories) > 20:
        print(f"  ... and {len(categories) - 20} more categories")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    print("\nTrying alternative: mock categories based on common Polymarket patterns")
    
    # Common Polymarket categories (estimated)
    mock_categories = [
        "Crypto", "Politics", "Sports", "Entertainment", "Science",
        "Economics", "Technology", "Geopolitics", "Climate", "Culture",
        "US Politics", "International", "Football", "Basketball", "Baseball",
        "Movies", "Music", "Gaming", "Space", "AI"
    ]
    
    print("Mock categories (for testing):")
    for cat in mock_categories:
        print(f"  - {cat}")