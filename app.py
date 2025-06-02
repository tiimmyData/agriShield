import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import calendar
from datetime import datetime
import sys
from pathlib import Path

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
                    'crop_stage_name': crop_stage,
                    'historical_loss_percentage': crop_calendar[region][crop]['historical_loss_percentage']
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

# Sidebar filters
st.sidebar.title('🌾 AgriShield')
st.sidebar.subheader('Crop Protection Dashboard')

selected_region = st.sidebar.selectbox('Select Your Region', df['region'].unique())
selected_crop = st.sidebar.selectbox('Select Your Crop', df[df['region'] == selected_region]['crop'].unique())

# Get the selected crop's susceptibility information
crop_info = next((c for c in crop_susceptibility['crops'] if c['name'] == selected_crop), None)
crop_interventions = interventions.get(selected_crop, {})

# Main dashboard
st.title('Crop Spoilage Risk Dashboard')
st.markdown(f"**Today's Month: {current_month_full}**")

# Create two columns for metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_risk = df[
        (df['region'] == selected_region) & 
        (df['crop'] == selected_crop)
    ]['risk_score'].mean()
    
    # Determine color and label
    if avg_risk < 35:
        risk_color = "🟢"
        risk_label = "Low"
    elif avg_risk < 70:
        risk_color = "🟡"
        risk_label = "Medium"
    else:
        risk_color = "🔴"
        risk_label = "High"
        
    st.metric(
        "Chance of Spoilage",
        f"{avg_risk:.1f}/100 {risk_color}",
        help="A higher score means a greater risk of crop spoilage this month. 0 = No risk, 100 = Very high risk.",
    )
    st.caption(f"**This is a {risk_label} risk for {selected_crop} in {selected_region} this month.**")

with col2:
    high_risk_months = df[
        (df['region'] == selected_region) & 
        (df['crop'] == selected_crop) & 
        (df['risk_category'] == 'High')
    ]['month'].nunique()
    st.metric("High Risk Months", high_risk_months, help="Number of months per year with high spoilage risk")

with col3:
    current_month_data = df[
        (df['region'] == selected_region) & 
        (df['crop'] == selected_crop) &
        (df['month'] == current_month)
    ]
    
    if not current_month_data.empty:
        current_stage = current_month_data['crop_stage_name'].iloc[0]
        st.metric("Current Crop Stage", current_stage, help="What stage your crop is in right now")
    else:
        st.metric("Current Crop Stage", "Unknown")

with col4:
    historical_loss = df[
        (df['region'] == selected_region) & 
        (df['crop'] == selected_crop)
    ]['historical_loss_percentage'].mean()
    st.metric("Historical Loss %", f"{historical_loss:.1f}%", help="Average percentage of crop lost to spoilage each year")
    st.caption(f"That means for every 1,000kg harvested, about {historical_loss*10:.0f}kg was lost last year.")

# What You Should Do Now Section
st.subheader("✅ What You Should Do Now")
if avg_risk >= 70:
    st.error("🚨 HIGH RISK! Act immediately: Dry or sell your crop within 2 days. Avoid transport delays. Use cold storage if possible.")
elif avg_risk >= 35:
    st.warning("⚠️ MEDIUM RISK: Monitor weather and storage conditions. Sell quickly if rain is forecast.")
else:
    st.success("✅ LOW RISK: No urgent action needed. Continue storing your crop properly.")

# Create two rows for charts
row1_col1, row1_col2 = st.columns(2)

# Risk score timeline chart
with row1_col1:
    st.subheader("Risk Score Timeline")
    st.caption("This chart shows how the risk of post-harvest loss changes throughout the year. Higher scores mean higher risk of crop spoilage.")

    filtered_df = df[
        (df['region'] == selected_region) & 
        (df['crop'] == selected_crop)
    ]

    months = list(calendar.month_abbr[1:])
    risk_scores = [filtered_df[filtered_df['month'] == m]['risk_score'].values[0] if not filtered_df[filtered_df['month'] == m].empty else None for m in months]
    current_idx = months.index(current_month)

    fig = go.Figure()

    # Add color bands for risk zones
    fig.add_shape(type="rect", x0=-0.5, x1=11.5, y0=0, y1=35, fillcolor="rgba(0,200,0,0.08)", line_width=0, layer="below")
    fig.add_shape(type="rect", x0=-0.5, x1=11.5, y0=35, y1=70, fillcolor="rgba(255,200,0,0.08)", line_width=0, layer="below")
    fig.add_shape(type="rect", x0=-0.5, x1=11.5, y0=70, y1=100, fillcolor="rgba(255,0,0,0.08)", line_width=0, layer="below")

    # Plot risk line
    fig.add_trace(go.Scatter(
        x=months,
        y=risk_scores,
        mode='lines+markers',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8, color=['red' if i == current_idx else '#1f77b4' for i in range(12)]),
        name='Risk Score'
    ))

    # Annotate current month
    fig.add_annotation(
        x=months[current_idx],
        y=risk_scores[current_idx],
        text="Current Month",
        showarrow=True,
        arrowhead=1,
        ax=0,
        ay=-40,
        bgcolor="red",
        font=dict(color="white")
    )

    # Annotate peak risk
    peak_idx = risk_scores.index(max(risk_scores))
    if peak_idx != current_idx:
        fig.add_annotation(
            x=months[peak_idx],
            y=risk_scores[peak_idx],
            text="Peak Risk",
            showarrow=True,
            arrowhead=1,
            ax=0,
            ay=-40,
            bgcolor="orange",
            font=dict(color="white")
        )

    fig.update_layout(
        title="Monthly Risk Profile",
        xaxis_title="Month",
        yaxis_title="Risk Score (0-100)",
        yaxis=dict(range=[0, 100]),
        showlegend=False,
        plot_bgcolor='#23272f',
        paper_bgcolor='#23272f',
        font=dict(color='white')
    )

    st.plotly_chart(fig, use_container_width=True)

    # Add actionable advice
    st.info("💡 **Advice:** Take extra care during months in the yellow and red zones. Dry or sell your crop quickly in high-risk months.")


with row1_col2:
    st.subheader("Main Risk Factors Right Now")
    current_risk_factors = filtered_df[filtered_df['month'] == current_month]
    
    if not current_risk_factors.empty:
        factors = []
        explanations = []
        # Rainy Season
        if current_risk_factors['is_rainy_season'].iloc[0]:
            factors.append("💧 Rainy Season")
            explanations.append("High humidity increases spoilage risk. Dry crops quickly.")
        # Flood Risk
        if current_risk_factors['flood_risk_level'].iloc[0]:
            factors.append("🌊 Flood Risk")
            explanations.append("Flooding may disrupt transport and damage stored crops.")
        # Lean Period
        if current_risk_factors['is_lean_period'].iloc[0]:
            factors.append("⏳ Lean Period")
            explanations.append("Food stocks are low; prices may be higher, but storage is critical.")
        # If no active factors
        if not factors:
            st.success("✅ No major risk factors this month.")
        else:
            for i, factor in enumerate(factors):
                st.markdown(f"**{factor}**")
                st.caption(explanations[i])
    else:
        st.info(f"No risk factor data available for {current_month}")
    # After the above code, add:
    region_info = next((r for r in region_data['regions'] if r['state'] == selected_region), None)
    if region_info:
        weather = region_info['monthly_weather'].get(current_month, {})
        if weather:
            st.markdown("**This Month's Weather:**")
            st.write(
                f"🌡️ Temp: {weather['avg_temp']}°C | "
                f"💧 Rainfall: {weather['avg_rainfall_mm']}mm | "
                f"💦 Humidity: {weather['avg_humidity']}%"
            )
    
    # Compare with previous month
    prev_month_idx = (list(calendar.month_abbr[1:]).index(current_month) - 1) % 12
    prev_month = list(calendar.month_abbr[1:])[prev_month_idx]
    prev_risk_factors = filtered_df[filtered_df['month'] == prev_month]
    if not prev_risk_factors.empty:
        prev_rainy = prev_risk_factors['is_rainy_season'].iloc[0]
        now_rainy = current_risk_factors['is_rainy_season'].iloc[0]
        if now_rainy and not prev_rainy:
            st.warning("Rainy season has just started—risk is rising.")



# Last Alert Sent Section
st.subheader("📱 Latest Alert Message")
current_month_risk = filtered_df[filtered_df['month'] == current_month]
if not current_month_risk.empty:
    risk_score = current_month_risk['risk_score'].iloc[0]
    crop_stage = current_month_risk['crop_stage_name'].iloc[0]
    
    if risk_score >= 70:
        alert_msg = f"⚠️ HIGH RISK ALERT: Your {selected_crop} crop in {selected_region} has a {risk_score:.0f}% chance of spoilage this month. Sell or process immediately. Heavy rains expected."
        st.error(alert_msg)
    elif risk_score >= 35:
        alert_msg = f"⚠️ MEDIUM RISK: Your {selected_crop} crop has a {risk_score:.0f}% spoilage risk. Monitor storage conditions closely. Consider early sale if weather worsens."
        st.warning(alert_msg)
    else:
        alert_msg = f"✅ LOW RISK: Your {selected_crop} crop is safe with only {risk_score:.0f}% spoilage risk. Continue normal storage practices."
        st.success(alert_msg)
else:
    st.info("No current alerts for your crop and region.")

# Crop Information Section
st.subheader("📖 Your Crop Information")
col1, col2 = st.columns(2)

with col1:
    if crop_info:
        st.write(f"**How Long It Lasts:** {crop_info['shelf_life_days']} days")
        st.write(f"**Sensitive to Moisture:** {crop_info['moisture_sensitivity']}")
        st.write(f"**Sensitive to Heat:** {crop_info['heat_sensitivity']}")
        st.write("**Main Spoilage Causes:**")
        for factor in crop_info['primary_spoilage']:
            st.write(f"- {factor}")
    else:
        st.write("No detailed crop information available")

with col2:
    st.write("**Best Storage Method:**")
    if crop_info:
        st.write(f"- {crop_info['recommended_storage']}")
    
    st.write("**Best Planting Times:**")
    if selected_region in crop_calendar and selected_crop in crop_calendar[selected_region]:
        planting_months = crop_calendar[selected_region][selected_crop]['planting_months']
        st.write(", ".join(planting_months))
    else:
        st.write("No planting information available")
    
    st.write("**Harvest Months:**")
    if selected_region in crop_calendar and selected_crop in crop_calendar[selected_region]:
        harvest_months = crop_calendar[selected_region][selected_crop]['harvest_months']
        st.write(", ".join(harvest_months))
    else:
        st.write("No harvest information available")

# Risk alerts section
st.subheader("⚠️ Yearly Risk Alerts")
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
        
        risk_factors_text = ", ".join(risk_factors) if risk_factors else "multiple factors"
        
        st.warning(
            f"🚨 Expect high spoilage risk for {row['crop']} in {row['month_name']} "
            f"due to {risk_factors_text}. Plan ahead!"
        )
else:
    st.success("✅ Good news! No high-risk periods detected for your crop and region.")

# Intervention recommendations
st.subheader("🛡️ Recommended Actions")

if crop_interventions:
    st.write(f"**When Risk is High:** {crop_interventions['high_risk_conditions']}")
    
    st.write("**What to Do:**")
    for action in crop_interventions['recommended_actions']:
        st.write(f"✓ {action}")
else:
    st.info(f"No specific action recommendations available for {selected_crop}")

# Weather Alert for Your Crops
st.subheader("🌤️ Weather Alert for Your Crops")

region_info = next((r for r in region_data['regions'] if r['state'] == selected_region), None)
if region_info:
    monthly_weather = region_info['monthly_weather']
    
    # Get current month weather data
    current_weather = monthly_weather.get(current_month_full, {})
    
    if current_weather:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**This Month's Conditions:**")
            temp = current_weather.get('avg_temp', 0)
            rainfall = current_weather.get('avg_rainfall_mm', 0)
            humidity = current_weather.get('avg_humidity', 0)
            
            st.write(f"🌡️ Temperature: {temp}°C")
            st.write(f"☔ Rainfall: {rainfall}mm")
            st.write(f"💧 Humidity: {humidity}%")
        
        with col2:
            st.write("**What This Means for Your Crops:**")
            
            # Temperature advice
            if temp > 35:
                st.write("🔥 Very hot - Store crops in cool, shaded areas")
            elif temp > 30:
                st.write("🌡️ Hot weather - Keep storage well-ventilated")
            else:
                st.write("✅ Good temperature for storage")
            
            # Rainfall advice
            if rainfall > 200:
                st.write("🌊 Heavy rains - Use waterproof storage")
            elif rainfall > 100:
                st.write("☔ Rainy season - Keep crops dry and covered")
            else:
                st.write("☀️ Dry conditions - Good for drying crops")
            
            # Humidity advice
            if humidity > 80:
                st.write("💨 High humidity - Ensure good air circulation")
            elif humidity > 60:
                st.write("💧 Moderate humidity - Monitor for mold growth")
            else:
                st.write("✅ Low humidity - Good for storage")
    
    # Show expandable detailed weather charts
    with st.expander("📊 View Detailed Weather Charts"):
        # Prepare weather data for plotting
        weather_data = []
        for month, data in monthly_weather.items():
            weather_data.append({
                'Month': month,
                'Temperature (°C)': data['avg_temp'],
                'Rainfall (mm)': data['avg_rainfall_mm'],
                'Humidity (%)': data['avg_humidity']
            })
        
        weather_df = pd.DataFrame(weather_data)
        
        # Plot charts
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.line(weather_df, x='Month', y='Temperature (°C)', markers=True,
                         title="Average Monthly Temperature")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(weather_df, x='Month', y='Rainfall (mm)',
                        title="Average Monthly Rainfall")
            st.plotly_chart(fig, use_container_width=True)    
    # Storage facilities
    st.subheader("🏪 Storage Facilities Near You")
    
    if 'storage_facilities' in region_info:
        facilities_df = pd.DataFrame(region_info['storage_facilities'])
        st.dataframe(facilities_df, hide_index=True, use_container_width=True)
    else:
        st.info("No storage facility information available for this region")
else:
    st.info(f"No detailed weather data available for {selected_region}")

# Footer
st.markdown("---")
st.markdown("🌾 AgriShield - Helping Farmers Protect Their Harvest | Updated May 2025")