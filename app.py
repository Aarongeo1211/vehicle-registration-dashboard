import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime, timedelta
from data_processor import VehicleDataProcessor

# Set page configuration
st.set_page_config(page_title="Vehicle Registration Dashboard", page_icon="🚗", layout="wide")

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

# Check if data exists, if not generate it
if not os.path.exists('data/vehicle_registrations.csv') and not os.path.exists('data/vehicle_registrations_scraped.csv'):
    st.warning("No data file found. Please choose an option below:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Generate Sample Data"):
            import data_generator
            st.success("Sample data generated successfully! Please refresh the page.")
            st.stop()
    with col2:
        if st.button("Fetch Real Data"):
            from data_scraper import VehicleDataScraper
            with st.spinner("Fetching data from public sources..."):
                scraper = VehicleDataScraper()
                data_file = scraper.scrape_and_save_data()
                st.success(f"Data fetched successfully from public sources! Data saved to {data_file}. Please refresh the page.")
            st.stop()
    st.stop()

# Initialize data processor
data_processor = VehicleDataProcessor()

# App title
st.markdown('<h1 class="main-header">Vehicle Registration Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center;">Analysis of vehicle registrations by type and manufacturer</p>', unsafe_allow_html=True)

# Sidebar filters
st.sidebar.markdown('<h2 class="sub-header">Filters</h2>', unsafe_allow_html=True)

# Date range filter
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

# Vehicle type filter
vehicle_types = data_processor.get_vehicle_types()
selected_vehicle_types = st.sidebar.multiselect(
    "Select Vehicle Types",
    options=vehicle_types,
    default=vehicle_types
)

# Manufacturer filter
all_manufacturers = data_processor.get_manufacturers()
selected_manufacturers = st.sidebar.multiselect(
    "Select Manufacturers",
    options=all_manufacturers,
    default=[]
)

# Time period selection for analysis
time_period = st.sidebar.radio(
    "Analysis Time Period",
    options=["Monthly", "Quarterly", "Yearly"],
    index=1
)

# Filter data based on selections
filtered_data = data_processor.filter_data(
    start_date=start_date,
    end_date=end_date,
    vehicle_types=selected_vehicle_types if selected_vehicle_types else None,
    manufacturers=selected_manufacturers if selected_manufacturers else None
)

# Determine groupby column based on time period selection
if time_period == "Monthly":
    groupby_col = "yearmonth"
elif time_period == "Quarterly":
    groupby_col = "yearquarter"
else:  # Yearly
    groupby_col = "year"

# Get aggregated data
total_registrations = data_processor.get_total_registrations(filtered_data, groupby=groupby_col)
registrations_by_category = data_processor.get_registrations_by_category(filtered_data, groupby=groupby_col)
registrations_by_manufacturer = data_processor.get_registrations_by_manufacturer(filtered_data, groupby=groupby_col)

# Calculate YoY and QoQ growth
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
    # Create a copy of the dataframes with year extracted from yearmonth
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
    # This is a simplification - in a real app, we'd handle this more elegantly
    has_qoq = False

# Dashboard layout
col1, col2 = st.columns(2)

# Total registrations over time
with col1:
    st.markdown('<h2 class="sub-header">Total Vehicle Registrations</h2>', unsafe_allow_html=True)
    
    fig = px.line(
        total_registrations, 
        x=groupby_col, 
        y="registrations",
        markers=True,
        title="Total Registrations Over Time"
    )
    fig.update_layout(height=400, xaxis_title="Time Period", yaxis_title="Registrations")
    st.plotly_chart(fig, use_container_width=True)

# YoY Growth
with col2:
    st.markdown('<h2 class="sub-header">Year-over-Year Growth</h2>', unsafe_allow_html=True)
    
    # Filter out NaN values (first year has no YoY growth)
    yoy_data = total_yoy.dropna(subset=["yoy_growth"])
    
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

# Registrations by vehicle type
st.markdown('<h2 class="sub-header">Analysis by Vehicle Type</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
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

with col2:
    # YoY growth by vehicle type
    if len(selected_vehicle_types) > 0:
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

# QoQ Growth section (only for quarterly data)
if has_qoq:
    st.markdown('<h2 class="sub-header">Quarter-over-Quarter Analysis</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # QoQ growth for total registrations
        qoq_data = total_qoq.dropna(subset=["qoq_growth"])
        qoq_data["period"] = qoq_data["year"].astype(str) + "-Q" + qoq_data["quarter"].astype(str)
        
        fig = px.bar(
            qoq_data,
            x="period",
            y="qoq_growth",
            title="QoQ Growth in Total Registrations",
            color="qoq_growth",
            color_continuous_scale=["red", "green"],
            range_color=[-20, 20]
        )
        fig.update_layout(height=400, xaxis_title="Quarter", yaxis_title="QoQ Growth (%)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # QoQ growth by vehicle type
        if len(selected_vehicle_types) > 0:
            category_qoq_filtered = category_qoq.dropna(subset=["qoq_growth"])
            category_qoq_filtered["period"] = category_qoq_filtered["year"].astype(str) + "-Q" + category_qoq_filtered["quarter"].astype(str)
            
            fig = px.line(
                category_qoq_filtered,
                x="period",
                y="qoq_growth",
                color="vehicle_type",
                title="QoQ Growth by Vehicle Type",
                markers=True
            )
            fig.update_layout(height=400, xaxis_title="Quarter", yaxis_title="QoQ Growth (%)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Please select at least one vehicle type to see QoQ growth comparison.")

# Manufacturer Analysis
st.markdown('<h2 class="sub-header">Manufacturer Analysis</h2>', unsafe_allow_html=True)

# Top manufacturers by registrations
top_manufacturers = registrations_by_manufacturer.groupby("manufacturer")["registrations"].sum().nlargest(10).reset_index()

col1, col2 = st.columns(2)

with col1:
    fig = px.bar(
        top_manufacturers,
        x="manufacturer",
        y="registrations",
        title="Top 10 Manufacturers by Total Registrations",
        color="registrations",
        color_continuous_scale="Viridis"
    )
    fig.update_layout(height=400, xaxis_title="Manufacturer", yaxis_title="Total Registrations")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Manufacturer market share
    fig = px.pie(
        top_manufacturers,
        values="registrations",
        names="manufacturer",
        title="Market Share of Top 10 Manufacturers"
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# Manufacturer growth analysis
if selected_manufacturers:
    st.markdown('<h3 class="sub-header">Selected Manufacturer Growth Analysis</h3>', unsafe_allow_html=True)
    
    # Filter YoY data for selected manufacturers
    selected_mfr_yoy = manufacturer_yoy[
        manufacturer_yoy["manufacturer"].isin(selected_manufacturers)
    ].dropna(subset=["yoy_growth"])
    
    if not selected_mfr_yoy.empty:
        fig = px.line(
            selected_mfr_yoy,
            x="year",
            y="yoy_growth",
            color="manufacturer",
            title="YoY Growth by Selected Manufacturers",
            markers=True
        )
        fig.update_layout(height=400, xaxis_title="Year", yaxis_title="YoY Growth (%)")
        st.plotly_chart(fig, use_container_width=True)
        
        if has_qoq:
            # Filter QoQ data for selected manufacturers
            selected_mfr_qoq = manufacturer_qoq[
                manufacturer_qoq["manufacturer"].isin(selected_manufacturers)
            ].dropna(subset=["qoq_growth"])
            
            selected_mfr_qoq["period"] = selected_mfr_qoq["year"].astype(str) + "-Q" + selected_mfr_qoq["quarter"].astype(str)
            
            fig = px.line(
                selected_mfr_qoq,
                x="period",
                y="qoq_growth",
                color="manufacturer",
                title="QoQ Growth by Selected Manufacturers",
                markers=True
            )
            fig.update_layout(height=400, xaxis_title="Quarter", yaxis_title="QoQ Growth (%)")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No growth data available for the selected manufacturers in the current time range.")
else:
    st.info("Please select manufacturers to see their growth analysis.")

# Key metrics and insights
st.markdown('<h2 class="sub-header">Key Metrics & Insights</h2>', unsafe_allow_html=True)

# Calculate key metrics
total_vehicles = filtered_data["registrations"].sum()

# Get the latest period data for YoY calculation
if time_period == "Yearly":
    latest_year = total_yoy["year"].max()
    latest_yoy = total_yoy[total_yoy["year"] == latest_year]["yoy_growth"].values[0] if not total_yoy.empty else np.nan
    
    # Get YoY by vehicle type for the latest year
    latest_category_yoy = {}
    for vtype in selected_vehicle_types:
        type_data = category_yoy[(category_yoy["vehicle_type"] == vtype) & (category_yoy["year"] == latest_year)]
        if not type_data.empty:
            latest_category_yoy[vtype] = type_data["yoy_growth"].values[0]
        else:
            latest_category_yoy[vtype] = np.nan
else:
    # For quarterly/monthly, get the latest year's YoY since we're now using year for YoY calculations
    latest_year = total_yoy["year"].max()
    latest_yoy_data = total_yoy[total_yoy["year"] == latest_year]
    latest_yoy = latest_yoy_data["yoy_growth"].values[0] if not latest_yoy_data.empty else np.nan
    
    # Get YoY by vehicle type for the latest year
    latest_category_yoy = {}
    for vtype in selected_vehicle_types:
        type_data = category_yoy[(category_yoy["vehicle_type"] == vtype) & (category_yoy["year"] == latest_year)]
        if not type_data.empty:
            latest_category_yoy[vtype] = type_data["yoy_growth"].values[0]
        else:
            latest_category_yoy[vtype] = np.nan

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
    if has_qoq:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-label">Latest QoQ Growth</p>', unsafe_allow_html=True)
        
        latest_qoq_period = total_qoq["period_num"].max()
        latest_qoq_data = total_qoq[total_qoq["period_num"] == latest_qoq_period]
        latest_qoq = latest_qoq_data["qoq_growth"].values[0] if not latest_qoq_data.empty else np.nan
        
        if not np.isnan(latest_qoq):
            color_class = "growth-positive" if latest_qoq >= 0 else "growth-negative"
            st.markdown(f'<p class="metric-value {color_class}">{latest_qoq:.1f}%</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="metric-value">N/A</p>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Vehicle Type Breakdown</p>', unsafe_allow_html=True)
        
        vehicle_counts = filtered_data.groupby("vehicle_type")["registrations"].sum()
        top_type = vehicle_counts.idxmax()
        top_pct = (vehicle_counts[top_type] / vehicle_counts.sum()) * 100
        
        st.markdown(f'<p class="metric-value">{top_type}: {top_pct:.1f}%</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Vehicle type YoY growth cards
st.markdown('<h3 class="sub-header">YoY Growth by Vehicle Type</h3>', unsafe_allow_html=True)

cols = st.columns(len(selected_vehicle_types) if selected_vehicle_types else 1)

if selected_vehicle_types:
    for i, vtype in enumerate(selected_vehicle_types):
        with cols[i]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f'<p class="metric-label">{vtype}</p>', unsafe_allow_html=True)
            
            if vtype in latest_category_yoy and not np.isnan(latest_category_yoy[vtype]):
                color_class = "growth-positive" if latest_category_yoy[vtype] >= 0 else "growth-negative"
                st.markdown(f'<p class="metric-value {color_class}">{latest_category_yoy[vtype]:.1f}%</p>', unsafe_allow_html=True)
            else:
                st.markdown('<p class="metric-value">N/A</p>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("Please select vehicle types to see their YoY growth.")

# Footer
st.markdown('<div class="footer">Vehicle Registration Dashboard | Data Source: Vahan Dashboard (Synthetic Data)</div>', unsafe_allow_html=True)