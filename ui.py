import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt

df = pd.read_csv('gamepass_impact_report.csv')
st.title('Xbox Game Pass Analysis Mk1 (Mortal Kombat 1 vs SF6 (Street Fighter 6))')
st.write('This application analyzes the impact of Xbox Game Pass on game performance, focusing on Mortal Kombat 1 and Street Fighter 6. Both games were similar in terms of rating (at least by xbox players all time) when they were released, but MK1 was added to Game Pass a week ago, while SF6 was not. This analysis explores how Game Pass inclusion affects various performance metrics such as player count, engagement, and revenue.')

st.dataframe(df)

st.write('Overall from the data frame we can see that the Discovery Momentum for Street Fighter™ 6 is significantly lower than that of Mortal Kombat™ 1, indicating that being part of Xbox Game Pass has a substantial positive impact on a game\'s visibility and player engagement.')


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