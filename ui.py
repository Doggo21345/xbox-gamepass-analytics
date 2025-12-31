import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from streamlit_option_menu import option_menu

selected = option_menu(
    menu_title=None,
    options=["Overview", "Proof of Concept", "Genre Analysis", "Engagement Metrics", "Revenue Impact", "Watch the Series!"],
    icons=["house", "bar-chart", "pie-chart", "graph-up", "currency-dollar"],
    orientation="horizontal",
)

if selected == "Proof of Concept":
    df = pd.read_csv('gamepass_impact_report.csv')
    st.title('Xbox Game Pass  _Analysis_ is :blue[MK1 (Mortal Kombat 1)] vs :red[SF6 (Street Fighter 6)]')
    st.write('This application analyzes the impact of Xbox Game Pass on game performance, focusing on Mortal Kombat 1 and Street Fighter 6. Both games were similar in terms of rating (at least by xbox players all time) when they were released, but MK1 was added to Game Pass a week ago, while SF6 was not. This analysis explores how Game Pass inclusion affects various performance metrics such as player count, engagement, and revenue.')
    st.dataframe(df)
    st.markdown("From the data pulled from the microsoft store API there is a clear difference in the games including that MK1 just overall is way more popular than SF6 overall. ")
    st.write("In order to determine if Game Pass then had an actually statistical impact on the games performance we can look at the discovery momentum of both games. Discovery momentum is a metric that measures how much a game is being discovered and played by new players. A higher discovery momentum indicates that a game is gaining popularity and attracting new players over the past 7 days as a percenatge of the the last month" 
    " The time frame of a week is important as MK1 was added to game pass a week ago, so we can see if there is a significant difference in discovery momentum between the two games.")
    latext = r'''
## Discovery Momentum (%)
### Full equation 
$$ 
\text{Discovery Momentum (\%)}=  \frac{a}{b} \cdot 100
$$ 
### Where:
- $a = \text{The number of votes in the last 7 days}$
- $b = \text{The number of votes in the last 30 days}$
'''
    st.write(latext)
    
    sns.set_theme(
        style="darkgrid",
        rc={
            "axes.facecolor": "#0e1117",
            "figure.facecolor": "#0e1117",
            "axes.edgecolor": "#9aa0a6",
            "grid.color": "#2a2f3a",
            "text.color": "#e8eaed",
            "axes.labelcolor": "#e8eaed",
            "xtick.color": "#e8eaed",
            "ytick.color": "#e8eaed",
        }
    )
    color_map = {
        "Mortal Kombat™ 1": "#1f77b4",
        "Street Fighter™ 6": "#d62728"
    }

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(
        data=df,
        x="Game Title",
        y="Discovery Momentum (%)",
        palette=color_map,
        ax=ax
    )

    ax.set_title("Discovery Momentum by Game")
    ax.set_xlabel("")
    ax.set_ylabel("Discovery Momentum (%)")
    plt.xticks(rotation=0)
    sns.despine(left=True, bottom=True)
    st.pyplot(fig)
    st.markdown("Even with this one of the major questions publishers still have is: **Do the players on Game Pass actually stick around for a long time I.E are they players that are of lower quality and only be around this for a short amount of time or do they actually engage with the game over a long period of time?** To answer this we can look at the engagement metrics of both games below.")
    SF6, MK1 = st.columns(2)
    SF6.metric("Recent Ratings (7d) for SF6", "1.3", "-60.61%", border=True, help = "Over the past 7days SF6 has seen a significant drop in ratings compared to the current momentum of those in the 30 days.")
    MK1.metric("Recent Ratings (7d) for Mk1", "2.6", "+4%", border=True, 
               help="Over the past 7days Mk1 has seen a slight increase in ratings compared to the current momentum of those in the 30 days.")
    st.markdown("From the engagement metrics above we can see that MK1 has a much higher recent rating compared to SF6. This indicates that players on Game Pass are more engaged with the game and are more likely to leave positive reviews. Althought it is a slight increase it is still a positive trend compared to SF6 which is seeing a significant drop in recent ratings.")
    st.markdown("Overall they should instead of getting someone to buy into thge game with game pass insetead seek for them to get them into the ecosystem")
    st.header("Reccomended Actions", divider= True )
    st.markdown('Since we can see that overall MK1 had a very high amount of current discovery momentum with quality players Nether Realm Studios should focus on trying to make the most of that')
    st.header('What :blue[MK1] Should Do :sunglasses:')
    st.markdown('- Provide Discounts on DLCs/other digital related products in order to increase revnue through the new influx of customers ')
    st.markdown('- Run promotional invasions to new game pass players or an exclusive skin or smth that will unlock after 10+ hours of gameplay to retain players')
    st.header('What :red[SF6] Should Do 💼')
    st.markdown('- Right now I think on xbox at least they are losing out to people who view MK1 as Free Alternative SF6 use to do a free weekend of play where anyone could download and try SF6 so maybe it might not be a bad idea to reintroduce that ')
    st.markdown('- Aditionally it looks like overall the ratings have been trending negativley in product ratings in the Xbox community so consider trying to incentive community events in the new Battle Hub to get others on the game ')


elif selected == "Watch the Series!":
    st.title('Check out the full series in Short Video Format!')
    st.video("https://www.youtube.com/shorts/oNFDN8k1bpc", format="video/mp4", start_time=0)

elif selected == "Genre Analysis":
    st.markdown("For the genre analsysis I wanted to see what games worked well in game pass and which genres are not performing the best right now To start off I looked at the ***Momentum score*** I came up with for the POC to quantify the impact of GP would have especially during the Holiday Season")
    st.write("As a reminder here is the formula for the momentum metric")
    latext = r'''
## Discovery Momentum (%)

### Full equation 

$$ 
\text{Discovery Momentum (\%)} = \frac{a}{b} \cdot 100
$$ 

### Where:
- $a$ = The number of votes in the last 7 days
- $b$ = The number of votes in the last 30 days
'''
    st.write(latext)
    st.markdown("Since the genres are an aggregation of games I used the agg function ijn python to compute summary statistics for each genre here is the code down below")
    st.code("""
def Genre_performance_analysis(df):
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
        'title': 'count'  
    }).round(2)
    """, language="python")
    st.markdown("This was used to compute an *aggregate baseline* for the genre level of all of the games inside of the data set The reasoning behind this was to see whether the discovery metrics for each genre were something that was trending upwards in the genre as whole or just on gamepass ")
    df = pd.read_csv("Genre_performance.csv")
    st.markdown("We are then able to get the following CSV once that happens")