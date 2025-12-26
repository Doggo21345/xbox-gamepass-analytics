import pandas as pd
import json
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from prepare_data import prepare_games_dataset



# ============================================================================
# COMPREHENSIVE GAME PASS IMPACT & GENRE ANALYSIS
# ============================================================================

def load_game_data(file_path):
    """Load and parse tidy JSON game data."""
    with open(file_path, 'r') as f:
        return json.load(f)

def extract_game_row(data):
    """Extract key metrics from a single game's tidy data."""
    try:
        r7 = data.get("rating_7_days", {}).get("RatingCount", 0)
        r30 = data.get("rating_30_days", {}).get("RatingCount", 0)
        r_all = data.get("rating_all_time", {}).get("RatingCount", 0)
        
        rating_7d = data.get("rating_7_days", {}).get("AverageRating", 0)
        rating_30d = data.get("rating_30_days", {}).get("AverageRating", 0)
        rating_all = data.get("rating_all_time", {}).get("AverageRating", 0)
        
        # Parse dates (ISO format expected)
        release_date_str = data.get("original_release_date", "")
        gamepass_date_str = data.get("gamepass_added_date", "")
        
        release_date = pd.to_datetime(release_date_str) if release_date_str else pd.NaT
        gamepass_date = pd.to_datetime(gamepass_date_str) if gamepass_date_str else pd.NaT
        
        days_since_release = (pd.Timestamp.now() - release_date).days if pd.notna(release_date) else None
        days_since_gp_add = (pd.Timestamp.now() - gamepass_date).days if pd.notna(gamepass_date) else None
        
        # MOMENTUM: How much engagement in last 7 days vs 30 days
        momentum = (r7 / r30 * 100) if r30 > 0 else 0
        
        # DISCOVERY CAPTURE: What % of all-time engagement is happening NOW
        discovery_capture = (r7 / r_all * 100) if r_all > 0 else 0
        
        # QUALITY RETENTION: Did GamePass players rate higher than original buyers?
        quality_retention = rating_30d - rating_all
        
        return {
            "title": data.get("title", "Unknown"),
            "genre": data.get("category", "Unknown"),
            "publisher": data.get("publisher", "Unknown"),
            "has_gamepass": data.get("has_gamepass_remediation", False),
            
            # Raw counts
            "rating_count_7d": r7,
            "rating_count_30d": r30,
            "rating_count_alltime": r_all,
            
            # Ratings
            "rating_7d": rating_7d,
            "rating_30d": rating_30d,
            "rating_alltime": rating_all,
            
            # Calculated metrics
            "momentum": round(momentum, 2),
            "discovery_capture": round(discovery_capture, 2),
            "quality_retention": round(quality_retention, 3),
            "rating_trend_7d_vs_alltime": round(rating_7d - rating_all, 3),
            
            # Timeline
            "release": release_date,
            "added": gamepass_date,
            "days_since_release": days_since_release,
            "days_since_gp_add": days_since_gp_add,
            "is_day_one_gp": (days_since_gp_add <= 1) if pd.notna(gamepass_date) else False,
        }
    except Exception as e:
        print(f"Error processing game: {e}")
        return None

def build_aggregated_dataframe(tidy_json_files):
    """Build master DataFrame from multiple tidy JSON files."""
    all_rows = []
    
    for file_path in tidy_json_files:
        try:
            data = load_game_data(file_path)
            row = extract_game_row(data)
            if row:
                all_rows.append(row)
        except Exception as e:
            print(f"Failed to load {file_path}: {e}")
    
    df = pd.DataFrame(all_rows)
    return df

# ============================================================================
# GENRE-LEVEL ANALYSIS
# ============================================================================

def genre_performance_analysis(df):
    """Analyze performance metrics by genre."""
    genre_stats = df.groupby('genre').agg({
        'momentum': ['median', 'mean', 'std'],
        'discovery_capture': ['median', 'mean'],
        'quality_retention': ['median', 'mean'],
        'rating_7d': ['mean', 'std', 'median'],
        'rating_30d': ['mean', 'std', 'median'],
        'rating_alltime': ['mean', 'std', 'median'],
        'rating_trend_7d_vs_alltime': ['mean', 'std', 'median'],
        'title': 'count'  # Number of games per genre
    }).round(2)
    
    genre_stats.columns = ['_'.join(col).strip() for col in genre_stats.columns.values]
    genre_stats = genre_stats.rename(columns={'title_count': 'game_count'})
    genre_stats = genre_stats.sort_values('momentum_median', ascending=False)
    
    return genre_stats

def genre_gamepass_comparison(df):
    """Compare Game Pass vs Non-Game Pass games by genre."""
    comparison = df.groupby(['genre', 'has_gamepass']).agg({ #using the agg fucntion to peform a series of operations on the grouped data to get summary statistics for each genre and Game Pass status
        'momentum': 'mean',
        'discovery_capture': 'mean',
        'quality_retention': 'mean',
        'rating_7d': 'mean',
        'rating_30d': 'mean',
        'rating_alltime': 'mean',
        'title': 'count'
    }).round(2)
    
    comparison = comparison.rename(columns={'title': 'game_count'})
    return comparison

# ============================================================================
# PUBLISHER ANALYSIS
# ============================================================================

def publisher_performance_analysis(df):
    """Identify which publishers are winning on Game Pass."""
    # Overall publisher stats
    pub_stats = df.groupby('publisher').agg({
        'momentum': 'mean',
        'discovery_capture': 'mean',
        'quality_retention': 'mean',
        'rating_7d': 'mean',
        'has_gamepass': 'sum',  # Number of games on GP
        'title': 'count'  # Total games
    }).round(2)
    
    pub_stats.columns = ['momentum_avg', 'discovery_capture_avg', 'quality_retention_avg', 
                         'rating_7d_avg', 'gamepass_count', 'total_games']
    pub_stats['gp_percentage'] = (pub_stats['gamepass_count'] / pub_stats['total_games'] * 100).round(1)
    pub_stats = pub_stats.sort_values('momentum_avg', ascending=False)
    
    return pub_stats

def publisher_gamepass_efficiency(df):
    """Show which publishers see the biggest sentiment jump with Game Pass."""
    gp_vs_paid = df.groupby(['publisher', 'has_gamepass']).agg({
        'momentum': 'mean',
        'quality_retention': 'mean',
        'rating_7d': 'mean',
        'rating_alltime': 'mean'
    }).round(3)
    
    return gp_vs_paid

# ============================================================================
# TREND & CORRELATION ANALYSIS
# ============================================================================

def momentum_rating_correlation(df):
    """Does higher momentum correlate with higher ratings?"""
    # Filter out null values for correlation
    df_clean = df.dropna(subset=['momentum', 'rating_7d', 'rating_30d', 'rating_alltime'])
    
    if len(df_clean) == 0:
        return None
    
    correlation = df_clean[['momentum', 'discovery_capture', 'quality_retention', 
                            'rating_7d', 'rating_30d', 'rating_alltime']].corr().round(3)
    
    return correlation

def day_one_vs_existing_gp(df):
    """Compare day-one Game Pass additions vs games added later."""
    gp_games = df[df['has_gamepass']].copy()
    gp_games = gp_games[gp_games['is_day_one_gp'] == True  if gp_games['release_date'] == gp_games['added'] else False]
    
    day_one = gp_games[gp_games['is_day_one_gp'] == True]
    existing = gp_games[gp_games['is_day_one_gp'] == False]
    
    comparison = pd.DataFrame({
        'Metric': ['Count', 'Momentum (avg)', 'Discovery Capture (avg)', 'Quality Retention (avg)', 'Rating 7d (avg)'],
        'Day-One GP': [
            len(day_one),
            day_one['momentum'].mean().round(2),
            day_one['discovery_capture'].mean().round(2),
            day_one['quality_retention'].mean().round(3),
            day_one['rating_7d'].mean().round(2)
        ],
        'Later Addition': [
            len(existing),
            existing['momentum'].mean().round(2),
            existing['discovery_capture'].mean().round(2),
            existing['quality_retention'].mean().round(3),
            existing['rating_7d'].mean().round(2)
        ]
    })
    
    return comparison

# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def create_visualizations(df, output_prefix="analysis"):
    """Generate key visualizations."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. Momentum by Genre
    genre_momentum = df.groupby('genre')['momentum'].median().sort_values(ascending=False)
    axes[0, 0].barh(genre_momentum.index, genre_momentum.values, color='steelblue')
    axes[0, 0].set_xlabel('Median Momentum (%)')
    axes[0, 0].set_title('Engagement Momentum by Genre')
    
    # 2. Quality Retention by Game Pass Status
    qr_by_gp = df.groupby('has_gamepass')['quality_retention'].mean()
    axes[0, 1].bar(['Paid Only', 'Game Pass'], qr_by_gp.values, color=['coral', 'green'])
    axes[0, 1].set_ylabel('Quality Retention (Rating Change)')
    axes[0, 1].set_title('Do Game Pass Players Rate Higher?')
    axes[0, 1].axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    # 3. Momentum vs Rating 7d Scatter
    scatter = axes[1, 0].scatter(df['momentum'], df['rating_7d'], 
                                 c=df['has_gamepass'].astype(int), cmap='viridis', alpha=0.6, s=50)
    axes[1, 0].set_xlabel('Momentum (%)')
    axes[1, 0].set_ylabel('7-Day Rating')
    axes[1, 0].set_title('Momentum vs Current Rating')
    plt.colorbar(scatter, ax=axes[1, 0], label='Game Pass')
    
    # 4. Discovery Capture Distribution
    axes[1, 1].hist([df[df['has_gamepass'] == False]['discovery_capture'],
                     df[df['has_gamepass'] == True]['discovery_capture']],
                    label=['Paid', 'Game Pass'], bins=15, alpha=0.7)
    axes[1, 1].set_xlabel('Discovery Capture (%)')
    axes[1, 1].set_ylabel('Frequency')
    axes[1, 1].set_title('Current Engagement Share Distribution')
    axes[1, 1].legend()
    
    plt.tight_layout()
    plt.savefig(f'{output_prefix}_visualizations.png', dpi=300, bbox_inches='tight')
    print(f"✓ Visualizations saved to {output_prefix}_visualizations.png")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("COMPREHENSIVE GAME PASS IMPACT ANALYSIS")
    print("=" * 80)
    # Build master dataframe
    df_all = prepare_games_dataset("xbox_data_20251224_1937.json")
    df_all = merge_genre_from_csv(df_all, "xbox_final_cleaned_results.csv")
    print(f"\n📊 Loaded {len(df_all)} games")
    
    # ────────────────────────────────────────────────────────────────────────
    # 1. GENRE PERFORMANCE
    # ────────────────────────────────────────────────────────────────────────
    print("\n" + "="*80)
    print("GENRE PERFORMANCE ANALYSIS")
    print("="*80)
    
    genre_perf = genre_performance_analysis(df_all)
    print("\nGenre Momentum & Ratings:")
    print(genre_perf)
    genre_perf.to_csv("genre_performance.csv")
    print("✓ Saved to genre_performance.csv")
    
    genre_gp = genre_gamepass_comparison(df_all)
    print("\nGame Pass vs Paid Games by Genre:")
    print(genre_gp)
    genre_gp.to_csv("genre_gamepass_comparison.csv")
    print("✓ Saved to genre_gamepass_comparison.csv")
    
    # ────────────────────────────────────────────────────────────────────────
    # 2. PUBLISHER PERFORMANCE
    # ────────────────────────────────────────────────────────────────────────
    print("\n" + "="*80)
    print("PUBLISHER PERFORMANCE ANALYSIS")
    print("="*80)
    
    pub_perf = publisher_performance_analysis(df_all)
    print("\nPublisher Momentum Rankings:")
    print(pub_perf.head(10))
    pub_perf.to_csv("publisher_performance.csv")
    print("✓ Saved to publisher_performance.csv")
    
    pub_efficiency = publisher_gamepass_efficiency(df_all)
    print("\nPublisher Sentiment Jump (GP vs Paid):")
    print(pub_efficiency)
    pub_efficiency.to_csv("publisher_gamepass_efficiency.csv")
    print("✓ Saved to publisher_gamepass_efficiency.csv")
    
    # ────────────────────────────────────────────────────────────────────────
    # 3. CORRELATION & TRENDS
    # ────────────────────────────────────────────────────────────────────────
    print("\n" + "="*80)
    print("CORRELATION & TREND ANALYSIS")
    print("="*80)
    
    corr_matrix = momentum_rating_correlation(df_all)
    if corr_matrix is not None:
        print("\nMetric Correlations:")
        print(corr_matrix)
        corr_matrix.to_csv("metric_correlations.csv")
        print("✓ Saved to metric_correlations.csv")

    
    day_one_comparison = day_one_vs_existing_gp(df_all)
    print("\nDay-One GP vs Later Additions:")
    print(day_one_comparison.to_string(index=False))
    day_one_comparison.to_csv("day_one_vs_later_gamepass.csv", index=False)
    print("✓ Saved to day_one_vs_later_gamepass.csv")
    
    # ────────────────────────────────────────────────────────────────────────
    # 4. VISUALIZATIONS
    # ────────────────────────────────────────────────────────────────────────
    print("\n" + "="*80)
    print("GENERATING VISUALIZATIONS")
    print("="*80)
    
    create_visualizations(df_all, "gamepass_analysis")
    
    # ────────────────────────────────────────────────────────────────────────
    # 5. KEY INSIGHTS
    # ────────────────────────────────────────────────────────────────────────
    print("\n" + "="*80)
    print("KEY INSIGHTS")
    print("="*80)
    
    gp_games = df_all[df_all['has_gamepass'] == True]
    paid_games = df_all[df_all['has_gamepass'] == False]
    
    print(f"\n📈 MOMENTUM:")
    print(f"   Game Pass (avg):  {gp_games['momentum'].mean():.2f}%")
    print(f"   Paid Only (avg):  {paid_games['momentum'].mean():.2f}%")
    
    print(f"\n⭐ QUALITY RETENTION:")
    print(f"   Game Pass (avg):  {gp_games['quality_retention'].mean():.3f} (rating diff from all-time)")
    print(f"   Paid Only (avg):  {paid_games['quality_retention'].mean():.3f}")
    if gp_games['quality_retention'].mean() > 0:
        print(f"   → Game Pass players rate {abs(gp_games['quality_retention'].mean()):.2f} points HIGHER")
    
    print(f"\n🎯 DISCOVERY CAPTURE:")
    print(f"   Game Pass (avg):  {gp_games['discovery_capture'].mean():.2f}% of all-time engagement")
    print(f"   Paid Only (avg):  {paid_games['discovery_capture'].mean():.2f}%")
    
    print(f"\n🏆 TOP GENRE BY MOMENTUM: {genre_perf.index[0]}")
    print(f"   Median Momentum: {genre_perf['momentum_median'].iloc[0]:.2f}%")
    
    print(f"\n👑 TOP PUBLISHER BY MOMENTUM: {pub_perf.index[0]}")
    print(f"   Avg Momentum: {pub_perf['momentum_avg'].iloc[0]:.2f}%")
    print(f"   Game Pass Titles: {int(pub_perf['gamepass_count'].iloc[0])}/{int(pub_perf['total_games'].iloc[0])}")
    
    print("\n" + "="*80)
    print("Analysis complete! Check the CSV files for detailed data.")
    print("="*80)
