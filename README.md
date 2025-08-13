# Vehicle Registration Dashboard

A data visualization dashboard focused on vehicle registration data from the Vahan Dashboard, designed with investors in mind. This dashboard provides insights into vehicle registrations by type (2W/3W/4W) and manufacturer, with Year-over-Year (YoY) and Quarter-over-Quarter (QoQ) growth analysis.

## Features

- **Interactive Filters**:
  - Date range selection
  - Vehicle type filtering (2W/3W/4W)
  - Manufacturer selection
  - Time period analysis (Monthly/Quarterly/Yearly)

- **Comprehensive Visualizations**:
  - Total registrations over time
  - YoY and QoQ growth trends
  - Vehicle type breakdown and comparison
  - Manufacturer market share and performance
  - Growth analysis for selected manufacturers

- **Investor-Focused Metrics**:
  - Key performance indicators
  - Growth percentages
  - Market share analysis
  - Trend identification

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/vehicle-registration-dashboard.git
   cd vehicle-registration-dashboard
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install required packages:
   ```
   pip install -r requirements.txt
   ```

### Running the Application

1. Launch the Streamlit dashboard:
   ```
   streamlit run app.py
   ```

2. If no data is available, you'll be prompted to either:
   - Generate synthetic data
   - Fetch real data from public sources

3. Open your web browser and navigate to the URL displayed in the terminal (typically http://localhost:8501)

## Data Assumptions

- The dashboard currently uses synthetic data that mimics the structure and patterns of real vehicle registration data from the Vahan Dashboard.
- The synthetic data includes:
  - Daily vehicle registrations from 2020 to 2023
  - Three vehicle categories: 2W (two-wheelers), 3W (three-wheelers), and 4W (four-wheelers)
  - Major manufacturers in each category
  - Seasonal patterns, yearly growth trends, and quarterly variations
  - Weekend effects (lower registrations on weekends)
  - Occasional promotional events causing registration spikes

- In a production environment, this would be replaced with real data from the Vahan Dashboard API or database.

## Data Collection Process

The dashboard supports two methods of data collection:

### 1. Real Data Scraping

The application can fetch vehicle registration data from public sources including:
- e-vahan portal data available through data.gov.in
- India Data Portal's VAHAN Vehicle Registrations dataset

To scrape data directly, run:
```
python scrape_data.py
```

Note: Direct API access to some sources may require registration or payment. The implementation includes fallback mechanisms to ensure the dashboard remains functional even when direct data access is limited.

### 2. Synthetic Data Generation

For testing or when real data is unavailable, the application can generate synthetic data with the following characteristics:

1. **Time Range**: 4 years of daily data (2020-2023)
2. **Vehicle Categories**: 2W, 3W, and 4W
3. **Manufacturers**: Major manufacturers in each category
4. **Patterns**:
   - Seasonal variations
   - Yearly growth trends (15% YoY)
   - Quarterly fluctuations
   - Weekend effects
   - Random promotional events

In a production environment, data would be collected from the Vahan Dashboard through:
1. API access (if available)
2. Database connection (if granted access)
3. Web scraping (if permitted)
4. Regular data updates via scheduled scripts

## Feature Roadmap

Future enhancements planned for the dashboard:

1. **Data Integration**:
   - Connect to real Vahan Dashboard API/database
   - Implement automated data refresh
   - Add historical data going back further

2. **Advanced Analytics**:
   - Predictive forecasting for future registrations
   - Anomaly detection for unusual registration patterns
   - Correlation analysis with economic indicators
   - Seasonal decomposition of trends

3. **Enhanced Visualizations**:
   - Geographic heatmaps of registrations by region
   - Interactive drill-down capabilities
   - Custom report generation
   - Export functionality for presentations

4. **Investor-Specific Features**:
   - Company financial data integration
   - Stock price correlation analysis
   - Competitive positioning metrics
   - Market penetration calculations

5. **Technical Improvements**:
   - Caching for improved performance
   - User authentication and personalized views
   - Mobile-optimized interface
   - Scheduled report delivery

## Video Walkthrough

A video walkthrough of the dashboard is available at: [Link to Video](https://youtu.be/your-video-id)

## Investment Insights

Based on the analysis of the vehicle registration data, some valuable investment insights include:

1. **Electric Vehicle Transition**: The data shows an accelerating trend in electric vehicle registrations, particularly in the 2W category, suggesting investment opportunities in EV manufacturers and infrastructure.

2. **Seasonal Patterns**: Strong seasonal patterns in vehicle registrations can help investors time their investments in automotive stocks.

3. **Market Consolidation**: The data reveals increasing market concentration among top manufacturers, indicating potential for market leaders to strengthen their positions.

4. **Regional Growth Disparities**: Significant variations in growth rates across different regions highlight opportunities in emerging markets.

5. **Policy Impact**: Registration spikes following policy announcements demonstrate the importance of monitoring regulatory changes for investment decisions.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Data source: Vahan Dashboard (synthetic data for prototype)
- Built with Streamlit, Pandas, and Plotly
