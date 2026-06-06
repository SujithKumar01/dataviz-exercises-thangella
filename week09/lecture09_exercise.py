"""
Lecture 9 Exercise — World Happiness Dashboard
================================================
Run with: streamlit run lecture09_exercise.py

Dashboard purpose (REQUIRED — write this before any code):
# PURPOSE: [one sentence: audience + what they can do with this dashboard]

BBD colour rule: name the colour type you use in a comment next to each chart:
# COLOUR TYPE: sequential / diverging / categorical / highlight
"""

import streamlit as st
import pandas as pd
import plotly.express as px

df = pd.read_csv('/Users/sujith/Documents/Data_Visualization/data-viz-class-material/data/world_happiness_2023.csv')
df.columns = ['Country','Region','Score','GDP','Social_Support',
              'Life_Expectancy','Freedom','Generosity','Corruption']

st.set_page_config(page_title="World Happiness Dashboard", page_icon="🌍", layout="wide")

# ─────────────────────────────────────────────────────────────────────────────
# TASK 1: Title and caption
# ─────────────────────────────────────────────────────────────────────────────
# YOUR CODE HERE
st.set_page_config(page_title="World Happiness Dashboard", page_icon="🌍", layout="wide")

st.markdown("""
<style>
.block-container { padding-top: 1.5rem; }
[data-testid="metric-container"] {
    background-color: #F8F9FA;
    border: 1px solid #E9ECEF;
    padding: 1rem;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

st.title("🌍 World Happiness Dashboard")
st.caption("Source: World Happiness Report 2023 | Kaggle")

# ─────────────────────────────────────────────────────────────────────────────
# TASK 2: Sidebar filters
#   - st.selectbox for Region ('All' option)
#   - st.slider for top N countries (5-30, default 15)
# Filter the dataframe. Store as `filtered`.
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")
    # YOUR CODE HERE
    regions = ['All'] + sorted(df['Region'].unique().tolist())
    selected_region = st.selectbox("Region", regions)
    top_n = st.slider("Show top N countries", 5, 30, 15)
    st.caption("Colour notes: blue sequential scale for ranking, single blue highlight for scatter, diverging scale for above/below average.")


# filtered = ...
filtered = df if selected_region == 'All' else df[df['Region'] == selected_region]
top = filtered.nlargest(top_n, 'Score').sort_values('Score')
global_avg = df['Score'].mean()
selection_avg = filtered['Score'].mean()
happiest = filtered.nlargest(1, 'Score').iloc[0]

# ─────────────────────────────────────────────────────────────────────────────
# TASK 3: KPI row — 3 st.metric() cards
#   1. Number of countries shown
#   2. Average score (with delta vs global average)
#   3. Happiest country in current selection
# ─────────────────────────────────────────────────────────────────────────────
# YOUR CODE HERE
k1, k2, k3 = st.columns(3)
k1.metric("Countries shown", len(filtered))
k2.metric("Average happiness score", f"{selection_avg:.2f}", f"{selection_avg - global_avg:+.2f} vs global")
k3.metric("Happiest country", happiest['Country'], f"Score: {happiest['Score']:.2f}")


st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# TASK 4: Two-column layout — two charts
#   Left (wider): horizontal bar of top N countries, sorted by score
#   Right: scatter of GDP vs Score
#
# BBD colour requirement:
#   - Name the colour type you chose (sequential/diverging/categorical/highlight)
#     in a comment next to the colour argument
#   - Do NOT use red and green as the only differentiator (CVD rule)
#
# SWD requirements:
#   - White background, Arial font
#   - Bar chart x-axis starts at 0
#   - Insight title (not topic title)
#   - use_container_width=True
# ─────────────────────────────────────────────────────────────────────────────
# YOUR CODE HERE
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("Happiness Rankings")
    # COLOUR TYPE: sequential
    fig1 = px.bar(
        top,
        x='Score',
        y='Country',
        orientation='h',
        color='Score',
        color_continuous_scale='Blues',
        range_color=[4.5, 8.5],
        labels={'Score': 'Happiness Score (0–10)', 'Country': ''}
    )
    fig1.update_layout(
        title='The happiest countries score well above the global average',
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(range=[0, 8.5], gridcolor='#EEEEEE'),
        yaxis=dict(showgrid=False),
        coloraxis_showscale=False,
        font=dict(family='Arial', size=12),
        margin=dict(l=10, r=10, t=50, b=10)
    )
    fig1.update_traces(marker_line_width=0)
    st.plotly_chart(fig1, use_container_width=True)
    
    
    
with col_right:
    st.subheader("GDP vs Happiness")
    # COLOUR TYPE: highlight
    fig2 = px.scatter(
        filtered,
        x='GDP',
        y='Score',
        hover_name='Country',
        color_discrete_sequence=['#2E75B6'],
        labels={'GDP': 'GDP Contribution', 'Score': 'Happiness Score'}
    )
    fig2.update_layout(
        title='Higher GDP generally aligns with higher happiness',
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(gridcolor='#EEEEEE'),
        yaxis=dict(gridcolor='#EEEEEE'),
        font=dict(family='Arial', size=12),
        margin=dict(l=10, r=10, t=50, b=10)
    )
    fig2.update_traces(marker=dict(size=9, opacity=0.8))
    st.plotly_chart(fig2, use_container_width=True)



st.divider()

st.subheader("Extension: Countries above and below the global average")

diverge_df = filtered.copy()
diverge_df['Score_vs_Global'] = diverge_df['Score'] - global_avg
diverge_top = diverge_df.reindex(diverge_df['Score_vs_Global'].abs().sort_values(ascending=False).index).head(20)
diverge_top = diverge_top.sort_values('Score_vs_Global')


# ─────────────────────────────────────────────────────────────────────────────
# EXTENSION: Add a third chart of your choice using a DIVERGING colour scale
# (something where values go above and below a meaningful midpoint)
# Label the midpoint in an annotation.
# ─────────────────────────────────────────────────────────────────────────────
# YOUR CODE HERE (optional)
# COLOUR TYPE: diverging
fig3 = px.bar(
    diverge_top,
    x='Score_vs_Global',
    y='Country',
    orientation='h',
    color='Score_vs_Global',
    color_continuous_scale='RdBu',
    color_continuous_midpoint=0,
    labels={'Score_vs_Global': 'Score vs Global Avg', 'Country': ''}
)

fig3.add_vline(
    x=0,
    line_dash='dash',
    line_color='black',
    annotation_text='Global average',
    annotation_position='top'
)

fig3.update_layout(
    title='Some countries sit far above the global happiness average while others remain far below',
    plot_bgcolor='white',
    paper_bgcolor='white',
    xaxis=dict(gridcolor='#EEEEEE'),
    yaxis=dict(showgrid=False),
    font=dict(family='Arial', size=12),
    margin=dict(l=10, r=10, t=60, b=10),
    coloraxis_colorbar=dict(title='Vs Global<br>Average')
)

fig3.update_traces(marker_line_width=0)
st.plotly_chart(fig3, use_container_width=True)

st.caption("Built with Streamlit + Plotly")