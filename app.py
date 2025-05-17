import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="AgriShield Dashboard",
    page_icon="🌾",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('agrishield_risk_data.csv')
    return df

df = load_data()

# Sidebar filters
st.sidebar.title('🌾 AgriShield')
selected_region = st.sidebar.selectbox('Select Region', df['region'].unique())
selected_crop = st.sidebar.selectbox('Select Crop', df['crop'].unique())

# Main dashboard
st.title('Post-Harvest Loss Risk Dashboard')

# Create two columns for metrics
col1, col2, col3 = st.columns(3)

with col1:
    avg_risk = df[
        (df['region'] == selected_region) & 
        (df['crop'] == selected_crop)
    ]['risk_score'].mean()
    st.metric("Average Risk Score", f"{avg_risk:.2f}")

with col2:
    high_risk_months = df[
        (df['region'] == selected_region) & 
        (df['crop'] == selected_crop) & 
        (df['risk_category'] == 'High')
    ]['month'].nunique()
    st.metric("High Risk Months", high_risk_months)

with col3:
    current_stage = df[
        (df['region'] == selected_region) & 
        (df['crop'] == selected_crop)
    ]['crop_stage_name'].iloc[0]
    st.metric("Current Stage", current_stage)

# Create two rows for charts
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("Risk Score Timeline")
    filtered_df = df[
        (df['region'] == selected_region) & 
        (df['crop'] == selected_crop)
    ]
    fig = px.line(filtered_df, x='month', y='risk_score', 
                  markers=True, title="Monthly Risk Profile")
    st.plotly_chart(fig, use_container_width=True)

with row1_col2:
    st.subheader("Risk Factors")
    risk_factors = pd.DataFrame({
        'Factor': ['Rainy Season', 'Flood Risk', 'Lean Period'],
        'Status': [
            filtered_df['is_rainy_season'].iloc[0],
            filtered_df['flood_risk_level'].iloc[0],
            filtered_df['is_lean_period'].iloc[0]
        ]
    })
    fig = go.Figure(data=[
        go.Bar(x=risk_factors['Factor'], 
               y=risk_factors['Status'],
               marker_color=['red' if x == 1 else 'green' for x in risk_factors['Status']])
    ])
    st.plotly_chart(fig, use_container_width=True)

# Risk alerts section
st.subheader("⚠️ Risk Alerts")
high_risk_data = filtered_df[filtered_df['risk_category'] == 'High']
if not high_risk_data.empty:
    for _, row in high_risk_data.iterrows():
        st.warning(
            f"High risk of post-harvest loss for {row['crop']} in {row['month']} "
            f"due to {'rainy season' if row['is_rainy_season'] else ''} "
            f"{'flood risk' if row['flood_risk_level'] else ''} "
            f"{'lean period' if row['is_lean_period'] else ''}"
        )
else:
    st.success("No high-risk periods detected for the selected crop and region.")