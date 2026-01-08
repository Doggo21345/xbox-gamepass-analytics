import json
import pandas as pd
from datetime import datetime
import os

# ============================================================================
# CONVERT RAW XBOX JSON TO TIDY FORMAT FOR ANALYSIS
# ============================================================================

def prepare_games_dataset(json_file):
    """Convert raw Xbox API JSON to analysis-ready format."""
    
    with open(json_file, 'r') as f:
        games = json.load(f)
    
    prepared_games = []
    
    for game in games:
        try:
            # Extract ratings safely
            r7 = game.get('rating_7_days', {})
            r30 = game.get('rating_30_days', {})
            r_all = game.get('rating_all_time', {})
            
            prepared_game = {
                "product_id": game.get('product_id'),
                "title": game.get('title'),
                "publisher": game.get('publisher', 'Unknown'),
                "developer": game.get('developer', 'Unknown'),
                "short_description": game.get('short_description', ''),
                
                # Category/Genre (will be "Unknown" - can enrich later)
                "category": game.get('category', 'unkown'),
                
                # Release & GP dates
                "original_release_date": game.get('release_date'),
                "gamepass_added_date": None,  # Not in this dataset
                
                # Rating counts (7-day, 30-day, all-time)
                "rating_7_days_count": r7.get('RatingCount', 0),
                "rating_30_days_count": r30.get('RatingCount', 0),
                "rating_alltime_count": r_all.get('RatingCount', 0),
                
                # Average ratings
                "rating_7_days_avg": r7.get('AverageRating', 0),
                "rating_30_days_avg": r30.get('AverageRating', 0),
                "rating_alltime_avg": r_all.get('AverageRating', 0),
                
                # Rating play counts
                "Rating_play_count_7_days": r7.get('PlayCount', 0),
                "Rating_play_count_30_days": r30.get('PlayCount', 0),
                "Rating_play_count_alltime": r_all.get('PlayCount', 0),

                # GamePass status
                "has_gamepass_remediation": game.get('has_gamepass_remediation', False),
                
                # Pricing (extract first non-zero price)
                "current_price": next(
                    (p.get('list_price', 0) for p in game.get('prices', []) if p.get('list_price', 0) > 0),
                    0
                ),
            }
            prepared_games.append(prepared_game)
            
        except Exception as e:
            print(f"Warning: Skipped {game.get('title', 'Unknown')}: {e}")
    
    # Create DataFrame
    df = pd.DataFrame(prepared_games)
    
    # Convert dates
    df['original_release_date'] = pd.to_datetime(df['original_release_date'], errors='coerce')
    
    # Filter out games with zero ratings (not yet released/no engagement)
    df_active = df[
        (df['rating_alltime_count'] > 0) | 
        (df['rating_7_days_count'] > 0) | 
        (df['rating_30_days_count'] > 0)
    ].copy()
    
    print(f"📊 Prepared {len(df_active)} games with engagement data")
    print(f"   (Excluded {len(df) - len(df_active)} games with zero ratings)")
    
    return df_active

def create_tidy_json(df, output_file):
    """Save as tidy JSON for the analysis script."""
    tidy_data = df.to_dict('records')
    
    with open(output_file, 'w') as f:
        json.dump(tidy_data, f, indent=2, default=str)
    
    print(f"✓ Saved {len(tidy_data)} games to {output_file}")
    return output_file


def merge_genre_from_csv(df, csv_file, left_key='title', right_key_candidates=('Game', 'title', 'Title')):
    """Left-join additional metadata (genre/publisher etc.) from a CSV onto the prepared df.

    - `left_key` is the column in `df` (defaults to 'title').
    - `right_key_candidates` are column names to try in the CSV for the game/title column.
    """
    if not os.path.exists(csv_file):
        print(f"→ Merge source not found: {csv_file}")
        return df

    other = pd.read_csv(csv_file)

    # Try to find the matching key in the CSV
    right_key = None
    for k in right_key_candidates:
        if k in other.columns:
            right_key = k
            break

    if right_key is None:
        print(f"→ No suitable title column found in {csv_file}. Columns: {list(other.columns)[:10]}")
        return df

    # Normalize keys for more robust exact matching
    df['_merge_key'] = df[left_key].astype(str).str.strip().str.lower()
    other['_merge_key'] = other[right_key].astype(str).str.strip().str.lower()

    merged = df.merge(other, on='_merge_key', how='left', suffixes=(None, '_src'))

    # If the CSV contains a genre or category column, prefer it
    if 'category' in merged.columns:
        merged['category'] = merged['category']
    elif 'Genre' in merged.columns:
        merged['category'] = merged['Genre']
    elif 'genre' in merged.columns:
        merged['category'] = merged['genre']

    # Clean up helper column
    merged = merged.drop(columns=['_merge_key'])
    print(f"✓ Merged metadata from {csv_file} (matched on '{right_key}')")
    return merged

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Step 1: Prepare the data
    print("=" * 80)
    print("PREPARING XBOX DATA FOR ANALYSIS")
    print("=" * 80)
    
    df = prepare_games_dataset("xbox_data_20251224_1937.json")
    
    print("\n📈 Dataset Summary:")
    print(f"   Total Games: {len(df)}")
    print(f"   Game Pass Games: {df['has_gamepass_remediation'].sum()}")
    print(f"   Paid Games: {len(df) - df['has_gamepass_remediation'].sum()}")
    print(f"\n   Rating Activity:")
    print(f"      Games with 7-day ratings: {(df['rating_7_days_count'] > 0).sum()}")
    print(f"      Games with 30-day ratings: {(df['rating_30_days_count'] > 0).sum()}")
    print(f"      Games with all-time ratings: {(df['rating_alltime_count'] > 0).sum()}")
    
    # Step 2: Save as tidy JSON
    create_tidy_json(df, "xbox_tidy.json")
    
    # Step 3: Also save as CSV for quick review
    df.to_csv("xbox_prepared.csv", index=False)
    print("✓ Saved to xbox_prepared.csv")
    
    print("\n" + "=" * 80)
    print("✅ Data ready! Next steps:")
    print("=" * 80)
    print("\n1. Update comprehensive_game_analysis.py to use:")
    print("   tidy_files = ['xbox_tidy.json']")
    print("\n2. Run: python comprehensive_game_analysis.py")
    print("\n3. Check the output CSV files and PNG visualization!")
    print("=" * 80)


