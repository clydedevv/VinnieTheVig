#!/usr/bin/env python3
"""
CORRECT Polymarket data population using CLOB API
Uses proper pagination and gets complete market data including market slugs for URLs
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

def fetch_all_markets_clob():
    """
    Fetch ALL markets using CLOB API with proper cursor pagination
    """
    all_markets = []
    next_cursor = ""  # Empty string means start from beginning
    
    print("🚀 Fetching ALL markets from CLOB API with proper pagination...")
    
    while True:
        try:
            # Use the correct CLOB API endpoint
            url = "https://clob.polymarket.com/markets"
            params = {}
            
            if next_cursor:
                params['next_cursor'] = next_cursor
            
            print(f"   Fetching batch with cursor: {next_cursor[:20]}{'...' if len(next_cursor) > 20 else ''}")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract batch data
            batch_markets = data.get('data', [])
            count = data.get('count', 0)
            next_cursor = data.get('next_cursor', '')
            
            if not batch_markets:
                print(f"   No more markets found")
                break
            
            print(f"   ✅ Got {len(batch_markets)} markets in this batch (total: {count})")
            all_markets.extend(batch_markets)
            
            # Check if we've reached the end (cursor 'LTE=' means end)
            if next_cursor == 'LTE=' or not next_cursor:
                print(f"   📊 Reached end of markets (cursor: {next_cursor})")
                break
                
        except Exception as e:
            print(f"   ❌ Error fetching batch: {e}")
            break
    
    print(f"🎯 Total markets fetched from CLOB API: {len(all_markets)}")
    return all_markets

def parse_clob_market_data(market):
    """
    Parse market data from CLOB API format
    """
    try:
        # Extract data using CLOB API field names
        condition_id = market.get('condition_id')
        question = market.get('question', '').strip()
        market_slug = market.get('market_slug', '')
        
        # Extract category from tags (CLOB API uses tags, not category)
        tags = market.get('tags', [])
        if tags and isinstance(tags, list) and len(tags) > 0:
            # Use the first tag that's not 'All' as category
            category = next((tag for tag in tags if tag != 'All'), tags[0] if tags else '')
        else:
            category = ''
        
        # Handle end date
        end_date_str = market.get('end_date_iso')
        end_date = None
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            except Exception as e:
                print(f"Could not parse end_date: {end_date_str} - {e}")
        
        # Extract token prices properly
        tokens = market.get('tokens', [])
        yes_price = None
        no_price = None
        
        for token in tokens:
            outcome = str(token.get('outcome', '')).lower()
            price = token.get('price')
            
            # Map common Yes/No outcomes
            if outcome in ['yes', 'true', '1'] or 'yes' in outcome:
                yes_price = float(price) if price is not None else None
            elif outcome in ['no', 'false', '0'] or 'no' in outcome:
                no_price = float(price) if price is not None else None
            elif len(tokens) == 2:
                # For binary markets with non-standard naming, assign first as "yes", second as "no"
                if yes_price is None:
                    yes_price = float(price) if price is not None else None
                elif no_price is None:
                    no_price = float(price) if price is not None else None
            
        # Determine if market is active
        is_active = market.get('active', False) and not market.get('closed', True)
        
        # Enhanced active detection based on end date
        if end_date:
            current_time = datetime.now(end_date.tzinfo) if end_date.tzinfo else datetime.now()
            is_active = is_active and end_date > current_time
        
        return {
            'market_id': condition_id,
            'title': question,
            'end_date': end_date,
            'category': category,
            'active': is_active,
            'market_slug': market_slug,  # NEW: Store the official market slug
            'yes_price': yes_price,
            'no_price': no_price
        }
        
    except Exception as e:
        print(f"Error parsing market {market.get('condition_id', 'unknown')}: {e}")
        return None

def ensure_market_slug_column(cursor):
    """
    Ensure market_slug column exists in the table
    """
    try:
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'polymarket_markets'
        """)
        
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        if 'market_slug' not in existing_columns:
            print("Adding market_slug column...")
            cursor.execute("ALTER TABLE polymarket_markets ADD COLUMN market_slug VARCHAR(500)")
            
        if 'yes_price' not in existing_columns:
            print("Adding yes_price column...")
            cursor.execute("ALTER TABLE polymarket_markets ADD COLUMN yes_price DECIMAL(10,6)")
            
        if 'no_price' not in existing_columns:
            print("Adding no_price column...")
            cursor.execute("ALTER TABLE polymarket_markets ADD COLUMN no_price DECIMAL(10,6)")
            
    except Exception as e:
        print(f"Error ensuring columns: {e}")

def insert_or_update_clob_market(cursor, market_data):
    """
    Insert or update market with market_slug support
    """
    try:
        sql = """
            INSERT INTO polymarket_markets (
                market_id, title, end_date, category, active, market_slug, yes_price, no_price, last_refreshed
            ) VALUES (
                %(market_id)s, %(title)s, %(end_date)s, %(category)s, %(active)s, %(market_slug)s, %(yes_price)s, %(no_price)s, NOW()
            )
            ON CONFLICT (market_id) DO UPDATE SET
                title = EXCLUDED.title,
                end_date = EXCLUDED.end_date,
                category = EXCLUDED.category,
                active = EXCLUDED.active,
                market_slug = EXCLUDED.market_slug,
                yes_price = EXCLUDED.yes_price,
                no_price = EXCLUDED.no_price,
                last_refreshed = NOW()
        """
        
        cursor.execute(sql, market_data)
        return True
        
    except Exception as e:
        print(f"Error inserting/updating market {market_data.get('market_id', 'unknown')}: {e}")
        return False

def cleanup_old_markets(cursor):
    """
    Deactivate markets that ended before current time
    """
    print("\n🧹 Cleaning up old markets...")
    
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM polymarket_markets 
        WHERE active = true AND end_date <= NOW()
    """)
    to_deactivate = cursor.fetchone()['count']
    
    if to_deactivate > 0:
        print(f"Deactivating {to_deactivate} markets that have ended...")
        
        cursor.execute("""
            UPDATE polymarket_markets 
            SET active = false 
            WHERE active = true AND end_date <= NOW()
        """)
        
        print(f"✅ Deactivated {cursor.rowcount} old markets")
    else:
        print("✅ No old markets to deactivate")

def populate_clob_polymarket_data():
    """
    Main function using CLOB API
    """
    print("🚀 Starting CLOB API Polymarket data population...")
    start_time = time.time()
    
    # Fetch ALL markets from CLOB API
    markets = fetch_all_markets_clob()
    
    if not markets:
        print("No markets fetched. Exiting.")
        return
    
    # Connect to database
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Ensure columns exist
        ensure_market_slug_column(cursor)
        
        # Process markets
        inserted_count = 0
        updated_count = 0
        error_count = 0
        korea_markets = []
        
        for i, market in enumerate(markets):
            if i % 100 == 0:
                print(f"Processing market {i+1}/{len(markets)}")
            
            # Parse market data
            market_data = parse_clob_market_data(market)
            if not market_data:
                error_count += 1
                continue
            
            # Track Korea-related markets
            if 'korea' in market_data['title'].lower():
                korea_markets.append(market_data)
                print(f"🇰🇷 Found Korea market: {market_data['title']} (slug: {market_data['market_slug']})")
            
            # Check if market exists
            cursor.execute("SELECT market_id FROM polymarket_markets WHERE market_id = %s", 
                         (market_data['market_id'],))
            exists = cursor.fetchone() is not None
            
            # Insert or update
            if insert_or_update_clob_market(cursor, market_data):
                if exists:
                    updated_count += 1
                else:
                    inserted_count += 1
            else:
                error_count += 1
        
        # Cleanup old markets
        cleanup_old_markets(cursor)
        
        # Commit changes
        conn.commit()
        
        # Get final counts
        cursor.execute("SELECT COUNT(*) FROM polymarket_markets")
        total_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM polymarket_markets WHERE active = true")
        active_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM polymarket_markets WHERE market_slug IS NOT NULL AND market_slug != ''")
        markets_with_slugs = cursor.fetchone()[0]
        
        # Print summary
        elapsed_time = time.time() - start_time
        print(f"\n=== CLOB API POLYMARKET DATA POPULATION COMPLETE ===")
        print(f"Processing time: {elapsed_time:.2f} seconds")
        print(f"Markets processed: {len(markets)}")
        print(f"New markets inserted: {inserted_count}")
        print(f"Existing markets updated: {updated_count}")
        print(f"Errors: {error_count}")
        print(f"Total markets in database: {total_count}")
        print(f"Active markets: {active_count}")
        print(f"Markets with slugs: {markets_with_slugs}")
        print(f"Korea markets found: {len(korea_markets)}")
        
        if korea_markets:
            print(f"\n🇰🇷 KOREA MARKETS FOUND:")
            for km in korea_markets:
                slug_info = f" (slug: {km['market_slug']})" if km['market_slug'] else " (no slug)"
                print(f"   • {km['title']}{slug_info}")
                print(f"     ID: {km['market_id']}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    populate_clob_polymarket_data() 