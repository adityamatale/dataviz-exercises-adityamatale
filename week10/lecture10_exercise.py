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
    path = Path(__file__).parent.parent / 'data' / 'co2_emissions.csv'
    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-01-01')
    return df

df = load_data()

st.title("🌱 CO2 Emissions Explorer")
st.caption("Source: Our World in Data — ourworldindata.org/co2-emissions")

# ── TASK 1: Sidebar with 5 widgets ────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")

    # a) Region selectbox (with 'All')
    regions = ['All'] + sorted(df['Region'].unique())
    selected_region = st.selectbox("Region", regions)

    # b) Country multiselect — chained to region
    if selected_region == 'All':
        country_options = sorted(df['Country'].unique())
    else:
        country_options = sorted(df[df['Region'] == selected_region]['Country'].unique())

    selected_countries = st.multiselect(
        "Countries", country_options, default=country_options[:5]
    )

    # c) Date range picker (two-handle)
    date_range = st.date_input(
        "Date range",
        value=(datetime.date(2000, 1, 1), datetime.date(2022, 1, 1)),
        min_value=datetime.date(int(df['Year'].min()), 1, 1),
        max_value=datetime.date(int(df['Year'].max()), 1, 1),
        format="YYYY-MM-DD"
    )

    # d) Metric radio
    metric = st.radio("Metric", ["Total CO2 (Mt)", "CO2 per capita"])

    # e) Highlight checkbox
    highlight_top = st.checkbox("Show only top emitter highlighted")

# ── Guards ─────────────────────────────────────────────────────────────────────
if not selected_countries:
    st.warning("👆 Select at least one country.")
    st.stop()

if len(date_range) != 2:
    st.warning("Select a start AND end date.")
    st.stop()

start_ts, end_ts = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])

filtered = df[
    df['Country'].isin(selected_countries) &
    (df['Date'] >= start_ts) & (df['Date'] <= end_ts)
]
if selected_region != 'All':
    filtered = filtered[filtered['Region'] == selected_region]

if filtered.empty:
    st.warning("No data matches these filters.")
    st.stop()

y_col = 'CO2_Mt' if metric == "Total CO2 (Mt)" else 'CO2_per_capita'
y_label = 'CO2 Emissions (Mt)' if y_col == 'CO2_Mt' else 'CO2 per Capita'

# ── TASK 2: Filter summary caption ────────────────────────────────────────────
st.caption(
    f"{len(selected_countries)} countries | {selected_region} | "
    f"{date_range[0].strftime('%d %b %Y')} – {date_range[1].strftime('%d %b %Y')} | {metric}"
)

# ── TASK 3: Two charts reacting to ALL filters ────────────────────────────────
col_left, col_right = st.columns([2, 1])

with col_left:
    if highlight_top:
        # BBD colour type: Highlight — one series drawn attention to, rest greyed
        top_emitter = (filtered[filtered['Date'] == filtered['Date'].max()]
                        .sort_values(y_col, ascending=False)['Country'].iloc[0])
        color_map = {c: '#2E75B6' if c == top_emitter else '#DDDDDD' for c in selected_countries}

        fig1 = px.line(filtered, x='Date', y=y_col, color='Country',
                        color_discrete_map=color_map,
                        labels={y_col: y_label, 'Date': ''})
        fig1.update_traces(line=dict(width=1.5), showlegend=False)
        fig1.update_traces(line=dict(width=3), selector=dict(name=top_emitter))

        last = filtered[(filtered['Country'] == top_emitter) & (filtered['Date'] == filtered['Date'].max())]
        fig1.add_annotation(
            x=last['Date'].values[0], y=last[y_col].values[0],
            text=f'<b>{top_emitter}</b>', showarrow=False,
            xanchor='left', xshift=6,
            font=dict(color='#2E75B6', size=12, family='Arial')
        )
        title1 = f'{top_emitter} leads emissions among selected countries'
    else:
        # BBD colour type: Categorical — unordered group, one colour per country
        fig1 = px.line(filtered, x='Date', y=y_col, color='Country',
                        labels={y_col: y_label, 'Date': ''})
        title1 = f'{metric} over time — selected countries'

    fig1.update_layout(
        title=title1,
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Arial', size=12, color='#2C2C2C'),
        title_font=dict(family='Arial', size=14, color='#2C2C2C'),
        xaxis=dict(showgrid=False, title=''),
        yaxis=dict(gridcolor='#EEEEEE'),
        margin=dict(l=60, r=60, t=55, b=40)
    )
    st.plotly_chart(fig1, use_container_width=True, theme=None)

with col_right:
    latest = filtered[filtered['Date'] == filtered['Date'].max()].sort_values(y_col)

    # BBD colour type: Highlight — single ranking series, not a category
    fig2 = px.bar(latest, x=y_col, y='Country', orientation='h',
                  color_discrete_sequence=['#2E75B6'],
                  labels={y_col: y_label, 'Country': ''})
    fig2.update_layout(
        title=f'Ranking — {int(latest["Year"].iloc[0])}',
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Arial', size=12, color='#2C2C2C'),
        title_font=dict(family='Arial', size=14, color='#2C2C2C'),
        xaxis=dict(range=[0, latest[y_col].max() * 1.15], gridcolor='#EEEEEE'),
        yaxis=dict(showgrid=False),
        margin=dict(l=100, r=30, t=55, b=60)
    )
    fig2.update_traces(marker_line_width=0)
    st.plotly_chart(fig2, use_container_width=True, theme=None)

# ── EXTENSION: KPI row ────────────────────────────────────────────────────────
last_year = filtered['Year'].max()
first_year = filtered['Year'].min()

total_last = filtered[filtered['Year'] == last_year][y_col].sum()
total_first = filtered[filtered['Year'] == first_year][y_col].sum()
pct_change = (total_last - total_first) / total_first * 100 if total_first else 0

top_country_last = (filtered[filtered['Year'] == last_year]
                     .sort_values(y_col, ascending=False)['Country'].iloc[0])

st.divider()
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric(f"Total {metric} ({int(last_year)})", f"{total_last:,.0f}")
kpi2.metric(f"Change since {int(first_year)}", f"{pct_change:+.1f}%")
kpi3.metric("Top emitter", top_country_last)