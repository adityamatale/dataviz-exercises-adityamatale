import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="World Happiness", page_icon="🌍", layout="wide")

df = pd.read_csv('https://raw.githubusercontent.com/adityamatale/dataviz-exercises-adityamatale/main/data/world_happiness_2023.csv')
df.columns = ['Country','Region','Score','GDP','Social_Support',
              'Life_Expectancy','Freedom','Generosity','Corruption']

with st.sidebar:
    st.header("Filters")
    regions = ['All'] + sorted(df['Region'].unique().tolist())
    selected_region = st.selectbox("Region", regions)
    top_n = st.slider("Show top N", 5, 25, 15)

filtered = df if selected_region == 'All' else df[df['Region'] == selected_region]

st.title("🌍 World Happiness Dashboard")
st.caption("Source: World Happiness Report 2023 | Kaggle")

# KPI row
col1, col2, col3 = st.columns(3)
col1.metric("Countries", len(filtered))
col2.metric("Avg Score", f"{filtered['Score'].mean():.2f}",
            f"{filtered['Score'].mean()-df['Score'].mean():+.2f} vs global")
col3.metric("Happiest", filtered.nlargest(1,'Score')['Country'].values[0])

st.divider()

col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("Rankings")
    top = filtered.nlargest(top_n, 'Score').sort_values('Score')
    fig1 = px.bar(top, x='Score', y='Country', orientation='h',
                  color_discrete_sequence=['#2E75B6'],
                  labels={'Score':'Score (0–10)','Country':''},
                  title='Highest-ranked countries by happiness score')
    fig1.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Arial', size=12, color='#2C2C2C'),
        title_font=dict(family='Arial', size=14, color='#2C2C2C'),
        xaxis=dict(range=[0,8.5], gridcolor='#EEEEEE',
                   tickfont=dict(color='#2C2C2C')),
        yaxis=dict(showgrid=False, tickfont=dict(color='#2C2C2C')),
        margin=dict(l=120,r=30,t=55,b=60)
    )
    fig1.update_traces(marker_line_width=0)
    st.plotly_chart(fig1, width='stretch', theme=None)

with col_right:
    st.subheader("Score vs GDP")
    fig2 = px.scatter(filtered, x='GDP', y='Score', hover_name='Country',
                      color_discrete_sequence=['#E63946'],
                      title='Higher GDP tracks with higher happiness')
    fig2.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Arial', size=12, color='#2C2C2C'),
        title_font=dict(family='Arial', size=14, color='#2C2C2C'),
        xaxis=dict(gridcolor='#EEEEEE', tickfont=dict(color='#2C2C2C')),
        yaxis=dict(gridcolor='#EEEEEE', tickfont=dict(color='#2C2C2C')),
        margin=dict(l=60,r=30,t=55,b=60)
    )
    st.plotly_chart(fig2, width='stretch', theme=None)

st.divider()

# ── STEP 6: Diverging colour scale chart ──────────────────────────────────
# GDP deviation from the global average — diverging RdBu, midpoint = 0 (global avg)
st.subheader("GDP: Above vs Below Global Average")

global_avg_gdp = df['GDP'].mean()
top_gdp = filtered.nlargest(top_n, 'Score').sort_values('Score').copy()
top_gdp['GDP_vs_avg'] = top_gdp['GDP'] - global_avg_gdp

fig3 = px.bar(
    top_gdp, x='GDP_vs_avg', y='Country', orientation='h',
    color='GDP_vs_avg',
    color_continuous_scale='RdBu',
    color_continuous_midpoint=0,
    labels={'GDP_vs_avg': f'GDP vs Global Avg ({global_avg_gdp:.2f})', 'Country': ''},
    title=f'Blue = above global GDP average ({global_avg_gdp:.2f}), Red = below'
)
fig3.add_vline(
    x=0, line_dash='dash', line_color='#555555', line_width=1.5,
    annotation=dict(text='Global average', font=dict(size=11, color='#555555'),
                     xanchor='left', yanchor='top', xshift=6)
)
fig3.update_layout(
    plot_bgcolor='white', paper_bgcolor='white',
    font=dict(family='Arial', size=12, color='#2C2C2C'),
    title_font=dict(family='Arial', size=14, color='#2C2C2C'),
    xaxis=dict(tickfont=dict(color='#2C2C2C')),
    yaxis=dict(tickfont=dict(color='#2C2C2C')),
    coloraxis_showscale=False,
    margin=dict(l=120, r=40, t=65, b=60)
)
fig3.update_traces(marker_line_width=0)
st.plotly_chart(fig3, width='stretch', theme=None)

st.divider()
st.caption("Built with Streamlit + Plotly")