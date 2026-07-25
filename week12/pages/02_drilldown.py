# pages/02_drilldown.py — drill-down page (BBD squiggle: summary → one story)
import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import load_data, sidebar_filters

df, p95 = load_data()
filtered = sidebar_filters(df, p95)  # SAME sidebar — choices carried over from page 1

st.title('Which neighbourhoods drive the premium?')
st.caption('BBD squiggle: from the market summary to one neighbourhood story')

if 'sel_hood' not in st.session_state:
    st.session_state.sel_hood = sorted(filtered['neighbourhood'].unique())[0]
st.session_state.sel_hood = st.session_state.sel_hood     # keep alive across pages

hoods_avail = sorted(filtered['neighbourhood'].unique())
if st.session_state.sel_hood not in hoods_avail:
    st.session_state.sel_hood = hoods_avail[0]

st.selectbox('Drill into a neighbourhood', hoods_avail, key='sel_hood')
hood = st.session_state.sel_hood
hood_df = filtered[filtered['neighbourhood'] == hood]

k1, k2, k3 = st.columns(3)
k1.metric('Listings', f'{len(hood_df):,}')
k2.metric('Median Price', f"£{hood_df['price'].median():.0f}/night",
          f"£{hood_df['price'].median()-filtered['price'].median():+.0f} "
          'vs filtered market')
k3.metric('Most common room type', hood_df['room_type'].mode()[0])

st.divider()

plot_df = filtered.copy()
plot_df['highlight'] = plot_df['neighbourhood'].apply(
    lambda n: hood if n == hood else 'Rest of market')

# BBD HIGHLIGHT: blue for the chosen neighbourhood, grey for everything else
# BBD CVD: blue vs grey — no red-green combination
fig = px.histogram(plot_df, x='price', color='highlight',
                   barmode='overlay', histnorm='percent', nbins=40,
                   color_discrete_map={hood: '#2E75B6', 'Rest of market': '#AAAAAA'},
                   labels={'price': 'Nightly Price (£)', 'highlight': ''},
                   title=f'{hood} vs the filtered market')
fig.update_traces(marker_line_width=0)
fig.update_layout(
    plot_bgcolor='white', paper_bgcolor='white',
    font=dict(family='Arial', size=12, color='#333333'),
    title_font=dict(family='Arial', size=16, color='#2C2C2C'),
    yaxis=dict(gridcolor='#EEEEEE', title='% of listings', automargin=True),
    xaxis=dict(showgrid=False, automargin=True),
    legend=dict(orientation='h', y=1.08, font=dict(color='#333333'))
)
st.plotly_chart(fig, use_container_width=True, theme=None)