#!/usr/bin/env python3
"""
Populate Polymarket data from the Gamma API.
This script fetches market data and populates the polymarket_markets table.
ENHANCED: Now includes automatic cleanup of old markets and odds fetching.
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

def fetch_polymarket_markets():
    """
    Fetch markets from Polymarket Gamma API.
    Returns list of market dictionaries.
    """
    try:
        # Use Gamma API for market data
        url = "https://gamma-api.polymarket.com/markets"
        
        # Add parameters for active markets
        params = {
            'limit': 2000,  # Get even more markets
            'offset': 0
        }
        
        print(f"Fetching markets from Gamma API: {url}")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Gamma API returns markets directly as an array or in a 'data' field
        if isinstance(data, list):
            markets = data
        elif isinstance(data, dict) and 'data' in data:
            markets = data['data']
        else:
            print(f"Unexpected API response format: {type(data)}")
            return []
            
        print(f"Successfully fetched {len(markets)} markets from Gamma API")
        return markets
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching markets: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

def parse_market_data(market):
    """
    Parse market data from Gamma API format to our database format.
    ENHANCED: Now includes odds data parsing.
    """
    try:
        # Extract basic info
        market_id = market.get('id')
        title = market.get('question', '').strip()
        
        # Handle end date
        end_date_str = market.get('end_date') or market.get('endDate')
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
                    print(f"Could not parse end_date: {end_date_str}")
        
        # Extract other fields
        category = market.get('category', '').strip()
        
        # ENHANCED: Extract odds data
        tokens = market.get('tokens', [])
        yes_price = None
        no_price = None
        
        for token in tokens:
            outcome = token.get('outcome', '').lower()
            price = token.get('price') or token.get('last_price')
            if price:
                try:
                    price_float = float(price)
                    if outcome in ['yes', 'true', '1']:
                        yes_price = price_float
                    elif outcome in ['no', 'false', '0']:
                        no_price = price_float
                except (ValueError, TypeError):
                    continue
        
        # ENHANCED: Determine if market should be active based on end date
        # Only consider markets active if they end after June 1, 2025
        is_actually_active = True
        if end_date:
            current_time = datetime.now(end_date.tzinfo) if end_date.tzinfo else datetime.now()
            is_actually_active = end_date > current_time and end_date > datetime(2025, 6, 1, tzinfo=end_date.tzinfo)
        
        return {
            'market_id': market_id,
            'title': title,
            'end_date': end_date,
            'category': category,
            'active': is_actually_active,  # ENHANCED: Smart active detection
            'yes_price': yes_price,
            'no_price': no_price
        }
        
    except Exception as e:
        print(f"Error parsing market {market.get('id', 'unknown')}: {e}")
        return None

def ensure_odds_columns_exist(cursor):
    """
    Ensure that odds columns exist in the table.
    """
    try:
        # Check if columns exist and add them if they don't
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
    """
    Insert or update a market in the database.
    ENHANCED: Now includes odds data.
    """
    try:
        # Use UPSERT (INSERT ... ON CONFLICT) with correct column names
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

def cleanup_old_markets(cursor):
    """
    ENHANCED: Deactivate markets that ended before June 1, 2025.
    """
    print("\n🧹 Cleaning up old markets...")
    
    # Count markets to deactivate
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM polymarket_markets 
        WHERE active = true AND end_date <= '2025-06-01'
    """)
    to_deactivate = cursor.fetchone()['count']
    
    if to_deactivate > 0:
        print(f"Deactivating {to_deactivate} markets that ended before/on June 1, 2025...")
        
        cursor.execute("""
            UPDATE polymarket_markets 
            SET active = false 
            WHERE active = true AND end_date <= '2025-06-01'
        """)
        
        print(f"✅ Deactivated {cursor.rowcount} old markets")
    else:
        print("✅ No old markets to deactivate")

def populate_polymarket_data():
    """
    Main function to populate Polymarket data.
    ENHANCED: Now includes cleanup and odds fetching.
    """
    print("Starting ENHANCED Polymarket data population...")
    start_time = time.time()
    
    # Fetch markets from API
    markets = fetch_polymarket_markets()
    if not markets:
        print("No markets fetched. Exiting.")
        return
    
    # Connect to database
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # ENHANCED: Ensure odds columns exist
        ensure_odds_columns_exist(cursor)
        
        # Process markets
        inserted_count = 0
        updated_count = 0
        error_count = 0
        
        for i, market in enumerate(markets):
            if i % 100 == 0:
                print(f"Processing market {i+1}/{len(markets)}")
            
            # Parse market data
            market_data = parse_market_data(market)
            if not market_data:
                error_count += 1
                continue
            
            # Check if market exists
            cursor.execute("SELECT market_id FROM polymarket_markets WHERE market_id = %s", (market_data['market_id'],))
            exists = cursor.fetchone() is not None
            
            # Insert or update
            if insert_or_update_market(cursor, market_data):
                if exists:
                    updated_count += 1
                else:
                    inserted_count += 1
            else:
                error_count += 1
        
        # ENHANCED: Cleanup old markets after updating
        cleanup_old_markets(cursor)
        
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
        print(f"Markets processed: {len(markets)}")
        print(f"New markets inserted: {inserted_count}")
        print(f"Existing markets updated: {updated_count}")
        print(f"Errors: {error_count}")
        print(f"Total markets in database: {total_count}")
        print(f"Active markets: {active_count}")
        print(f"Markets with odds data: {markets_with_odds}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    populate_polymarket_data() 