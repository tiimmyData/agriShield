# 🌾 AgriShield - Crop Protection Dashboard

AgriShield is an intelligent crop spoilage risk assessment and prevention dashboard designed to help farmers protect their harvest from post-harvest losses. The system provides real-time risk analysis, weather-based alerts, and actionable recommendations to minimize crop spoilage.

## 🚀 Features

### Core Functionality
- **Risk Assessment**: Real-time crop spoilage risk scoring (0-100 scale)
- **Monthly Risk Timeline**: Visualize risk patterns throughout the year
- **Weather Integration**: Weather-based risk factors and alerts
- **Crop-Specific Guidance**: Tailored recommendations for different crops
- **Regional Data**: Location-specific weather and storage information
- **Intervention Recommendations**: Actionable steps to prevent losses

### Dashboard Components
- **Risk Metrics**: Current spoilage risk, high-risk months, crop stages
- **Interactive Charts**: Risk timeline with current month highlighting
- **Alert System**: Color-coded risk levels (Low/Medium/High)
- **Weather Alerts**: Current conditions and crop-specific advice
- **Storage Facilities**: Local storage options and recommendations
- **Crop Information**: Shelf life, storage methods, and best practices

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Data Visualization**: Plotly Express & Plotly Graph Objects
- **Data Processing**: Pandas
- **Python Libraries**: 
  - `streamlit` - Web app framework
  - `pandas` - Data manipulation
  - `plotly` - Interactive visualizations
  - `calendar` - Date/time utilities
  - `datetime` - Date handling
  - `pathlib` - File path management

## 📁 Project Structure

```
agrishield/
├── app/
│   └── dashboard.py          # Main Streamlit application
├── database/
│   ├── crop_calender.py      # Crop planting/harvest schedules
│   ├── crop_sustainability.py # Crop characteristics and vulnerabilities
│   ├── intervention.py       # Risk mitigation strategies
│   ├── region_data.py        # Regional weather and facility data
│   └── seasonal_calender.py  # Seasonal weather patterns
├── requirements.txt          # Python dependencies
└── README.md                # Project documentation
```

## 🔧 Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/tiimmyData/agriShield
   cd agrishield
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv agrishield-env
   source agrishield-env/bin/activate  # On Windows: agrishield-env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run app/dashboard.py
   ```

5. **Access the dashboard**
   - Open your web browser and navigate to `http://localhost:8501`

## 📋 Requirements

Create a `requirements.txt` file with the following dependencies:

```txt
streamlit>=1.28.0
pandas>=1.5.0
plotly>=5.15.0
```

## 🎯 Usage

### Getting Started
1. **Select Your Region**: Choose your farming region from the sidebar dropdown
2. **Select Your Crop**: Pick the crop you want to monitor
3. **View Risk Assessment**: Check the current spoilage risk score and category
4. **Follow Recommendations**: Read the "What You Should Do Now" section for immediate actions

### Understanding Risk Levels
- **🟢 Low Risk (0-35)**: No urgent action needed
- **🟡 Medium Risk (35-70)**: Monitor conditions closely
- **🔴 High Risk (70-100)**: Take immediate action to prevent losses

### Key Metrics Explained
- **Chance of Spoilage**: Overall risk score based on weather, crop stage, and historical data
- **High Risk Months**: Number of months per year with elevated spoilage risk
- **Current Crop Stage**: Whether crops are in planting, harvest, or post-harvest phase
- **Historical Loss %**: Average percentage of crop lost to spoilage annually

## 📊 Data Sources

The system integrates multiple data sources:

### Crop Calendar (`crop_calender.py`)
- Planting and harvest schedules by region
- Peak loss periods
- Historical loss percentages

### Crop Sustainability (`crop_sustainability.py`)
- Crop shelf life and storage requirements
- Moisture and heat sensitivity
- Primary spoilage factors

### Regional Data (`region_data.py`)
- Monthly weather patterns
- Storage facility locations
- Regional climate characteristics

### Seasonal Calendar (`seasonal_calender.py`)
- Rainfall patterns
- Temperature variations
- Seasonal risk factors

## 🔍 Risk Calculation Algorithm

The risk score is calculated using multiple factors:

1. **Base Risk**: 20 points (baseline)
2. **Peak Loss Period**: +40 points if in high-loss months
3. **Rainy Season**: +20 points during heavy rainfall periods
4. **Harvest Period**: +10 points during harvest months
5. **Crop Perishability**: +10 points for highly perishable crops

**Risk Categories:**
- Low: 0-35 points
- Medium: 36-70 points  
- High: 71-100 points

## 🚨 Alert System

### Immediate Alerts
- **High Risk (70+)**: "Act immediately - dry or sell within 2 days"
- **Medium Risk (35-69)**: "Monitor conditions - sell quickly if rain forecast"
- **Low Risk (0-34)**: "Continue normal storage practices"

### Monthly Notifications
- Advance warnings for high-risk periods
- Weather-based recommendations
- Storage facility suggestions

## 🌤️ Weather Integration

The system provides:
- Current month weather conditions
- Temperature, rainfall, and humidity data
- Weather-specific crop advice
- Monthly weather pattern visualization

## 🎨 Customization

### Adding New Crops
1. Update `crop_calender.py` with planting/harvest schedules
2. Add crop characteristics to `crop_sustainability.py`
3. Define interventions in `intervention.py`

### Adding New Regions
1. Add regional data to `region_data.py`
2. Include weather patterns in `seasonal_calender.py`
3. Update crop calendars for the new region

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 📈 Future Enhancements

- [ ] Real-time weather API integration
- [ ] SMS/Email alert notifications
- [ ] Mobile app development
- [ ] Machine learning-based risk prediction
- [ ] Market price integration
- [ ] Multi-language support
- [ ] Offline functionality

## 🐛 Troubleshooting

### Common Issues

**Import Errors**
- Ensure all database modules are in the correct directory
- Check Python path configuration

**Data Loading Issues**
- Verify data files exist in the database directory
- Check file permissions

**Streamlit Errors**
- Update Streamlit to the latest version
- Clear browser cache and reload

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Send me an [Email](mailto:badadavid04@gmailcom)


## 🙏 Acknowledgments

- Lasis Simon
- Cambiado
- Bernoulli Jnr
- Tech Girl

---

**AgriShield** - Helping Farmers Protect Their Harvest | Updated May 2025

*Built with ❤️ for farmers in Nigeria*