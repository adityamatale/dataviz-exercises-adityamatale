# pages/03_demand.py — demand drill-down (BBD squiggle: page 3 of 3)
import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import load_data, sidebar_filters

df, p95 = load_data()
filtered = sidebar_filters(df, p95)

st.title('Where is guest demand strongest?')
st.caption('BBD squiggle: market summary → neighbourhood story → demand')

demand_df = filtered[filtered['reviews_per_month'] > 0]

if demand_df.empty:
    st.warning('No listings with review activity match current filters.')
    st.stop()

if 'demand_sort' not in st.session_state:
    st.session_state.demand_sort = 'Highest demand first'
else:
    st.session_state.demand_sort = st.session_state.demand_sort

st.radio(
    'Sort neighbourhoods by',
    ['Highest demand first', 'Lowest demand first'],
    key='demand_sort',
    horizontal=True
)
ascending = st.session_state.demand_sort == 'Lowest demand first'

st.divider()

hood_demand = (demand_df.groupby('neighbourhood')['reviews_per_month']
               .mean().sort_values(ascending=False))

k1, k2, k3 = st.columns(3)
k1.metric('Active listings', f'{len(demand_df):,}',
          f'{len(demand_df) - len(filtered):+,} vs all filtered')
k2.metric('Avg reviews/month', f"{demand_df['reviews_per_month'].mean():.2f}")
k3.metric('Highest-demand area', hood_demand.index[0],
          f"{hood_demand.iloc[0]:.2f} reviews/mo")

st.divider()

col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.subheader('Demand is concentrated in a handful of neighbourhoods')

    top3 = hood_demand.head(3).index.tolist()
    plot_df = hood_demand.sort_values(ascending=ascending).reset_index()
    plot_df['highlight'] = plot_df['neighbourhood'].apply(
        lambda n: 'Top 3' if n in top3 else 'Other')

    # BBD HIGHLIGHT: blue = top-3 demand areas, grey = rest (CVD-safe)
    fig1 = px.bar(
        plot_df, x='reviews_per_month', y='neighbourhood',
        orientation='h', color='highlight',
        color_discrete_map={'Top 3': '#2E75B6', 'Other': '#AAAAAA'},
        labels={'reviews_per_month': 'Avg Reviews / Month', 'neighbourhood': ''}
    )
    fig1.update_traces(marker_line_width=0)
    fig1.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Arial', size=11, color='#333333'), showlegend=False,
        xaxis=dict(gridcolor='#EEEEEE', automargin=True),
        yaxis=dict(showgrid=False, automargin=True),
        margin=dict(l=60, r=30, t=40, b=60)
    )
    st.plotly_chart(fig1, use_container_width=True, theme=None)

with col_right:
    st.subheader('Demand vs price')
    # BBD CATEGORICAL: room type = unordered distinct group (blue/orange/grey, CVD-safe)
    fig2 = px.scatter(
        demand_df, x='price', y='reviews_per_month', color='room_type',
        color_discrete_map={
            'Entire home/apt': '#2E75B6',
            'Private room':    '#E07B39',
            'Shared room':     '#AAAAAA'
        },
        labels={'price': 'Nightly Price (£)', 'reviews_per_month': 'Reviews / Month'},
        opacity=0.5
    )
    fig2.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Arial', size=11, color='#333333'),
        legend=dict(orientation='h', y=1.12, title='', font=dict(color='#333333')),
        xaxis=dict(gridcolor='#EEEEEE', automargin=True),
        yaxis=dict(gridcolor='#EEEEEE', automargin=True),
        margin=dict(l=60, r=30, t=40, b=60)
    )
    st.plotly_chart(fig2, use_container_width=True, theme=None)

with st.expander('📊 Show demand data sample'):
    st.dataframe(
        demand_df[['neighbourhood', 'room_type', 'price', 'reviews_per_month']].head(100),
        use_container_width=True
    )

st.divider()
st.caption(
    f'Inside Airbnb | Demand = reviews/month, 0-review listings excluded | '
    f'{len(demand_df):,} active listings shown'
)