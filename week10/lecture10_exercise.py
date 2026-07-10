
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import datetime

st.set_page_config(page_title="CO2 Dashboard", page_icon="🌱", layout="wide")

# ── Data ──────────────────────────────────────────────────────────────────────
# @st.cache_data: Streamlit reruns the entire script on every widget interaction.
# Without caching, the CSV is read from disk on every interaction — slow and wasteful.
# cache_data stores the result after the first run and reuses it until the file changes.
@st.cache_data
def load_data():
    # path = Path(__file__).parent.parent / 'data' / 'co2_emissions.csv'
    path = '/Users/sujith/Documents/Data_Visualization/data-viz-class-material/data/co2_emissions.csv'
    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-01-01')
    return df

df = load_data()

st.title("🌱 CO2 Emissions Explorer")
st.caption("Source: Our World in Data — ourworldindata.org/co2-emissions")

# ── TASK 1: Sidebar with 5 widgets ────────────────────────────────────────────
#   a) st.selectbox for Region (with 'All')
#   b) st.multiselect for Countries (updates based on region — chained)
#   c) st.date_input for date range (two-handle; convert years to Jan-1 dates)
#   d) st.radio for Metric: "Total CO2 (Mt)" vs "CO2 per capita"
#   e) st.checkbox labelled "Show only top emitter highlighted"
#
# Guards:
#   - empty countries → st.warning + st.stop()
#   - incomplete date_input → st.warning + st.stop()
# Convert date_input result to pd.Timestamp before filtering.
# ─────────────────────────────────────────────────────────────────────────────


# ── TASK 1: Sidebar with 5 widgets ────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")

    # a) Region selectbox — default 'All' (BBD: default to the most common case)
    regions = ['All'] + sorted(df['Region'].unique())
    selected_region = st.selectbox("Region", regions)

    # b) Chained multiselect — country list narrows based on region
    if selected_region == 'All':
        country_options = sorted(df['Country'].unique())
    else:
        country_options = sorted(df[df['Region'] == selected_region]['Country'].unique())

    default_countries = country_options[:4] if len(country_options) >= 4 else country_options
    selected_countries = st.multiselect("Countries", country_options, default=default_countries)

    # Guard: empty countries → warn + stop (never show an empty chart silently)
    if not selected_countries:
        st.warning("👆 Select at least one country.")
        st.stop()

    # c) date_input — two-handle calendar range; years converted to Jan-1 dates in loader
    date_range = st.date_input(
        "Date range",
        value=(datetime.date(2000, 1, 1), datetime.date(2022, 1, 1)),
        min_value=datetime.date(int(df['Year'].min()), 1, 1),
        max_value=datetime.date(int(df['Year'].max()), 1, 1),
        format="YYYY-MM-DD"
    )

    # Guard: incomplete date range (user clicked start but not end yet)
    if len(date_range) != 2:
        st.warning("Select a start AND end date.")
        st.stop()

    st.divider()

    # d) radio — 2 mutually exclusive options, clearer than a selectbox here
    metric = st.radio("Metric", ["Total CO2 (Mt)", "CO2 per capita"])

    # e) checkbox — default False (unchecked = show all countries in full color)
    highlight_top = st.checkbox("Show only top emitter highlighted")

# Always convert date_input → pd.Timestamp before pandas comparisons
start_ts, end_ts = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])

filtered = df[
    df['Country'].isin(selected_countries) &
    (df['Date'] >= start_ts) &
    (df['Date'] <= end_ts)
]

# Guard: empty result after filtering
if filtered.empty:
    st.warning("No data in this date range for the selected countries.")
    st.stop()

y_col = 'CO2_Mt' if metric == "Total CO2 (Mt)" else 'CO2_per_capita'
y_label = 'CO2 Emissions (Mt)' if y_col == 'CO2_Mt' else 'CO2 per Capita (t)'

last_year = filtered['Year'].max()
first_year = filtered['Year'].min()
latest = filtered[filtered['Year'] == last_year].sort_values(y_col)
top_emitter = latest.sort_values(y_col, ascending=False).iloc[0]['Country']



# filtered = ...  # apply all filters and store here


# ── TASK 2: Filter summary caption ────────────────────────────────────────────
# Show: "X countries | Region | Date range | Metric"
# BBD rule: always show users how many records match current filters
# ─────────────────────────────────────────────────────────────────────────────
st.caption(
    f"{len(selected_countries)} countries | {selected_region} | "
    f"{date_range[0].strftime('%d %b %Y')} – {date_range[1].strftime('%d %b %Y')} | {metric}"
)

# ── EXTENSION: KPI row above the charts ───────────────────────────────────────
first_total = filtered[filtered['Year'] == first_year][y_col].sum()
last_total = filtered[filtered['Year'] == last_year][y_col].sum()
pct_change = ((last_total - first_total) / first_total * 100) if first_total else float('nan')

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric(f"Total {metric} ({int(last_year)})", f"{last_total:,.1f}")
kpi2.metric(f"% change since {int(first_year)}", f"{pct_change:+.1f}%")
kpi3.metric("Top emitter (latest year)", top_emitter, f"{latest[y_col].max():,.1f}")


# ── TASK 3: Two charts reacting to ALL filters ────────────────────────────────
#   Left: line chart — selected metric over time, one line per country
#         If "Show only top emitter highlighted" checkbox is on:
#           - grey all lines except the highest emitter in the date range
#           - label that country at the end of its line (SWD grey-and-highlight)
#   Right: bar chart — ranking for the last year in selected date range
#
# BBD colour requirement: name the colour type in a comment next to each chart
# SWD requirements: white background, insight title, use_container_width=True
# ─────────────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([2, 1])

with col_left:
    # Line chart
    if highlight_top:
        # BBD grey-and-highlight color: categorical grey for context,
        # single highlight hue to draw the eye to one series (SWD technique)
        color_map = {c: '#BFBFBF' for c in selected_countries}
        color_map[top_emitter] = '#C00000'

        fig1 = px.line(filtered, x='Year', y=y_col, color='Country',
                       color_discrete_map=color_map,
                       labels={y_col: y_label},
                       title=f'{metric} over time — {top_emitter} highlighted')

        # Grey out non-highlighted lines and drop them from the legend for a cleaner read
        for trace in fig1.data:
            if trace.name != top_emitter:
                trace.showlegend = False
                trace.line.width = 1.5
            else:
                trace.line.width = 3

        # Label the highlighted country directly at the end of its line (SWD: label, don't rely on legend)
        top_line = filtered[filtered['Country'] == top_emitter].sort_values('Year')
        last_point = top_line.iloc[-1]
        fig1.add_annotation(
            x=last_point['Year'], y=last_point[y_col],
            text=top_emitter, showarrow=False,
            xanchor='left', yanchor='middle',
            font=dict(color='#C00000', size=12),
            xshift=8
        )
    else:
        # BBD categorical color: one distinct hue per country from a wide qualitative palette
        fig1 = px.line(filtered, x='Year', y=y_col, color='Country',
                       color_discrete_sequence=px.colors.qualitative.Alphabet,
                       labels={y_col: y_label},
                       title=f'{metric} over time')

    fig1.update_layout(plot_bgcolor='white', paper_bgcolor='white', font=dict(family='Arial'))
    st.plotly_chart(fig1, width='stretch')
    pass

with col_right:
    # Bar chart
    # BBD highlight color: single hue, since this chart ranks one metric rather than comparing categories
    fig2 = px.bar(latest, x=y_col, y='Country', orientation='h',
                  color_discrete_sequence=['#2E75B6'],
                  title=f'Latest year ({int(last_year)}) ranking')
    fig2.update_layout(plot_bgcolor='white', paper_bgcolor='white', font=dict(family='Arial'),
                       xaxis=dict(range=[0, latest[y_col].max() * 1.15]))
    fig2.update_traces(marker_line_width=0)
    st.plotly_chart(fig2, width='stretch')
    pass


# ── EXTENSION: KPI row above the charts ───────────────────────────────────────
#   - Total CO2 in last year of selected range (sum across selected countries)
#   - % change from first to last year
#   - Country with highest emissions in last year
# ─────────────────────────────────────────────────────────────────────────────
# YOUR CODE HERE (optional)