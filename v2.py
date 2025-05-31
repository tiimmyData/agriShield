import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import calendar
from datetime import datetime
import sys
from pathlib import Path
import json
import numpy as np
import folium
from streamlit_folium import folium_static
from folium.plugins import HeatMap
import altair as alt
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

# Add parent directory to Python path
app_dir = Path(__file__).resolve().parent
project_root = app_dir.parent
sys.path.append(str(project_root))

# Import custom modules
from database.crop_calender import crop_calendar
from database.crop_sustainability import crop_susceptibility
from database.intervention import interventions
from database.region_data import region_data
from database.seasonal_calender import (
    get_seasonal_calendar,
    get_regional_data,
    get_monthly_data,
    get_all_regions
)

# Now you can use the functions
seasonal_data = get_seasonal_calendar()
regions = get_all_regions()

# Set page config
st.set_page_config(
    page_title="AgriShield Dashboard",
    page_icon="🌾",
    layout="wide"
)

# Theme configurations
def get_theme_colors(is_dark_mode):
    if is_dark_mode:
        return {
            'bg_color': '#121212',
            'text_color': '#FFFFFF',
            'card_bg': '#1E1E1E',
            'accent': '#7289DA',
            'success': '#43B581',
            'warning': '#FAA61A',
            'danger': '#F04747',
            'chart_palette': ['#7289DA', '#43B581', '#FAA61A', '#F04747', '#B9BBBE'],
            'card_border': '#2C2F33',
            'grid_color': '#2C2F33'
        }
    else:
        return {
            'bg_color': '#F9F9F9',
            'text_color': '#333333',
            'card_bg': '#FFFFFF',
            'accent': '#4361EE',
            'success': '#4CAF50',
            'warning': '#FF9800',
            'danger': '#F44336',
            'chart_palette': ['#4361EE', '#4CAF50', '#FF9800', '#F44336', '#607D8B'],
            'card_border': '#E0E0E0',
            'grid_color': '#EEEEEE'
        }

# Get current month
current_month = datetime.now().strftime("%b")
current_month_full = datetime.now().strftime("%B")

# Create risk data based on imported modules
def generate_risk_data():
    data = []
    
    for region in crop_calendar.keys():
        region_weather = next((r for r in region_data['regions'] if r['state'] == region), None)
        
        for crop in crop_calendar[region].keys():
            crop_info = next((c for c in crop_susceptibility['crops'] if c['name'] == crop), None)
            # Fix: Call the function and then use get()
            seasonal_data = get_seasonal_calendar().get(region, {}).get('monthly_data', {})
            
            for month_idx, month in enumerate(calendar.month_abbr[1:], 1):
                month_name = calendar.month_name[month_idx]
                
                # Get seasonal data for this month
                month_seasonal = seasonal_data.get(month, {})
                is_rainy = month_seasonal.get('avg_rainfall_mm', 0) > 100
                is_harvest = month in crop_calendar[region][crop]['harvest_months']
                is_peak_loss = month in crop_calendar[region][crop]['peak_loss_months']

                # Calculate risk score (0-100)
                base_risk = 20  # Base risk
                
                if is_peak_loss:
                    base_risk += 40
                
                if is_rainy:
                    base_risk += 20
                
                if is_harvest:
                    base_risk += 10
                
                # Adjust based on crop shelf life
                if crop_info:
                    if crop_info['shelf_life_days'] < 7:  # Highly perishable
                        base_risk += 10
                
                # Risk category
                risk_category = "Low"
                if base_risk > 70:
                    risk_category = "High"
                elif base_risk > 40:
                    risk_category = "Medium"
                
                # Determine current crop stage
                crop_stage = "Off-season"
                if month in crop_calendar[region][crop]['planting_months']:
                    crop_stage = "Planting"
                elif month in crop_calendar[region][crop]['harvest_months']:
                    crop_stage = "Harvest"
                elif is_peak_loss:
                    crop_stage = "Post-harvest"
                
                # Determine if this is a lean period (when food stocks are traditionally low)
                # Generally, just before new harvest comes in
                is_lean = False
                if month_idx > 0 and month_idx < 12:
                    next_month = calendar.month_abbr[month_idx + 1]
                    if next_month in crop_calendar[region][crop]['harvest_months']:
                        is_lean = True
                
                # Get flood risk based on rainfall
                flood_risk = 0
                if month_seasonal.get('avg_rainfall_mm', 0) > 200:
                    flood_risk = 1
                
                # Transport access risk (new)
                transport_risk = 0
                if region_weather and 'transport_accessibility' in region_weather:
                    if region_weather['transport_accessibility'] < 0.5:  # Low accessibility
                        transport_risk = 1
                
                # Calculate economic impact based on risk score and crop value
                crop_value = crop_info.get('market_value', 100) if crop_info else 100  # Default value
                economic_impact = (base_risk / 100) * crop_value * crop_calendar[region][crop]['historical_loss_percentage'] / 100
                
                # Calculate potential savings with interventions
                potential_savings = economic_impact * 0.7  # Assume interventions can save 70% of losses
                
                data.append({
                    'region': region,
                    'crop': crop,
                    'month': month,
                    'month_name': month_name,
                    'risk_score': base_risk,
                    'risk_category': risk_category,
                    'is_rainy_season': 1 if is_rainy else 0,
                    'is_lean_period': 1 if is_lean else 0,
                    'flood_risk_level': flood_risk,
                    'transport_risk': transport_risk,
                    'crop_stage_name': crop_stage,
                    'historical_loss_percentage': crop_calendar[region][crop]['historical_loss_percentage'],
                    'economic_impact': economic_impact,
                    'potential_savings': potential_savings,
                    'lat': region_weather['latitude'] if region_weather else 9.0820,  # Default Nigeria latitude
                    'long': region_weather['longitude'] if region_weather else 8.6753  # Default Nigeria longitude
                })
    
    return pd.DataFrame(data)

# Load data
@st.cache_data
def load_data():
    # In a real application, this would load from CSV
    # For this demo, we'll generate it from our modules
    df = generate_risk_data()
    # Optionally save to CSV for potential future use
    # df.to_csv('agrishield_risk_data.csv', index=False)
    return df

df = load_data()

# Custom CSS for better styling
def apply_custom_css(theme):
    st.markdown(f"""
    <style>
    .main {{
        background-color: {theme['bg_color']};
        color: {theme['text_color']};
    }}
    .css-1d391kg {{
        background-color: {theme['bg_color']};
    }}
    .stSidebar {{
        background-color: {theme['card_bg']};
    }}
    .card {{
        background-color: {theme['card_bg']};
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px solid {theme['card_border']};
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }}
    .metric-container {{
        background-color: {theme['card_bg']};
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        border: 1px solid {theme['card_border']};
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }}
    .metric-value {{
        font-size: 24px;
        font-weight: bold;
        color: {theme['accent']};
    }}
    .metric-label {{
        font-size: 14px;
        color: {theme['text_color']};
        opacity: 0.8;
    }}
    .high-risk {{
        color: {theme['danger']};
    }}
    .medium-risk {{
        color: {theme['warning']};
    }}
    .low-risk {{
        color: {theme['success']};
    }}
    .tooltip {{
        position: relative;
        display: inline-block;
        border-bottom: 1px dotted {theme['accent']};
    }}
    .tooltip .tooltiptext {{
        visibility: hidden;
        width: 200px;
        background-color: {theme['card_bg']};
        color: {theme['text_color']};
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
        border: 1px solid {theme['card_border']};
    }}
    .tooltip:hover .tooltiptext {{
        visibility: visible;
        opacity: 1;
    }}
    .risk-alert {{
        background-color: rgba(244, 67, 54, 0.1);
        border-left: 4px solid {theme['danger']};
        padding: 10px 15px;
        margin-bottom: 10px;
        border-radius: 4px;
    }}
    .success-alert {{
        background-color: rgba(76, 175, 80, 0.1);
        border-left: 4px solid {theme['success']};
        padding: 10px 15px;
        margin-bottom: 10px;
        border-radius: 4px;
    }}
    .info-alert {{
        background-color: rgba(33, 150, 243, 0.1);
        border-left: 4px solid {theme['accent']};
        padding: 10px 15px;
        margin-bottom: 10px;
        border-radius: 4px;
    }}
    .tab {{
        border-radius: 5px 5px 0 0;
        padding: 10px 15px;
        margin-right: 5px;
        background-color: {theme['card_bg']};
        cursor: pointer;
        border: 1px solid {theme['card_border']};
        border-bottom: none;
    }}
    .tab-active {{
        background-color: {theme['accent']};
        color: white;
    }}
    .progress-container {{
        width: 100%;
        background-color: {theme['card_bg']};
        border-radius: 5px;
        margin-bottom: 10px;
    }}
    .progress-bar {{
        height: 8px;
        border-radius: 5px;
    }}
    .status-indicator {{
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 5px;
    }}
    </style>
    """, unsafe_allow_html=True)

# Sidebar content
def render_sidebar(theme):
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/placeholder/agrishield/main/assets/logo.png", width=200)
        st.title('🌾 AgriShield')
        st.subheader('Post-Harvest Loss Prevention')
        
        # Theme toggle
        is_dark_mode = st.toggle('Dark Mode', value=True)
        
        # Help button with tooltip
        st.markdown("""
        <div class="tooltip">Need Help?
            <span class="tooltiptext">Click the ? icon next to any section for more information</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Dashboard navigation
        st.subheader("Navigation")
        selected_page = st.radio("", ["Risk Dashboard", "Intervention Planner", "Market Intel", "Settings"], index=0)
        
        st.markdown("---")
        
        # Filters
        st.subheader("Filter Options")
        selected_region = st.selectbox('Select Region', df['region'].unique())
        selected_crop = st.selectbox('Select Crop', df[df['region'] == selected_region]['crop'].unique())
        
        # Time filter
        st.subheader("Time Period")
        time_period = st.select_slider(
            "Select Month Range",
            options=calendar.month_abbr[1:],
            value=(current_month, current_month)
        )
        
        # Risk threshold
        st.subheader("Risk Threshold")
        risk_threshold = st.slider("Minimum Risk Score to Display", 0, 100, 40)
        
        st.markdown("---")
        
        # User profile
        st.subheader("User Profile")
        st.markdown(f"""
        <div class="card">
            <div style="display: flex; align-items: center;">
                <div style="margin-right: 10px;">👤</div>
                <div>
                    <div style="font-weight: bold;">Adebayo Olukoya</div>
                    <div style="font-size: 12px;">Agricultural Officer, Oyo State</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick stats
        st.subheader("Quick Stats")
        current_month_data = df[
            (df['region'] == selected_region) & 
            (df['crop'] == selected_crop) &
            (df['month'] == current_month)
        ]
        
        if not current_month_data.empty:
            risk_score = current_month_data['risk_score'].iloc[0]
            risk_category = current_month_data['risk_category'].iloc[0]
            
            risk_color = theme['success']
            if risk_category == 'High':
                risk_color = theme['danger']
            elif risk_category == 'Medium':
                risk_color = theme['warning']
            
            st.markdown(f"""
            <div class="card">
                <div style="font-size: 12px;">Current Risk</div>
                <div style="font-size: 24px; font-weight: bold; color: {risk_color};">{risk_score:.1f}/100</div>
                <div style="font-size: 14px;">Category: {risk_category}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # SMS Notification status
        st.markdown(f"""
        <div class="card">
            <div style="font-size: 14px;">SMS Notifications</div>
            <div style="display: flex; align-items: center;">
                <div class="status-indicator" style="background-color: {theme['success']};"></div>
                <div>Active - 245 farmers registered</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    return selected_region, selected_crop, time_period, risk_threshold, is_dark_mode, selected_page

# Render main dashboard components
def render_risk_dashboard(selected_region, selected_crop, theme, df):
    st.title('Post-Harvest Loss Risk Dashboard')
    st.markdown(f"""
    <div style="display: flex; align-items: center;">
        <div style="margin-right: 10px; font-size: 18px;">📅</div>
        <div>
            <div style="font-weight: bold; font-size: 18px;">{current_month_full} 2025</div>
            <div style="font-size: 14px;">Last updated: May 20, 2025</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Filter data
    filtered_df = df[
        (df['region'] == selected_region) & 
        (df['crop'] == selected_crop)
    ]
    
    current_month_data = filtered_df[filtered_df['month'] == current_month]
    
    with col1:
        avg_risk = filtered_df['risk_score'].mean()
        
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">
                <div class="tooltip">Average Risk Score
                    <span class="tooltiptext">Average risk score across all months</span>
                </div>
            </div>
            <div class="metric-value">{avg_risk:.1f}/100</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        high_risk_months = filtered_df[filtered_df['risk_category'] == 'High']['month'].nunique()
        
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">
                <div class="tooltip">High Risk Months
                    <span class="tooltiptext">Number of months with high risk score</span>
                </div>
            </div>
            <div class="metric-value">{high_risk_months}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        if not current_month_data.empty:
            current_stage = current_month_data['crop_stage_name'].iloc[0]
            
            stage_color = theme['text_color']
            if current_stage == "Harvest":
                stage_color = theme['success']
            elif current_stage == "Post-harvest":
                stage_color = theme['warning']
            
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">
                    <div class="tooltip">Current Crop Stage
                        <span class="tooltiptext">The current growth stage of the selected crop</span>
                    </div>
                </div>
                <div class="metric-value" style="color: {stage_color};">{current_stage}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Current Crop Stage</div>
                <div class="metric-value">Unknown</div>
            </div>
            """, unsafe_allow_html=True)

    with col4:
        historical_loss = filtered_df['historical_loss_percentage'].mean()
        
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">
                <div class="tooltip">Historical Loss %
                    <span class="tooltiptext">Average percentage of crop lost post-harvest historically</span>
                </div>
            </div>
            <div class="metric-value">{historical_loss:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Interactive Risk Map
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <h3>📍 Regional Risk Map</h3>
        <div class="tooltip">ℹ️
            <span class="tooltiptext">View the regional risk distribution on the map</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create map data
    map_data = df[
        (df['crop'] == selected_crop) &
        (df['month'] == current_month)
    ]
    
    # Create folium map
    m = folium.Map(location=[9.0820, 8.6753], zoom_start=6, tiles="CartoDB positron")
    
    # Add markers for each region
    for _, row in map_data.iterrows():
        # Determine color based on risk category
        if row['risk_category'] == 'High':
            color = 'red'
        elif row['risk_category'] == 'Medium':
            color = 'orange'
        else:
            color = 'green'
        
        # Create popup content
        popup_content = f"""
        <div style="width: 200px;">
            <h4>{row['region']}</h4>
            <p><b>Crop:</b> {row['crop']}</p>
            <p><b>Risk Score:</b> {row['risk_score']:.1f}/100</p>
            <p><b>Risk Level:</b> {row['risk_category']}</p>
            <p><b>Current Stage:</b> {row['crop_stage_name']}</p>
        </div>
        """
        
        # Add marker to map
        folium.Marker(
            location=[row['lat'], row['long']],
            popup=folium.Popup(popup_content, max_width=300),
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(m)
    
    # Display the map
    folium_static(m, width=1200, height=500)
    
    # Create two rows for detailed charts
    st.markdown("<h3>📊 Risk Analytics</h3>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Risk Timeline", "Risk Factors", "Economic Impact"])
    
    with tab1:
        # Risk Timeline Chart
        st.subheader("Risk Score Timeline")
        
        # Create a more interactive chart with Plotly
        fig = px.line(filtered_df, x='month', y='risk_score', 
                      markers=True, 
                      labels={"risk_score": "Risk Score (0-100)", "month": "Month"},
                      color_discrete_sequence=[theme['accent']])
        
        # Add risk zones
        fig.add_shape(
            type="rect",
            x0=filtered_df['month'].min(),
            x1=filtered_df['month'].max(),
            y0=70,
            y1=100,
            fillcolor="rgba(244, 67, 54, 0.2)",
            line=dict(width=0),
            layer="below"
        )
        
        fig.add_shape(
            type="rect",
            x0=filtered_df['month'].min(),
            x1=filtered_df['month'].max(),
            y0=40,
            y1=70,
            fillcolor="rgba(255, 152, 0, 0.2)",
            line=dict(width=0),
            layer="below"
        )
        
        # Add annotations
        fig.add_annotation(
            x=0.95,
            y=85,
            xref="paper",
            yref="y",
            text="High Risk",
            showarrow=False,
            font=dict(color="red")
        )
        
        fig.add_annotation(
            x=0.95,
            y=55,
            xref="paper",
            yref="y",
            text="Medium Risk",
            showarrow=False,
            font=dict(color="orange")
        )
        
        # Highlight current month
        if not current_month_data.empty:
            fig.add_trace(
                go.Scatter(
                    x=[current_month],
                    y=[current_month_data['risk_score'].iloc[0]],
                    mode='markers',
                    marker=dict(color='red', size=12),
                    name='Current Month'
                )
            )
        
        # Update layout for better appearance
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor=theme['grid_color'],
                tickmode='array',
                tickvals=filtered_df['month'].tolist()
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=theme['grid_color'],
                range=[0, 100]
            ),
            font=dict(color=theme['text_color'])
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add interactive risk breakdown
        st.markdown("### Risk Breakdown by Month")
        selected_month = st.select_slider(
            "Select Month for Detailed Analysis",
            options=calendar.month_abbr[1:],
            value=current_month
        )
        
        # Get data for selected month
        month_data = filtered_df[filtered_df['month'] == selected_month]
        
        if not month_data.empty:
            month_risk = month_data['risk_score'].iloc[0]
            month_risk_category = month_data['risk_category'].iloc[0]
            
            # Create a breakdown of risk factors
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown(f"### {selected_month} Risk Analysis")
                st.markdown(f"""
                <div class="card">
                    <div style="font-size: 18px; margin-bottom: 10px;">Risk Score: {month_risk:.1f}/100</div>
                    <div style="font-size: 16px; margin-bottom: 5px;">Category: 
                        <span class="{month_risk_category.lower()}-risk">{month_risk_category}</span>
                    </div>
                    <div style="font-size: 14px;">Crop Stage: {month_data['crop_stage_name'].iloc[0]}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Create a radar chart for risk factors
                categories = ['Rainy Season', 'Flood Risk', 'Lean Period', 'Transport Risk']
                values = [
                    month_data['is_rainy_season'].iloc[0] * 100,
                    month_data['flood_risk_level'].iloc[0] * 100,
                    month_data['is_lean_period'].iloc[0] * 100,
                    month_data['transport_risk'].iloc[0] * 100
                ]
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    name='Risk Factors',
                    line_color=theme['accent']
                ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )
                    ),
                    showlegend=False,
                    margin=dict(l=40, r=40, t=40, b=40),
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=theme['text_color'])
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Risk Factors Analysis")
        
        # Create a heatmap for risk factors across months
        risk_factors_data = {
            'Month': [],
            'Rainy Season': [],
            'Flood Risk': [],
            'Lean Period': [],
            'Transport Risk': []
        }
        
        for _, row in filtered_df.iterrows():
            risk_factors_data['Month'].append(row['month'])
            risk_factors_data['Rainy Season'].append(row['is_rainy_season'])
            risk_factors_data['Flood Risk'].append(row['flood_risk_level'])
            risk_factors_data['Lean Period'].append(row['is_lean_period'])
            risk_factors_data['Transport Risk'].append(row['transport_risk'])
        
        risk_factors_df = pd.DataFrame(risk_factors_data)
        risk_factors_pivot = risk_factors_df.set_index('Month')
        
        # Create heatmap with Plotly
        fig = px.imshow(risk_factors_pivot.T,
                        x=risk_factors_pivot.index,
                        y=risk_factors_pivot.columns,
                        color_continuous_scale=[[0, 'green'], [1, 'red']],
                        labels=dict(x="Month", y="Risk Factor", color="Present"))
        
        fig.update_layout(
            margin=dict(l=40, r=40, t=40, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=theme['text_color'])
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add correlation analysis
        st.subheader("Risk Factor Impact Analysis")
        
        # Create a scatter plot to show correlation between risk factors and total risk
        factor_analysis = pd.DataFrame({
            'Rainy Season': [0, 1],
            'Flood Risk': [0, 1],
            'Lean Period': [0, 1],
            'Transport Risk': [0, 1],
            'Average Risk Score': [
                filtered_df[filtered_df['is_rainy_season'] == 0]['risk_score'].mean(),
                filtered_df[filtered_df['is_rainy_season'] == 1]['risk_score'].mean()
            ]
        })
        
        fig = px.bar(
            x=['Rainy Season', 'Flood Risk', 'Lean Period', 'Transport Risk'],
            y=[
                filtered_df[filtered_df['is_rainy_season'] == 1]['risk_score'].mean() - 
                filtered_df[filtered_df['is_rainy_season'] == 0]['risk_score'].mean(),
                
                filtered_df[filtered_df['flood_risk_level'] == 1]['risk_score'].mean() - 
                filtered_df[filtered_df['flood_risk_level'] == 0]['risk_score'].mean(),
                
                filtered_df[filtered_df['is_lean_period'] == 1]['risk_score'].mean() - 
                filtered_df[filtered_df['is_lean_period'] == 0]['risk_score'].mean(),
                
                filtered_df[filtered_df['transport_risk'] == 1]['risk_score'].mean() - 
                filtered_df[filtered_df['transport_risk'] == 0]['risk_score'].mean()
            ],
            title="Risk Factor Impact on Risk Score",
            labels={"x": "Risk Factor", "y": "Increase in Risk Score"},
            color_discrete_sequence=[theme['accent']]
        )
        
        fig.update_layout(
            margin=dict(l=40, r=40, t=40, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=theme['text_color'])
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add explanation
        st.markdown("""
        <div class="info-alert">
        <strong>Impact Analysis:</strong> This chart shows how much each risk factor increases the overall risk score when present.
        Higher values indicate factors that have more influence on crop loss risk.
        </div>
        """, unsafe_allow_html=True)
    
    with tab3:
        st.subheader("Economic Impact Analysis")
        
        # Create economic impact visualization
        economic_data = filtered_df[['month', 'risk_score', 'economic_impact', 'potential_savings']]
        
        # Total projected losses
        total_loss = economic_data['economic_impact'].sum()
        potential_savings = economic_data['potential_savings'].sum()
        
        # Create metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Projected Annual Loss</div>
                <div class="metric-value" style="color: {theme['danger']};">₦{total_loss:,.2f}M</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Potential Savings with Interventions</div>
                <div class="metric-value" style="color: {theme['success']};">₦{potential_savings:,.2f}M</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            roi = potential_savings / (potential_savings * 0.3) if potential_savings > 0 else 0
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Estimated ROI on Interventions</div>
                <div class="metric-value" style="color: {theme['accent']};">{roi:.1f}x</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Create economic impact chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=economic_data['month'],
            y=economic_data['economic_impact'],
            name='Projected Loss',
            marker_color=theme['danger']
        ))
        
        fig.add_trace(go.Bar(
            x=economic_data['month'],
            y=economic_data['potential_savings'],
            name='Potential Savings',
            marker_color=theme['success']
        ))
        
        fig.update_layout(
            barmode='group',
            title="Monthly Economic Impact (in ₦ Million)",
            xaxis_title="Month",
            yaxis_title="Economic Value (₦ Million)",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=40, r=40, t=60, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=theme['text_color'])
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add interactive ROI calculator
        st.subheader("Intervention ROI Calculator")
        
        col1, col2 = st.columns(2)
        
        with col1:
            intervention_cost = st.number_input(
                "Estimated Intervention Cost (₦ Million)",
                min_value=0.1,
                max_value=100.0,
                value=potential_savings * 0.3,
                step=0.1
            )
            
            effectiveness_rate = st.slider(
                "Intervention Effectiveness Rate (%)",
                min_value=10,
                max_value=100,
                value=70,
                step=5
            )
        
        with col2:
            calculated_savings = total_loss * effectiveness_rate / 100
            calculated_roi = calculated_savings / intervention_cost if intervention_cost > 0 else 0
            
            st.markdown(f"""
            <div class="card" style="height: 100%;">
                <h4>ROI Analysis Results</h4>
                <div style="margin-top: 20px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <div>Estimated Savings:</div>
                        <div style="font-weight: bold;">₦{calculated_savings:,.2f}M</div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <div>Return on Investment:</div>
                        <div style="font-weight: bold;">{calculated_roi:.2f}x</div>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <div>Payback Period:</div>
                        <div style="font-weight: bold;">{12/calculated_roi:.1f} months</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Risk alerts section
    st.markdown("<h3>⚠️ Risk Alerts</h3>", unsafe_allow_html=True)
    
    high_risk_data = filtered_df[filtered_df['risk_category'] == 'High']
    if not high_risk_data.empty:
        for _, row in high_risk_data.iterrows():
            risk_factors = []
            if row['is_rainy_season'] == 1:
                risk_factors.append("rainy season")
            if row['flood_risk_level'] == 1:
                risk_factors.append("flood risk")
            if row['is_lean_period'] == 1:
                risk_factors.append("lean period")
            if row['transport_risk'] == 1:
                risk_factors.append("transport accessibility issues")
            
            risk_factors_text = ", ".join(risk_factors) if risk_factors else "multiple factors"
            
            st.markdown(f"""
            <div class="risk-alert">
                <div style="display: flex; align-items: center;">
                    <div style="margin-right: 10px; font-size: 24px;">⚠️</div>
                    <div>
                        <div style="font-weight: bold; font-size: 16px;">High Risk Alert: {row['month_name']}</div>
                        <div>
                            High risk of post-harvest loss for {row['crop']} in {row['month_name']} 
                            due to {risk_factors_text}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="success-alert">
            <div style="display: flex; align-items: center;">
                <div style="margin-right: 10px; font-size: 24px;">✅</div>
                <div>
                    <div style="font-weight: bold; font-size: 16px;">No High Risk Periods</div>
                    <div>No high-risk periods detected for the selected crop and region.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Intervention recommendations
    st.markdown("<h3>🛡️ Recommended Interventions</h3>", unsafe_allow_html=True)
    
    # Get the selected crop's susceptibility information
    crop_info = next((c for c in crop_susceptibility['crops'] if c['name'] == selected_crop), None)
    crop_interventions = interventions.get(selected_crop, {})
    
    if crop_interventions:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"""
            <div class="card">
                <h4>High Risk Conditions</h4>
                <p>{crop_interventions['high_risk_conditions']}</p>
                
                <h4>Recommended Actions</h4>
                <ul>
            """, unsafe_allow_html=True)
            
            for action in crop_interventions['recommended_actions']:
                st.markdown(f"<li>{action}</li>", unsafe_allow_html=True)
            
            st.markdown("</ul></div>", unsafe_allow_html=True)
        
        with col2:
            # Add SMS template for farmers
            st.markdown(f"""
            <div class="card">
                <h4>SMS Alert Template</h4>
                <div style="background-color: {theme['bg_color']}; padding: 15px; border-radius: 5px; border: 1px solid {theme['card_border']};">
                    <p style="font-family: monospace; font-size: 14px;">
                    ⚠️ {selected_crop} in {selected_region} at {current_month_data['risk_category'].iloc[0] if not current_month_data.empty else 'Medium'} risk.
                    {crop_interventions['recommended_actions'][0] if crop_interventions['recommended_actions'] else 'Use recommended practices'}.
                    Contact AgriShield: 080-XXX-XXXX for help.
                    </p>
                </div>
                <div style="margin-top: 10px; text-align: right;">
                    <button style="background-color: {theme['accent']}; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer;">
                        Send Test
                    </button>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info(f"No specific intervention recommendations available for {selected_crop}")
    
    # Add Interactive Report Generation
    st.markdown("<h3>📊 Report Generation</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        report_type = st.selectbox(
            "Report Type",
            ["Risk Assessment", "Intervention Plan", "Economic Analysis"]
        )
    
    with col2:
        report_format = st.selectbox(
            "Format",
            ["PDF", "Excel", "CSV"]
        )
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("Generate Report", type="primary")
    
    # Add section for tracking SMS delivery status
    st.markdown("<h3>📱 SMS Advisory Status</h3>", unsafe_allow_html=True)
    
    # Create SMS delivery status data
    sms_data = {
        'Date': ['May 20, 2025', 'May 13, 2025', 'May 6, 2025', 'Apr 29, 2025', 'Apr 22, 2025'],
        'Recipients': [245, 243, 240, 238, 230],
        'Delivered': [240, 238, 235, 232, 225],
        'Read': [210, 200, 205, 198, 190],
        'Actions Taken': [85, 82, 80, 75, 72]
    }
    
    sms_df = pd.DataFrame(sms_data)
    
    # Create columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create delivery metrics
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=sms_df['Date'],
            y=sms_df['Recipients'],
            mode='lines+markers',
            name='Recipients',
            marker_color=theme['accent']
        ))
        
        fig.add_trace(go.Scatter(
            x=sms_df['Date'],
            y=sms_df['Delivered'],
            mode='lines+markers',
            name='Delivered',
            marker_color=theme['success']
        ))
        
        fig.add_trace(go.Scatter(
            x=sms_df['Date'],
            y=sms_df['Read'],
            mode='lines+markers',
            name='Read',
            marker_color=theme['warning']
        ))
        
        fig.add_trace(go.Scatter(
            x=sms_df['Date'],
            y=sms_df['Actions Taken'],
            mode='lines+markers',
            name='Actions Taken',
            marker_color=theme['danger']
        ))
        
        fig.update_layout(
            title="SMS Advisory Metrics",
            xaxis_title="Date",
            yaxis_title="Count",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=40, r=40, t=60, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=theme['text_color'])
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Add action rate metrics
        latest = sms_df.iloc[0]
        action_rate = (latest['Actions Taken'] / latest['Delivered']) * 100
        
        st.markdown(f"""
        <div class="card">
            <h4>Latest SMS Campaign</h4>
            <div style="margin-top: 20px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <div>Date:</div>
                    <div style="font-weight: bold;">{latest['Date']}</div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <div>Delivery Rate:</div>
                    <div style="font-weight: bold;">{(latest['Delivered']/latest['Recipients'])*100:.1f}%</div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <div>Read Rate:</div>
                    <div style="font-weight: bold;">{(latest['Read']/latest['Delivered'])*100:.1f}%</div>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <div>Action Rate:</div>
                    <div style="font-weight: bold;">{action_rate:.1f}%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_intervention_planner(selected_region, selected_crop, theme, df):
    st.title('Intervention Planner')
    st.markdown("Plan and track your post-harvest loss interventions")
    
    # Get the selected crop's interventions
    crop_interventions = interventions.get(selected_crop, {})
    
    if not crop_interventions:
        st.warning(f"No specific interventions available for {selected_crop}")
        return
    
    # Create columns for intervention planner
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Available Interventions")
        
        # Create intervention cards
        for i, action in enumerate(crop_interventions.get('recommended_actions', [])):
            effectiveness = [70, 60, 80, 50, 75][min(i, 4)]  # Sample effectiveness ratings
            cost_level = ["$", "$", "$$", "$", "$"][min(i, 4)]  # Sample cost levels
            
            st.markdown(f"""
            <div class="card" style="cursor: pointer;" onclick="alert('Intervention selected!')">
                <div style="display: flex; justify-content: space-between;">
                    <div style="font-weight: bold;">{action.split('.')[0]}</div>
                    <div style="color: {theme['accent']};">{cost_level}</div>
                </div>
                <div style="margin-top: 10px; font-size: 14px;">
                    {action}
                </div>
                <div style="margin-top: 10px;">
                    <div style="font-size: 12px;">Effectiveness</div>
                    <div class="progress-container">
                        <div class="progress-bar" style="width: {effectiveness}%; background-color: {theme['success']};"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 12px;">
                        <div>Low</div>
                        <div>{effectiveness}%</div>
                        <div>High</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("Intervention Planner")
        
        # Create tabs for different planning views
        plan_tab1, plan_tab2 = st.tabs(["Timeline View", "Calendar View"])
        
        with plan_tab1:
            # Create a Gantt-like chart for intervention planning
            intervention_data = {
                'Task': ['Pre-harvest', 'Harvest preparation', 'Harvesting', 'Post-harvest handling', 'Storage preparation'],
                'Start': ['May 1', 'May 10', 'May 20', 'May 25', 'Jun 5'],
                'End': ['May 10', 'May 20', 'May 25', 'Jun 5', 'Jun 15'],
                'Status': ['Completed', 'Completed', 'In Progress', 'Planned', 'Planned']
            }
            
            # Convert to DataFrame
            intervention_df = pd.DataFrame(intervention_data)
            
            # Create a figure
            fig = go.Figure()
            
            # Add tasks to the chart
            for i, task in enumerate(intervention_df['Task']):
                start_date = pd.to_datetime(intervention_df['Start'][i])
                end_date = pd.to_datetime(intervention_df['End'][i])
                
                # Determine color based on status
                color = theme['success']
                if intervention_df['Status'][i] == 'In Progress':
                    color = theme['warning']
                elif intervention_df['Status'][i] == 'Planned':
                    color = theme['accent']
                
                # Add task bar
                fig.add_trace(go.Bar(
                    x=[end_date - start_date],
                    y=[task],
                    orientation='h',
                    marker=dict(color=color),
                    text=intervention_df['Status'][i],
                    textposition='inside',
                    hoverinfo='text',
                    hovertext=f"{task}: {intervention_df['Start'][i]} to {intervention_df['End'][i]}<br>Status: {intervention_df['Status'][i]}"
                ))
            
            # Update layout
            fig.update_layout(
                title="Intervention Timeline",
                xaxis=dict(
                    title="Timeline",
                    tickformat="%b %d",
                    showgrid=True,
                    gridcolor=theme['grid_color']
                ),
                yaxis=dict(
                    title="Intervention",
                    autorange="reversed"
                ),
                height=400,
                margin=dict(l=40, r=40, t=60, b=40),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=theme['text_color'])
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.button("➕ Add Intervention")
            
            with col2:
                st.button("📅 Schedule")
            
            with col3:
                st.button("✏️ Edit Timeline")
        
        with plan_tab2:
            st.markdown("### Monthly Calendar View")
            st.info("Calendar view feature coming soon")

def render_market_intel(selected_region, selected_crop, theme, df):
    st.title('Market Intelligence')
    st.markdown("Market trends, prices, and supply chain analytics")
    
    # Create tabs for different market views
    market_tab1, market_tab2, market_tab3 = st.tabs(["Price Trends", "Supply Chain", "Buyer Connect"])
    
    with market_tab1:
        st.subheader("Price Trends")
        
        # Create sample price data
        months = calendar.month_abbr[1:]
        price_data = {
            'Month': months,
            'Farm Gate': [120, 115, 110, 105, 100, 95, 100, 110, 120, 130, 135, 125],
            'Wholesale': [150, 145, 140, 135, 130, 125, 130, 140, 150, 160, 165, 155],
            'Retail': [180, 175, 170, 165, 160, 155, 160, 170, 180, 190, 195, 185]
        }
        
        price_df = pd.DataFrame(price_data)
        
        # Create price trend chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=price_df['Month'],
            y=price_df['Farm Gate'],
            mode='lines+markers',
            name='Farm Gate',
            marker_color=theme['success']
        ))
        
        fig.add_trace(go.Scatter(
            x=price_df['Month'],
            y=price_df['Wholesale'],
            mode='lines+markers',
            name='Wholesale',
            marker_color=theme['warning']
        ))
        
        fig.add_trace(go.Scatter(
            x=price_df['Month'],
            y=price_df['Retail'],
            mode='lines+markers',
            name='Retail',
            marker_color=theme['danger']
        ))
        
        # Update layout
        fig.update_layout(
            title=f"{selected_crop} Price Trends in {selected_region} (₦ per kg)",
            xaxis_title="Month",
            yaxis_title="Price (₦ per kg)",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=40, r=40, t=60, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=theme['text_color'])
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add price spread analysis
        st.subheader("Price Spread Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Calculate price spreads
            price_df['Wholesale-Farm Spread'] = price_df['Wholesale'] - price_df['Farm Gate']
            price_df['Retail-Wholesale Spread'] = price_df['Retail'] - price_df['Wholesale']
            
            # Create spread chart
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=price_df['Month'],
                y=price_df['Wholesale-Farm Spread'],
                name='Wholesale-Farm Spread',
                marker_color=theme['accent']
            ))
            
            fig.add_trace(go.Bar(
                x=price_df['Month'],
                y=price_df['Retail-Wholesale Spread'],
                name='Retail-Wholesale Spread',
                marker_color=theme['danger']
            ))
            
            # Update layout
            fig.update_layout(
                title="Price Spreads Across Supply Chain",
                xaxis_title="Month",
                yaxis_title="Price Spread (₦)",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                margin=dict(l=40, r=40, t=60, b=40),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=theme['text_color'])
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Add price volatility metrics
            current_price = price_df.iloc[-1]['Farm Gate']
            avg_price = price_df['Farm Gate'].mean()
            max_price = price_df['Farm Gate'].max()
            min_price = price_df['Farm Gate'].min()
            volatility = price_df['Farm Gate'].std() / avg_price * 100
            
            st.markdown(f"""
            <div class="card">
                <h4>Price Volatility Metrics</h4>
                <div style="margin-top: 20px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <div>Current Farm Gate Price:</div>
                        <div style="font-weight: bold;">₦{current_price:.2f}/kg</div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <div>Average Price (12 months):</div>
                        <div style="font-weight: bold;">₦{avg_price:.2f}/kg</div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <div>Price Range:</div>
                        <div style="font-weight: bold;">₦{min_price:.2f} - ₦{max_price:.2f}/kg</div>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <div>Price Volatility:</div>
                        <div style="font-weight: bold;">{volatility:.1f}%</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Add price forecasting
            st.markdown(f"""
            <div class="card">
                <h4>Price Forecast</h4>
                <div style="margin-top: 20px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <div>Next Month Forecast:</div>
                        <div style="font-weight: bold;">₦{current_price * 1.05:.2f}/kg</div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <div>3-Month Forecast:</div>
                        <div style="font-weight: bold;">₦{current_price * 1.10:.2f}/kg</div>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <div>Forecast Confidence:</div>
                        <div style="font-weight: bold;">75%</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with market_tab2:
        st.subheader("Supply Chain Analysis")
        
        # Create sample supply chain data
        supply_chain_data = {
            'Stage': ['Farmer', 'Aggregator', 'Processor', 'Distributor', 'Retailer'],
            'Loss (%)': [8, 5, 3, 2, 2],
            'Value Add (%)': [0, 15, 25, 10, 20],
            'Days': [1, 2, 3, 2, 5]
        }
        
        supply_chain_df = pd.DataFrame(supply_chain_data)
        
        # Create supply chain visualization
        fig = go.Figure()
        
        # Add loss bars
        fig.add_trace(go.Bar(
            x=supply_chain_df['Stage'],
            y=supply_chain_df['Loss (%)'],
            name='Loss (%)',
            marker_color=theme['danger']
        ))
        
        # Add value add line
        fig.add_trace(go.Scatter(
            x=supply_chain_df['Stage'],
            y=supply_chain_df['Value Add (%)'],
            mode='lines+markers',
            name='Value Add (%)',
            marker_color=theme['success'],
            yaxis='y2'
        ))
        
        # Update layout
        fig.update_layout(
            title="Supply Chain Analysis",
            xaxis_title="Supply Chain Stage",
            yaxis=dict(
                title="Loss (%)",
                side='left',
                range=[0, 10]
            ),
            yaxis2=dict(
                title="Value Add (%)",
                side='right',
                overlaying='y',
                range=[0, 30]
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=40, r=40, t=60, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=theme['text_color'])
        )
        
        st.plotly_chart(fig, use_container_width=True)
        # ...existing code...

    with market_tab3:
        st.subheader("Buyer Connect")
        
        # Create sample buyer data
        buyers_data = {
            'Buyer': ['Lagos Wholesale Market', 'Fresh Foods Ltd', 'AgriProcess Nigeria', 'Export Connect'],
            'Type': ['Wholesale Market', 'Retail Chain', 'Processor', 'Exporter'],
            'Min_Volume': [1000, 500, 2000, 5000],
            'Price_Range': ['110-120', '115-125', '105-115', '120-130'],
            'Requirements': ['Grade A, Clean', 'Packaged, Grade A', 'All Grades', 'Export Quality']
        }
        
        buyers_df = pd.DataFrame(buyers_data)
        
        # Display buyer opportunities
        st.markdown("""
        <div class="info-alert">
            Available buying opportunities for your region and crop
        </div>
        """, unsafe_allow_html=True)
        
        for _, buyer in buyers_df.iterrows():
            st.markdown(f"""
            <div class="card">
                <div style="display: flex; justify-content: space-between;">
                    <div>
                        <h4>{buyer['Buyer']}</h4>
                        <div style="font-size: 14px; color: {theme['accent']};">{buyer['Type']}</div>
                    </div>
                    <div>
                        <button style="background-color: {theme['accent']}; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer;">
                            Contact
                        </button>
                    </div>
                </div>
                <div style="margin-top: 10px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <div>Minimum Volume:</div>
                        <div>{buyer['Min_Volume']} kg</div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <div>Price Range (₦/kg):</div>
                        <div>{buyer['Price_Range']}</div>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <div>Requirements:</div>
                        <div>{buyer['Requirements']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Main app execution
def main():
    # Get theme colors (default to dark mode)
    theme = get_theme_colors(True)
    
    # Apply custom CSS
    apply_custom_css(theme)
    
    # Render sidebar and get selected options
    selected_region, selected_crop, time_period, risk_threshold, is_dark_mode, selected_page = render_sidebar(theme)
    
    # Update theme if changed
    if not is_dark_mode:
        theme = get_theme_colors(False)
    
    # Render selected page
    if selected_page == "Risk Dashboard":
        render_risk_dashboard(selected_region, selected_crop, theme, df)
    elif selected_page == "Intervention Planner":
        render_intervention_planner(selected_region, selected_crop, theme, df)
    elif selected_page == "Market Intel":
        render_market_intel(selected_region, selected_crop, theme, df)
    else:
        st.info("Settings page coming soon!")

if __name__ == "__main__":
    main()