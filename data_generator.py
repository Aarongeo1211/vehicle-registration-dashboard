import pandas as pd
import numpy as np
import os
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
            manufacturer_factor = np.random.uniform(0.5, 1.5, 1)[0]
            
            # Calculate registrations with some randomness
            registrations = int(base_registrations * yearly_factor * quarterly_factor * 
                               day_factor * category_factor * manufacturer_factor * 
                               np.random.uniform(0.8, 1.2, 1)[0])
            
            # Add special events/promotions randomly
            if np.random.random() < 0.01:  # 1% chance of a promotion
                registrations = int(registrations * np.random.uniform(1.5, 2.5, 1)[0])
            
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

print(f"Generated {len(df)} records of synthetic vehicle registration data from {start_date.date()} to {end_date.date()}")

# Display sample
print("\nSample data:")
print(df.sample(10))

# Summary statistics
print("\nSummary by vehicle type:")
print(df.groupby('vehicle_type')['registrations'].agg(['count', 'sum', 'mean', 'min', 'max']))

print("\nSummary by manufacturer:")
print(df.groupby('manufacturer')['registrations'].agg(['count', 'sum', 'mean']))

print("\nSummary by year:")
print(df.groupby(df['date'].dt.year)['registrations'].agg(['count', 'sum', 'mean']))