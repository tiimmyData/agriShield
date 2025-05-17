region_data = {
    'regions': [
        {
            'state': 'Kano',
            'agricultural_zone': 'Northern Sudan Savanna',
            'major_markets': ['Dawanau', 'Yankaba', 'Rimi', 'Gwarzo', 'Wudil'],
            'monthly_weather': {
                'Jan': {'avg_temp': 23, 'avg_rainfall_mm': 0, 'avg_humidity': 20},
                'Feb': {'avg_temp': 25, 'avg_rainfall_mm': 0, 'avg_humidity': 15},
                'Mar': {'avg_temp': 30, 'avg_rainfall_mm': 0, 'avg_humidity': 14},
                'Apr': {'avg_temp': 33, 'avg_rainfall_mm': 10, 'avg_humidity': 25},
                'May': {'avg_temp': 33, 'avg_rainfall_mm': 55, 'avg_humidity': 45},
                'Jun': {'avg_temp': 30, 'avg_rainfall_mm': 110, 'avg_humidity': 60},
                'Jul': {'avg_temp': 28, 'avg_rainfall_mm': 210, 'avg_humidity': 70},
                'Aug': {'avg_temp': 27, 'avg_rainfall_mm': 290, 'avg_humidity': 75},
                'Sep': {'avg_temp': 28, 'avg_rainfall_mm': 150, 'avg_humidity': 68},
                'Oct': {'avg_temp': 29, 'avg_rainfall_mm': 20, 'avg_humidity': 40},
                'Nov': {'avg_temp': 26, 'avg_rainfall_mm': 0, 'avg_humidity': 25},
                'Dec': {'avg_temp': 24, 'avg_rainfall_mm': 0, 'avg_humidity': 22}
            },
            'storage_facilities': [
                {'name': 'Dawanau Grains Market Warehouse', 'type': 'Dry', 'capacity_tons': 25000},
                {'name': 'Kano State Agricultural Supply Company', 'type': 'Dry', 'capacity_tons': 5000},
                {'name': 'Gezawa Commodity Market Storage', 'type': 'Dry', 'capacity_tons': 3500},
                {'name': 'Kano Cold Storage', 'type': 'Cold', 'capacity_tons': 500}
            ],
            'road_conditions': {
                'rainy_season': 'Fair',
                'dry_season': 'Good'
            }
        },
        {
            'state': 'Benue',
            'agricultural_zone': 'Southern Guinea Savanna',
            'major_markets': ['Wurukum', 'Modern Market', 'North Bank', 'Gboko', 'Otukpo'],
            'monthly_weather': {
                'Jan': {'avg_temp': 26, 'avg_rainfall_mm': 5, 'avg_humidity': 37},
                'Feb': {'avg_temp': 28, 'avg_rainfall_mm': 15, 'avg_humidity': 40},
                'Mar': {'avg_temp': 31, 'avg_rainfall_mm': 45, 'avg_humidity': 52},
                'Apr': {'avg_temp': 30, 'avg_rainfall_mm': 90, 'avg_humidity': 65},
                'May': {'avg_temp': 29, 'avg_rainfall_mm': 160, 'avg_humidity': 72},
                'Jun': {'avg_temp': 28, 'avg_rainfall_mm': 190, 'avg_humidity': 80},
                'Jul': {'avg_temp': 27, 'avg_rainfall_mm': 210, 'avg_humidity': 83},
                'Aug': {'avg_temp': 26, 'avg_rainfall_mm': 240, 'avg_humidity': 85},
                'Sep': {'avg_temp': 27, 'avg_rainfall_mm': 220, 'avg_humidity': 80},
                'Oct': {'avg_temp': 28, 'avg_rainfall_mm': 120, 'avg_humidity': 70},
                'Nov': {'avg_temp': 27, 'avg_rainfall_mm': 15, 'avg_humidity': 50},
                'Dec': {'avg_temp': 26, 'avg_rainfall_mm': 5, 'avg_humidity': 40}
            },
            'storage_facilities': [
                {'name': 'Makurdi Grains Silo Complex', 'type': 'Dry', 'capacity_tons': 15000},
                {'name': 'Benue Agricultural Development Company Warehouse', 'type': 'Dry', 'capacity_tons': 8000},
                {'name': 'Gboko Community Storage', 'type': 'Dry', 'capacity_tons': 5000},
                {'name': 'Otukpo Yam Storage', 'type': 'Traditional', 'capacity_tons': 3000}
            ],
            'road_conditions': {
                'rainy_season': 'Poor',
                'dry_season': 'Fair'
            }
        },
        {
            'state': 'Kebbi',
            'agricultural_zone': 'Sahel Savanna',
            'major_markets': ['Argungu', 'Jega', 'Birnin Kebbi', 'Yauri', 'Zuru'],
            'monthly_weather': {
                'Jan': {'avg_temp': 24, 'avg_rainfall_mm': 0, 'avg_humidity': 16},
                'Feb': {'avg_temp': 27, 'avg_rainfall_mm': 0, 'avg_humidity': 14},
                'Mar': {'avg_temp': 31, 'avg_rainfall_mm': 0, 'avg_humidity': 13},
                'Apr': {'avg_temp': 34, 'avg_rainfall_mm': 5, 'avg_humidity': 26},
                'May': {'avg_temp': 34, 'avg_rainfall_mm': 40, 'avg_humidity': 45},
                'Jun': {'avg_temp': 32, 'avg_rainfall_mm': 80, 'avg_humidity': 58},
                'Jul': {'avg_temp': 30, 'avg_rainfall_mm': 180, 'avg_humidity': 68},
                'Aug': {'avg_temp': 29, 'avg_rainfall_mm': 250, 'avg_humidity': 73},
                'Sep': {'avg_temp': 30, 'avg_rainfall_mm': 110, 'avg_humidity': 65},
                'Oct': {'avg_temp': 31, 'avg_rainfall_mm': 15, 'avg_humidity': 35},
                'Nov': {'avg_temp': 28, 'avg_rainfall_mm': 0, 'avg_humidity': 22},
                'Dec': {'avg_temp': 25, 'avg_rainfall_mm': 0, 'avg_humidity': 18}
            },
            'storage_facilities': [
                {'name': 'Kebbi State Silo Complex', 'type': 'Dry', 'capacity_tons': 10000},
                {'name': 'Jega Rice Storage Facility', 'type': 'Dry', 'capacity_tons': 7500},
                {'name': 'Yauri Fish Processing Facility', 'type': 'Cold', 'capacity_tons': 300},
                {'name': 'Birnin Kebbi Central Storage', 'type': 'Dry', 'capacity_tons': 5000}
            ],
            'road_conditions': {
                'rainy_season': 'Poor',
                'dry_season': 'Fair'
            }
        },
        {
            'state': 'Plateau',
            'agricultural_zone': 'High Altitude Zone',
            'major_markets': ['Terminus', 'Farin Gada', 'Bukuru', 'Mangu', 'Shendam'],
            'monthly_weather': {
                'Jan': {'avg_temp': 22, 'avg_rainfall_mm': 0, 'avg_humidity': 15},
                'Feb': {'avg_temp': 24, 'avg_rainfall_mm': 5, 'avg_humidity': 20},
                'Mar': {'avg_temp': 27, 'avg_rainfall_mm': 25, 'avg_humidity': 35},
                'Apr': {'avg_temp': 26, 'avg_rainfall_mm': 80, 'avg_humidity': 55},
                'May': {'avg_temp': 25, 'avg_rainfall_mm': 140, 'avg_humidity': 68},
                'Jun': {'avg_temp': 23, 'avg_rainfall_mm': 170, 'avg_humidity': 78},
                'Jul': {'avg_temp': 22, 'avg_rainfall_mm': 280, 'avg_humidity': 85},
                'Aug': {'avg_temp': 21, 'avg_rainfall_mm': 320, 'avg_humidity': 88},
                'Sep': {'avg_temp': 22, 'avg_rainfall_mm': 240, 'avg_humidity': 80},
                'Oct': {'avg_temp': 23, 'avg_rainfall_mm': 90, 'avg_humidity': 60},
                'Nov': {'avg_temp': 22, 'avg_rainfall_mm': 10, 'avg_humidity': 30},
                'Dec': {'avg_temp': 21, 'avg_rainfall_mm': 0, 'avg_humidity': 17}
            },
            'storage_facilities': [
                {'name': 'Jos Central Cold Store', 'type': 'Cold', 'capacity_tons': 1200},
                {'name': 'Plateau Agricultural Development Programme Warehouse', 'type': 'Dry', 'capacity_tons': 6000},
                {'name': 'Bokkos Potato Storage', 'type': 'Cold', 'capacity_tons': 800},
                {'name': 'Shendam Community Storage', 'type': 'Traditional', 'capacity_tons': 2500}
            ],
            'road_conditions': {
                'rainy_season': 'Poor',
                'dry_season': 'Fair'
            }
        }
    ]
}