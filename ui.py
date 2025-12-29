import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from streamlit_option_menu import option_menu


df = pd.read_csv('gamepass_impact_report.csv')
st.title('Xbox Game Pass Analysis Mk1 (Mortal Kombat 1 vs SF6 (Street Fighter 6))')
st.write('This application analyzes the impact of Xbox Game Pass on game performance, focusing on Mortal Kombat 1 and Street Fighter 6. Both games were similar in terms of rating (at least by xbox players all time) when they were released, but MK1 was added to Game Pass a week ago, while SF6 was not. This analysis explores how Game Pass inclusion affects various performance metrics such as player count, engagement, and revenue.')
st.dataframe(df)

selected = option_menu(
    menu_title=None,
    options=["Overview", "Inital Use Case: MK1 vs SF6", "Genre Analysis", "Engagement Metrics", "Revenue Impact"],
    icons=["house", "bar-chart", "pie-chart", "graph-up", "currency-dollar"],
    orientation="horizontal",
)

st.markdown("From the data pulled from the microsoft store API there is a clear difference in the games including that MK1 just overall is way more popular than SF6 overall. ")
st.write("In order to determine if Game Pass then had an actually statistical impact on the games performance we can look at the discovery momentum of both games. Discovery momentum is a metric that measures how much a game is being discovered and played by new players. A higher discovery momentum indicates that a game is gaining popularity and attracting new players over the past 7 days as a percenatge of the the last month" \
" The time fram of a week is important as MK1 was added to game pass a week ago, so we can see if there is a significant difference in discovery momentum between the two games.")
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
#Visualization of the inital use case of sf 6 vs mk1
sns.set_theme(
    style="darkgrid",
    rc={
        "axes.facecolor": "#0e1117",   # Streamlit dark bg
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
    "Mortal Kombat™ 1": "#1f77b4",   # blue
    "Street Fighter™ 6": "#d62728"   # red
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



