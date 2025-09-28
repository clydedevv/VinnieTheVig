#!/usr/bin/env python3
"""
ENHANCED Polymarket data population with full pagination and multiple API sources
Fixes the pagination issue that was causing us to miss markets like South Korea election
"""

import requests
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv                                          
from datetime import datetime
import time

# Load environment variables
load_dotenv()

def get_db_connection():
    """Get database connection."""
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

def fetch_all_markets_with_pagination():
    """
    ENHANCED: Fetch ALL markets using pagination to ensure we don't miss any
    """
    all_markets = []
    limit = 1000  # Smaller batches for reliability
    offset = 0
    
    print("🔄 Fetching ALL markets with pagination...")
    
    while True:
        try:
            url = "https://gamma-api.polymarket.com/markets"
            params = {
                'limit': limit,
                'offset': offset
            }
            
            print(f"   Fetching batch: offset={offset}, limit={limit}")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Handle response format
            if isinstance(data, list):
                batch_markets = data
            elif isinstance(data, dict) and 'data' in data:
                batch_markets = data['data']
            else:
                print(f"   Unexpected API response format: {type(data)}")
                break
            
            if not batch_markets:
                print(f"   No more markets found at offset {offset}")
                break
            
            print(f"   ✅ Got {len(batch_markets)} markets in this batch")
            all_markets.extend(batch_markets)
            
            # If we got fewer markets than the limit, we've reached the end
            if len(batch_markets) < limit:
                print(f"   📊 Reached end of markets (got {len(batch_markets)} < {limit})")
                break
            
            offset += limit
            
            # Safety check to prevent infinite loops
            if offset > 10000:  # Max 10k markets
                print(f"   ⚠️ Safety limit reached at offset {offset}")
                break
                
        except Exception as e:
            print(f"   ❌ Error fetching batch at offset {offset}: {e}")
            break
    
    print(f"🎯 Total markets fetched with pagination: {len(all_markets)}")
    return all_markets

def fetch_specific_markets():
    """
    Try to fetch specific high-value markets that might be missing
    """
    print("🎯 Searching for specific high-value markets...")
    
    # Try different API endpoints or search patterns
    specific_markets = []
    
    # Try searching for popular election markets
    search_terms = [
        "South Korea president",
        "Korea election", 
        "Lee Jae-myung",
        "Korean election"
    ]
    
    for term in search_terms:
        try:
            # Try if there's a search endpoint
            search_url = f"https://gamma-api.polymarket.com/markets?search={term}"
            response = requests.get(search_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and data:
                    print(f"   ✅ Found {len(data)} markets for '{term}'")
                    specific_markets.extend(data)
        except:
            continue
    
    return specific_markets

def parse_market_data(market):
    """
    ENHANCED: Parse market data with better field handling
    """
    try:
        # Extract basic info with multiple field name attempts
        market_id = market.get('id') or market.get('market_id')
        title = (market.get('question') or market.get('title') or '').strip()
        
        # Handle end date with multiple formats
        end_date_str = (market.get('end_date') or 
                       market.get('endDate') or 
                       market.get('end_time'))
        end_date = None
        if end_date_str:
            try:
                # Try parsing ISO format
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            except:
                try:
                    # Try parsing timestamp
                    end_date = datetime.fromtimestamp(float(end_date_str))
                except:
                    try:
                        # Try other formats
                        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                    except:
                        print(f"Could not parse end_date: {end_date_str}")
        
        # Extract category
        category = (market.get('category') or 
                   market.get('markets_category') or '').strip()
        
        # ENHANCED: Extract odds data with multiple attempts
        tokens = market.get('tokens', [])
        outcomes = market.get('outcomes', [])
        yes_price = None
        no_price = None
        
        # Try tokens first
        for token in tokens:
            outcome = str(token.get('outcome', '')).lower()
            price = token.get('price') or token.get('last_price') or token.get('current_price')
            if price:
                try:
                    price_float = float(price)
                    if outcome in ['yes', 'true', '1', 'lee jae-myung']:
                        yes_price = price_float
                    elif outcome in ['no', 'false', '0']:
                        no_price = price_float
                except (ValueError, TypeError):
                    continue
        
        # Try outcomes if tokens didn't work
        if not yes_price and not no_price:
            for outcome in outcomes:
                outcome_name = str(outcome.get('name', '')).lower()
                price = outcome.get('price') or outcome.get('last_price')
                if price:
                    try:
                        price_float = float(price)
                        if 'yes' in outcome_name or 'lee jae-myung' in outcome_name:
                            yes_price = price_float
                        elif 'no' in outcome_name:
                            no_price = price_float
                    except (ValueError, TypeError):
                        continue
        
        # ENHANCED: Better active detection
        is_actually_active = True
        if end_date:
            current_time = datetime.now(end_date.tzinfo) if end_date.tzinfo else datetime.now()
            is_actually_active = end_date > current_time
        
        # Also check if market is explicitly marked as inactive
        if market.get('active') is False or market.get('status') in ['closed', 'resolved']:
            is_actually_active = False
        
        return {
            'market_id': str(market_id),
            'title': title,
            'end_date': end_date,
            'category': category,
            'active': is_actually_active,
            'yes_price': yes_price,
            'no_price': no_price
        }
        
    except Exception as e:
        print(f"Error parsing market {market.get('id', 'unknown')}: {e}")
        return None

def ensure_odds_columns_exist(cursor):
    """Ensure odds columns exist"""
    try:
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'polymarket_markets'
        """)
        
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        if 'yes_price' not in existing_columns:
            print("Adding yes_price column...")
            cursor.execute("ALTER TABLE polymarket_markets ADD COLUMN yes_price DECIMAL(10,6)")
            
        if 'no_price' not in existing_columns:
            print("Adding no_price column...")
            cursor.execute("ALTER TABLE polymarket_markets ADD COLUMN no_price DECIMAL(10,6)")
            
    except Exception as e:
        print(f"Error ensuring odds columns: {e}")

def insert_or_update_market(cursor, market_data):
    """Insert or update market with enhanced error handling"""
    try:
        sql = """
            INSERT INTO polymarket_markets (
                market_id, title, end_date, category, active, yes_price, no_price, last_refreshed
            ) VALUES (
                %(market_id)s, %(title)s, %(end_date)s, %(category)s, %(active)s, %(yes_price)s, %(no_price)s, NOW()
            )
            ON CONFLICT (market_id) DO UPDATE SET
                title = EXCLUDED.title,
                end_date = EXCLUDED.end_date,
                category = EXCLUDED.category,
                active = EXCLUDED.active,
                yes_price = EXCLUDED.yes_price,
                no_price = EXCLUDED.no_price,
                last_refreshed = NOW()
        """
        
        cursor.execute(sql, market_data)
        return True
        
    except Exception as e:
        print(f"Error inserting/updating market {market_data.get('market_id', 'unknown')}: {e}")
        return False

def populate_enhanced_polymarket_data():
    """
    ENHANCED main function with full pagination
    """
    print("🚀 Starting ENHANCED Polymarket data population with FULL PAGINATION...")
    start_time = time.time()
    
    # Fetch ALL markets with pagination
    all_markets = fetch_all_markets_with_pagination()
    
    # Also try to fetch specific markets
    specific_markets = fetch_specific_markets()
    if specific_markets:
        print(f"🎯 Adding {len(specific_markets)} specific markets")
        all_markets.extend(specific_markets)
    
    # Remove duplicates by ID
    seen_ids = set()
    unique_markets = []
    for market in all_markets:
        market_id = market.get('id') or market.get('market_id')
        if market_id and market_id not in seen_ids:
            seen_ids.add(market_id)
            unique_markets.append(market)
    
    print(f"📊 Total unique markets to process: {len(unique_markets)}")
    
    if not unique_markets:
        print("No markets fetched. Exiting.")
        return
    
    # Connect to database
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Ensure odds columns exist
        ensure_odds_columns_exist(cursor)
        
        # Process markets
        inserted_count = 0
        updated_count = 0
        error_count = 0
        korea_markets = []
        
        for i, market in enumerate(unique_markets):
            if i % 100 == 0:
                print(f"Processing market {i+1}/{len(unique_markets)}")
            
            # Parse market data
            market_data = parse_market_data(market)
            if not market_data:
                error_count += 1
                continue
            
            # Track Korea-related markets
            if 'korea' in market_data['title'].lower():
                korea_markets.append(market_data)
                print(f"🇰🇷 Found Korea market: {market_data['title']}")
            
            # Check if market exists
            cursor.execute("SELECT market_id FROM polymarket_markets WHERE market_id = %s", 
                         (market_data['market_id'],))
            exists = cursor.fetchone() is not None
            
            # Insert or update
            if insert_or_update_market(cursor, market_data):
                if exists:
                    updated_count += 1
                else:
                    inserted_count += 1
            else:
                error_count += 1
        
        # Commit changes
        conn.commit()
        
        # Get final counts
        cursor.execute("SELECT COUNT(*) FROM polymarket_markets")
        total_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM polymarket_markets WHERE active = true")
        active_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM polymarket_markets WHERE active = true AND yes_price IS NOT NULL")
        markets_with_odds = cursor.fetchone()[0]
        
        # Print summary
        elapsed_time = time.time() - start_time
        print(f"\n=== ENHANCED POLYMARKET DATA POPULATION COMPLETE ===")
        print(f"Processing time: {elapsed_time:.2f} seconds")
        print(f"Markets processed: {len(unique_markets)}")
        print(f"New markets inserted: {inserted_count}")
        print(f"Existing markets updated: {updated_count}")
        print(f"Errors: {error_count}")
        print(f"Total markets in database: {total_count}")
        print(f"Active markets: {active_count}")
        print(f"Markets with odds data: {markets_with_odds}")
        print(f"Korea markets found: {len(korea_markets)}")
        
        if korea_markets:
            print(f"\n🇰🇷 KOREA MARKETS FOUND:")
            for km in korea_markets:
                print(f"   • {km['title']} (ID: {km['market_id']})")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    populate_enhanced_polymarket_data() 