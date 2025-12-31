import pandas as pd
import json
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from prepare_data import prepare_games_dataset



# ============================================================================
# COMPREHENSIVE GAME PASS IMPACT & Genre ANALYSIS
# ============================================================================

def load_game_data(file_path):
    """Load and parse tidy JSON game data."""
    with open(file_path, 'r') as f:
        return json.load(f)

def calculate_game_metrics(df):
    """Add calculated metric columns directly to DataFrame."""
    # Get rating counts
    r7 = pd.to_numeric(df["rating_7_days_count"], errors='coerce').fillna(0)
    r30 = pd.to_numeric(df["rating_30_days_count"], errors='coerce').fillna(0)
    r_all = pd.to_numeric(df["rating_alltime_count"], errors='coerce').fillna(0)
    
    # Get ratings
    rating_7d = pd.to_numeric(df["rating_7_days_avg"], errors='coerce').fillna(0)
    rating_30d = pd.to_numeric(df["rating_30_days_avg"], errors='coerce').fillna(0)
    rating_all = pd.to_numeric(df["rating_alltime_avg"], errors='coerce').fillna(0)

    
    # Parse dates
    release_date = pd.to_datetime(df["Release"], errors='coerce')
    gamepass_date = pd.to_datetime(df["Added"], errors='coerce')

    # Normalize timezones: make sure datetimes are tz-naive so subtraction works
    # If series are timezone-aware, convert to naive by removing tz info.
    try:
        if getattr(release_date.dt, 'tz', None) is not None:
            release_date = release_date.dt.tz_convert(None)
    except Exception:
        # fallback: attempt elementwise removal
        release_date = release_date.apply(lambda x: x.tz_convert(None) if getattr(x, 'tzinfo', None) is not None else x)

    try:
        if getattr(gamepass_date.dt, 'tz', None) is not None:
            gamepass_date = gamepass_date.dt.tz_convert(None)
    except Exception:
        gamepass_date = gamepass_date.apply(lambda x: x.tz_convert(None) if getattr(x, 'tzinfo', None) is not None else x)
    
    # Calculate time deltas using a tz-naive 'now'
    now = pd.Timestamp.now()
    df['days_since_release'] = (now - release_date).dt.days
    df['days_since_gp_add'] = (now - gamepass_date).dt.days
    
    # Calculate metrics
    df['momentum'] = ((r7 / r30 * 100).fillna(0)).round(2)
    df['discovery_capture'] = ((r7 / r_all * 100).fillna(0)).round(2)
    df['quality_retention'] = (rating_30d - rating_all).round(3)
    df['rating_trend_7d_vs_alltime'] = (rating_7d - rating_all).round(3)
    df['is_day_one_gp'] = (df['days_since_gp_add'] <= 1) & (gamepass_date.notna())
    
    return df


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
# Genre-LEVEL ANALYSIS
# ============================================================================

def Genre_performance_analysis(df):
    """Analyze performance metrics by Genre."""
    Genre_stats = df.groupby('Genre').agg({
        'momentum': ['median', 'mean', 'std'],
        'discovery_capture': ['median', 'mean'],
        'quality_retention': ['median', 'mean'],
        'rating_7_days_count': ['mean', 'std', 'median'],
        'rating_30_days_count': ['mean', 'std', 'median'],
        'rating_alltime_count': ['mean', 'std', 'median'],
        'rating_alltime_avg': ['mean', 'std', 'median'],
        'rating_30_days_avg': ['mean', 'std', 'median'],
        'rating_7_days_avg': ['mean', 'std', 'median'],
        'rating_trend_7d_vs_alltime': ['mean', 'std', 'median'],
        'title': 'count'  # Number of games per Genre
    }).round(2)
    
    Genre_stats.columns = ['_'.join(col).strip() for col in Genre_stats.columns.values]
    Genre_stats = Genre_stats.rename(columns={'title_count': 'game_count'})
    Genre_stats = Genre_stats.sort_values('momentum_median', ascending=False)
    
    return Genre_stats

def Genre_gamepass_comparison(df):
    """Compare Game Pass vs Non-Game Pass games by Genre."""
    comparison = df.groupby(['Genre', 'has_gamepass_remediation']).agg({ #using the agg fucntion to peform a series of operations on the grouped data to get summary statistics for each Genre and Game Pass status
        'momentum': ['mean', 'std', 'median'],
        'discovery_capture': ['mean', 'std', 'median'],
        'quality_retention': ['mean', 'std', 'median'],
        'rating_7_days_avg': ['mean', 'std', 'median'],
        'rating_30_days_avg': ['mean', 'std', 'median'],
        'rating_alltime_avg': ['mean', 'std', 'median'],
        'rating_7_days_count': ['mean', 'std', 'median'],
        'rating_30_days_count': ['mean', 'std', 'median'],
        'rating_alltime_count': ['mean', 'std', 'median'],
        'has_gamepass_remediation': 'sum',  # Number of games on GP
        'title': 'count'  # Total games
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
        'momentum': ['mean', 'std', 'median'],
        'discovery_capture': ['mean', 'std', 'median'],
        'quality_retention': ['mean', 'std', 'median'],
        'rating_7_days_avg': ['mean', 'std', 'median'],
        'rating_30_days_avg': ['mean', 'std', 'median'],
        'rating_alltime_avg': ['mean', 'std', 'median'],
        'rating_7_days_count': ['mean', 'std', 'median'],
        'rating_30_days_count': ['mean', 'std', 'median'],
        'rating_alltime_count': ['mean', 'std', 'median'],
        'has_gamepass_remediation': 'sum',  # Number of games on GP
        'title': 'count'  # Total games
    }).round(2)

    pub_stats = pub_stats.rename(columns={'title': 'total_games', 'has_gamepass_remediation': 'gamepass_count',
                                          'title_count': 'total_games',
                                          'momentum_mean': 'momentum_avg',
                                          'discovery_capture_mean': 'discovery_capture_avg',
                                          'quality_retention_mean': 'quality_retention_avg'})
    gp_percentage = (pub_stats['gamepass_count'] / pub_stats['total_games'] * 100).round(1)
    

    return pub_stats, gp_percentage

def publisher_gamepass_efficiency(df):
    """Show which publishers see the biggest sentiment jump with Game Pass."""
    gp_vs_paid = df.groupby(['publisher', 'has_gamepass_remediation']).agg({
        'momentum': 'mean',
        'discovery_capture': 'mean',
        'quality_retention': 'mean',
        'rating_7_days_avg': ['mean', 'std', 'median'],
        'rating_30_days_avg': ['mean', 'std', 'median'],
        'rating_alltime_avg': ['mean', 'std', 'median'],
        'rating_7_days_count': ['mean', 'std', 'median'],
        'rating_30_days_count': ['mean', 'std', 'median'],
        'rating_alltime_count': ['mean', 'std', 'median'],
        'has_gamepass_remediation': 'sum',  # Number of games on GP
        'title': 'count'  # Total games
    }).round(3)
    
    return gp_vs_paid

# ============================================================================
# TREND & CORRELATION ANALYSIS
# ============================================================================

def momentum_rating_correlation(df):
    """Does higher momentum correlate with higher ratings?"""
    # Filter out null values for correlation
    df_clean = df.dropna(subset=['momentum', 'rating_7_days_avg', 'rating_30_days_avg', 'rating_alltime_avg'])
    
    if len(df_clean) == 0:
        return None
    
    correlation = df_clean[['momentum', 'discovery_capture', 'quality_retention', 
                            'rating_7_days_avg', 'rating_30_days_avg', 'rating_alltime_avg']].corr().round(3)

    return correlation

def day_one_vs_existing_gp(df):
    """Compare day-one Game Pass additions vs games added later."""
    gp_games = df[df['has_gamepass_remediation'] == True].copy()
    # ensure datetimes
    gp_games['Release'] = pd.to_datetime(gp_games['Release'], errors='coerce')
    gp_games['Added'] = pd.to_datetime(gp_games['Added'], errors='coerce')
    # elementwise day-one mask: same calendar date (or within 1 day tolerance)
    gp_games['is_day_one_gp'] = (
        gp_games['Added'].notna()
    ) & (
        (gp_games['Added'].dt.date == gp_games['Release'].dt.date) |
        (gp_games['Added'] - gp_games['Release']).dt.days.abs().le(1)
    )
    
    day_one = gp_games[gp_games['is_day_one_gp'] == True]
    existing = gp_games[gp_games['is_day_one_gp'] == False]
    
    comparison = pd.DataFrame({
        'Day-One GP': [
            len(day_one),
            day_one['momentum'].mean().round(2),
            day_one['discovery_capture'].mean().round(2),
            day_one['quality_retention'].mean().round(3),
            day_one['rating_7_days_avg'].mean().round(2),
            day_one['rating_7_days_count'].mean().round(2)
        ],
        'Later Addition': [
            len(existing),
            existing['momentum'].mean().round(2),
            existing['discovery_capture'].mean().round(2),
            existing['quality_retention'].mean().round(3),
            existing['rating_7_days_avg'].mean().round(2),
            existing['rating_7_days_count'].mean().round(2)
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
    Genre_momentum = df.groupby('Genre')['momentum'].median().sort_values(ascending=False)
    axes[0, 0].barh(Genre_momentum.index, Genre_momentum.values, color='steelblue')
    axes[0, 0].set_xlabel('Median Momentum (%)')
    axes[0, 0].set_title('Engagement Momentum by Genre')
    
    # 2. Quality Retention by Game Pass Status
    qr_by_gp = df.groupby('has_gamepass_remediation')['quality_retention'].mean()
    axes[0, 1].bar(['Paid Only', 'Game Pass'], qr_by_gp.values, color=['coral', 'green'])
    axes[0, 1].set_ylabel('Quality Retention (Rating Change)')
    axes[0, 1].set_title('Do Game Pass Players Rate Higher?')
    axes[0, 1].axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    # 3. Momentum vs Rating 7d Scatter
    scatter = axes[1, 0].scatter(df['momentum'], df['rating_7_days_count'], 
                                 c=df['has_gamepass_remediation'].astype(int), cmap='viridis', alpha=0.6, s=50)
    axes[1, 0].set_xlabel('Momentum (%)')
    axes[1, 0].set_ylabel('7-Day Rating')
    axes[1, 0].set_title('Momentum vs Current Rating')
    plt.colorbar(scatter, ax=axes[1, 0], label='Game Pass')
    
    # 4. Discovery Capture Distribution
    axes[1, 1].hist([df[df['has_gamepass_remediation'] == False]['discovery_capture'],
                     df[df['has_gamepass_remediation'] == True]['discovery_capture']],
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
    # Load and process dataframe
    df_all = pd.read_csv('xbox_final_merged_data.csv')
    df_all = calculate_game_metrics(df_all)
    print(f"\n📊 Loaded and processed {len(df_all)} games")
    

 # ────────────────────────────────────────────────────────────────────────
    # 1. Genre PERFORMANCE
    # ────────────────────────────────────────────────────────────────────────
    print("\n" + "="*80)
    print("Genre PERFORMANCE ANALYSIS")
    print("="*80)
    
    Genre_perf = Genre_performance_analysis(df_all)
    print("\nGenre Momentum & Ratings:")
    print(Genre_perf)
    Genre_perf.to_csv("Genre_performance.csv")
    print("✓ Saved to Genre_performance.csv")
    
    df_all = pd.read_csv('xbox_final_merged_data.csv')
    df_all = calculate_game_metrics(df_all)
    Genre_gp = Genre_gamepass_comparison(df_all)
    print("\nGame Pass vs Paid Games by Genre:")
    print(Genre_gp)
    Genre_gp.to_csv("Genre_gamepass_comparison.csv")
    print("✓ Saved to Genre_gamepass_comparison.csv")
    
    # ────────────────────────────────────────────────────────────────────────
    # 2. PUBLISHER PERFORMANCE
    # ────────────────────────────────────────────────────────────────────────
    print("\n" + "="*80)
    print("PUBLISHER PERFORMANCE ANALYSIS")
    print("="*80)

    pub_perf, gp_percentage = publisher_performance_analysis(df_all)
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
    
    gp_games = df_all[df_all['has_gamepass_remediation'] == True]
    paid_games = df_all[df_all['has_gamepass_remediation'] == False]
    
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
    
    print(f"\n🏆 TOP Genre BY MOMENTUM: {Genre_perf.index[0]}")
    print(f"   Median Momentum: {Genre_perf['momentum_median'].iloc[0]:.2f}%")
    
    print(f"\n👑 TOP PUBLISHER BY MOMENTUM: {pub_perf.index[0]}")
    print(f"   Game Pass Titles: {int(pub_perf['gamepass_count'].iloc[0])}/{int(pub_perf['total_games'].iloc[0])}")
    
    print("\n" + "="*80)
    print("Analysis complete! Check the CSV files for detailed data.")
    print("="*80)


