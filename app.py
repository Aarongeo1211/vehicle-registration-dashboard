import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime, timedelta

# Set page configuration - must be first Streamlit command
st.set_page_config(page_title="Vehicle Registration Dashboard", page_icon="🚗", layout="wide")

# Import data processor after page config
try:
    from data_processor import VehicleDataProcessor
except ImportError as e:
    st.error(f"Error importing data processor: {e}")
    st.stop()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin-bottom: 1rem;
    }
    .card {
        border-radius: 5px;
        background-color: #f9f9f9;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 1rem;
        color: #616161;
    }
    .growth-positive {
        color: #4CAF50;
    }
    .growth-negative {
        color: #F44336;
    }
    .footer {
        text-align: center;
        margin-top: 2rem;
        color: #9E9E9E;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

def generate_synthetic_data():
    """Generate synthetic data directly in the app if no data exists"""
    try:
        import random
        from datetime import datetime, timedelta
        
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Define parameters for synthetic data
        start_date = datetime(2020, 1, 1)
        end_date = datetime(2023, 12, 31)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Vehicle types
        vehicle_types = {
            '2W': ['Hero', 'Honda', 'TVS', 'Bajaj', 'Royal Enfield', 'Yamaha', 'Suzuki', 'Ola Electric', 'Ather'],
            '3W': ['Bajaj', 'Piaggio', 'Mahindra', 'TVS', 'Atul', 'Kinetic'],
            '4W': ['Maruti Suzuki', 'Hyundai', 'Tata Motors', 'Mahindra', 'Kia', 'Toyota', 'Honda', 'MG', 'Skoda', 'Volkswagen']
        }
        
        # Create empty dataframe
        data = []
        
        # Set random seed for consistent data generation
        np.random.seed(42)
        random.seed(42)
        
        # Generate synthetic data
        for date in date_range:
            # Add seasonality and trends
            base_registrations = 1000 + 500 * np.sin(date.dayofyear * 2 * np.pi / 365)
            
            # Add yearly growth trend (15% YoY growth)
            yearly_factor = 1.0 + 0.15 * (date.year - start_date.year)
            
            # Add quarterly variations
            quarter = (date.month - 1) // 3 + 1
            quarterly_factor = 1.0 + 0.05 * (quarter == 4) - 0.03 * (quarter == 2)
            
            # Weekend effect (less registrations on weekends)
            day_factor = 0.6 if date.weekday() >= 5 else 1.0
            
            for vehicle_category, manufacturers in vehicle_types.items():
                # Different base volumes for different vehicle types
                category_factor = 1.0
                if vehicle_category == '2W':
                    category_factor = 5.0  # More 2-wheelers
                elif vehicle_category == '3W':
                    category_factor = 0.5  # Fewer 3-wheelers
                
                for manufacturer in manufacturers:
                    # Manufacturer market share (random but consistent)
                    manufacturer_factor = random.uniform(0.5, 1.5)
                    
                    # Calculate registrations with some randomness
                    registrations = int(base_registrations * yearly_factor * quarterly_factor * 
                                       day_factor * category_factor * manufacturer_factor * 
                                       random.uniform(0.8, 1.2))
                    
                    # Add special events/promotions randomly
                    if random.random() < 0.01:  # 1% chance of a promotion
                        registrations = int(registrations * random.uniform(1.5, 2.5))
                    
                    # Add to data list
                    if registrations > 0:  # Only add non-zero registrations
                        data.append({
                            'date': date,
                            'vehicle_type': vehicle_category,
                            'manufacturer': manufacturer,
                            'registrations': registrations
                        })
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Save to CSV
        df.to_csv('data/vehicle_registrations.csv', index=False)
        
        return True
        
    except Exception as e:
        st.error(f"Error generating synthetic data: {e}")
        return False

# Check if data exists, if not generate it
data_files = ['data/vehicle_registrations.csv', 'data/vehicle_registrations_scraped.csv']
data_exists = any(os.path.exists(f) for f in data_files)

if not data_exists:
    st.warning("No data file found. Generating sample data...")
    
    with st.spinner("Generating sample data..."):
        if generate_synthetic_data():
            st.success("Sample data generated successfully!")
            st.rerun()
        else:
            st.error("Failed to generate sample data. Please check the logs.")
            st.stop()

# Initialize data processor
try:
    data_processor = VehicleDataProcessor()
except Exception as e:
    st.error(f"Error initializing data processor: {e}")
    st.stop()

# App title
st.markdown('<h1 class="main-header">Vehicle Registration Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center;">Analysis of vehicle registrations by type and manufacturer</p>', unsafe_allow_html=True)

# Sidebar filters
st.sidebar.markdown('<h2 class="sub-header">Filters</h2>', unsafe_allow_html=True)

# Date range filter
try:
    min_date, max_date = data_processor.get_date_range()
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=[min_date.date(), max_date.date()],
        min_value=min_date.date(),
        max_value=max_date.date()
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date.date(), max_date.date()
except Exception as e:
    st.error(f"Error setting up date filters: {e}")
    st.stop()

# Vehicle type filter
try:
    vehicle_types = data_processor.get_vehicle_types()
    selected_vehicle_types = st.sidebar.multiselect(
        "Select Vehicle Types",
        options=vehicle_types,
        default=vehicle_types
    )
except Exception as e:
    st.error(f"Error setting up vehicle type filters: {e}")
    selected_vehicle_types = []

# Manufacturer filter
try:
    all_manufacturers = data_processor.get_manufacturers()
    selected_manufacturers = st.sidebar.multiselect(
        "Select Manufacturers",
        options=all_manufacturers,
        default=[]
    )
except Exception as e:
    st.error(f"Error setting up manufacturer filters: {e}")
    selected_manufacturers = []

# Time period selection for analysis
time_period = st.sidebar.radio(
    "Analysis Time Period",
    options=["Monthly", "Quarterly", "Yearly"],
    index=1
)

# Filter data based on selections
try:
    filtered_data = data_processor.filter_data(
        start_date=start_date,
        end_date=end_date,
        vehicle_types=selected_vehicle_types if selected_vehicle_types else None,
        manufacturers=selected_manufacturers if selected_manufacturers else None
    )
except Exception as e:
    st.error(f"Error filtering data: {e}")
    st.stop()

# Determine groupby column based on time period selection
if time_period == "Monthly":
    groupby_col = "yearmonth"
elif time_period == "Quarterly":
    groupby_col = "yearquarter"
else:  # Yearly
    groupby_col = "year"

# Get aggregated data
try:
    total_registrations = data_processor.get_total_registrations(filtered_data, groupby=groupby_col)
    registrations_by_category = data_processor.get_registrations_by_category(filtered_data, groupby=groupby_col)
    registrations_by_manufacturer = data_processor.get_registrations_by_manufacturer(filtered_data, groupby=groupby_col)
except Exception as e:
    st.error(f"Error aggregating data: {e}")
    st.stop()

# Calculate YoY and QoQ growth
try:
    if time_period == "Yearly":
        total_yoy = data_processor.calculate_yoy_growth(total_registrations, time_col=groupby_col)
        category_yoy = data_processor.calculate_yoy_growth(registrations_by_category, time_col=groupby_col, group_col="vehicle_type")
        manufacturer_yoy = data_processor.calculate_yoy_growth(registrations_by_manufacturer, time_col=groupby_col, group_col="manufacturer")
        
        # No QoQ for yearly data
        has_qoq = False
    elif time_period == "Quarterly":
        # For YoY, extract year from yearquarter
        total_reg_copy = total_registrations.copy()
        total_reg_copy['year'] = total_reg_copy[groupby_col].str.split('-').str[0].astype(int)
        
        category_reg_copy = registrations_by_category.copy()
        category_reg_copy['year'] = category_reg_copy[groupby_col].str.split('-').str[0].astype(int)
        
        manufacturer_reg_copy = registrations_by_manufacturer.copy()
        manufacturer_reg_copy['year'] = manufacturer_reg_copy[groupby_col].str.split('-').str[0].astype(int)
        
        # Calculate YoY growth using the year column
        total_yoy = data_processor.calculate_yoy_growth(total_reg_copy, time_col='year')
        category_yoy = data_processor.calculate_yoy_growth(category_reg_copy, time_col='year', group_col="vehicle_type")
        manufacturer_yoy = data_processor.calculate_yoy_growth(manufacturer_reg_copy, time_col='year', group_col="manufacturer")
        
        # For QoQ, we can use the original data
        total_qoq = data_processor.calculate_qoq_growth(total_registrations, time_col=groupby_col)
        category_qoq = data_processor.calculate_qoq_growth(registrations_by_category, time_col=groupby_col, group_col="vehicle_type")
        manufacturer_qoq = data_processor.calculate_qoq_growth(registrations_by_manufacturer, time_col=groupby_col, group_col="manufacturer")
        
        has_qoq = True
    else:  # Monthly - convert to quarterly for QoQ
        # For YoY, we need to extract year from yearmonth
        total_reg_copy = total_registrations.copy()
        total_reg_copy['year'] = pd.to_datetime(total_reg_copy[groupby_col]).dt.year
        
        category_reg_copy = registrations_by_category.copy()
        category_reg_copy['year'] = pd.to_datetime(category_reg_copy[groupby_col]).dt.year
        
        manufacturer_reg_copy = registrations_by_manufacturer.copy()
        manufacturer_reg_copy['year'] = pd.to_datetime(manufacturer_reg_copy[groupby_col]).dt.year
        
        # Calculate YoY growth using the year column
        total_yoy = data_processor.calculate_yoy_growth(total_reg_copy, time_col='year')
        category_yoy = data_processor.calculate_yoy_growth(category_reg_copy, time_col='year', group_col="vehicle_type")
        manufacturer_yoy = data_processor.calculate_yoy_growth(manufacturer_reg_copy, time_col='year', group_col="manufacturer")
        
        # For QoQ, we need to convert to quarterly data
        has_qoq = False
        
except Exception as e:
    st.error(f"Error calculating growth metrics: {e}")
    # Set default values to prevent further errors
    total_yoy = pd.DataFrame()
    category_yoy = pd.DataFrame()
    manufacturer_yoy = pd.DataFrame()
    has_qoq = False

# Dashboard layout
col1, col2 = st.columns(2)

# Total registrations over time
with col1:
    st.markdown('<h2 class="sub-header">Total Vehicle Registrations</h2>', unsafe_allow_html=True)
    
    try:
        fig = px.line(
            total_registrations, 
            x=groupby_col, 
            y="registrations",
            markers=True,
            title="Total Registrations Over Time"
        )
        fig.update_layout(height=400, xaxis_title="Time Period", yaxis_title="Registrations")
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error creating total registrations chart: {e}")

# YoY Growth
with col2:
    st.markdown('<h2 class="sub-header">Year-over-Year Growth</h2>', unsafe_allow_html=True)
    
    try:
        # Filter out NaN values (first year has no YoY growth)
        yoy_data = total_yoy.dropna(subset=["yoy_growth"]) if not total_yoy.empty else pd.DataFrame()
        
        if not yoy_data.empty:
            fig = px.bar(
                yoy_data,
                x="year",
                y="yoy_growth",
                title="YoY Growth in Total Registrations",
                color="yoy_growth",
                color_continuous_scale=["red", "green"],
                range_color=[-20, 20]
            )
            fig.update_layout(height=400, xaxis_title="Year", yaxis_title="YoY Growth (%)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No YoY growth data available for the current selection.")
    except Exception as e:
        st.error(f"Error creating YoY growth chart: {e}")

# Continue with rest of the dashboard...
# (Rest of the code remains the same as in the original app.py)

# Registrations by vehicle type
st.markdown('<h2 class="sub-header">Analysis by Vehicle Type</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    try:
        # Stacked area chart of registrations by vehicle type
        pivot_df = registrations_by_category.pivot(index=groupby_col, columns="vehicle_type", values="registrations").reset_index()
        
        fig = px.area(
            pivot_df, 
            x=groupby_col, 
            y=pivot_df.columns[1:],
            title="Registrations by Vehicle Type",
            labels={"value": "Registrations", "variable": "Vehicle Type"}
        )
        fig.update_layout(height=400, xaxis_title="Time Period", yaxis_title="Registrations")
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error creating vehicle type chart: {e}")

with col2:
    try:
        # YoY growth by vehicle type
        if len(selected_vehicle_types) > 0 and not category_yoy.empty:
            fig = px.line(
                category_yoy.dropna(subset=["yoy_growth"]),
                x="year",
                y="yoy_growth",
                color="vehicle_type",
                title="YoY Growth by Vehicle Type",
                markers=True
            )
            fig.update_layout(height=400, xaxis_title="Year", yaxis_title="YoY Growth (%)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Please select at least one vehicle type to see YoY growth comparison.")
    except Exception as e:
        st.error(f"Error creating vehicle type YoY chart: {e}")

# Key metrics and insights
st.markdown('<h2 class="sub-header">Key Metrics & Insights</h2>', unsafe_allow_html=True)

# Calculate key metrics
try:
    total_vehicles = filtered_data["registrations"].sum()
    
    # Get the latest period data for YoY calculation
    if not total_yoy.empty:
        if time_period == "Yearly":
            latest_year = total_yoy["year"].max()
            latest_yoy = total_yoy[total_yoy["year"] == latest_year]["yoy_growth"].values[0] if not total_yoy.empty else np.nan
        else:
            # For quarterly/monthly, get the latest year's YoY since we're now using year for YoY calculations
            latest_year = total_yoy["year"].max()
            latest_yoy_data = total_yoy[total_yoy["year"] == latest_year]
            latest_yoy = latest_yoy_data["yoy_growth"].values[0] if not latest_yoy_data.empty else np.nan
    else:
        latest_yoy = np.nan
        
except Exception as e:
    st.error(f"Error calculating key metrics: {e}")
    total_vehicles = 0
    latest_yoy = np.nan

# Display metrics in cards
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<p class="metric-label">Total Vehicles Registered</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="metric-value">{total_vehicles:,.0f}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<p class="metric-label">Latest YoY Growth</p>', unsafe_allow_html=True)
    
    if not np.isnan(latest_yoy):
        color_class = "growth-positive" if latest_yoy >= 0 else "growth-negative"
        st.markdown(f'<p class="metric-value {color_class}">{latest_yoy:.1f}%</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="metric-value">N/A</p>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<p class="metric-label">Vehicle Type Breakdown</p>', unsafe_allow_html=True)
    
    try:
        vehicle_counts = filtered_data.groupby("vehicle_type")["registrations"].sum()
        if not vehicle_counts.empty:
            top_type = vehicle_counts.idxmax()
            top_pct = (vehicle_counts[top_type] / vehicle_counts.sum()) * 100
            st.markdown(f'<p class="metric-value">{top_type}: {top_pct:.1f}%</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="metric-value">N/A</p>', unsafe_allow_html=True)
    except Exception as e:
        st.markdown('<p class="metric-value">N/A</p>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown('<div class="footer">Vehicle Registration Dashboard | Data Source: Vahan Dashboard (Synthetic Data)</div>', unsafe_allow_html=True)
