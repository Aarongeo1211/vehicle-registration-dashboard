import pandas as pd
import numpy as np

class VehicleDataProcessor:
    def __init__(self, data_path=None):
        """
        Initialize the data processor with the path to the vehicle registration data.
        
        Parameters:
        -----------
        data_path : str
            Path to the CSV file containing vehicle registration data. If None, will try to find
            available data files in the data directory.
        """
        import os
        
        if data_path is None:
            # Try to find available data files
            scraped_data_path = 'data/vehicle_registrations_scraped.csv'
            synthetic_data_path = 'data/vehicle_registrations.csv'
            
            if os.path.exists(scraped_data_path):
                self.data_path = scraped_data_path
                print(f"Using scraped data from {scraped_data_path}")
            elif os.path.exists(synthetic_data_path):
                self.data_path = synthetic_data_path
                print(f"Using synthetic data from {synthetic_data_path}")
            else:
                raise FileNotFoundError("No vehicle registration data found. Please generate or scrape data first.")
        else:
            self.data_path = data_path
            
        self.df = None
        self.load_data()
    
    def load_data(self):
        """
        Load the vehicle registration data from CSV file.
        """
        self.df = pd.read_csv(self.data_path)
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df['year'] = self.df['date'].dt.year
        self.df['quarter'] = self.df['date'].dt.quarter
        self.df['month'] = self.df['date'].dt.month
        self.df['yearquarter'] = self.df['year'].astype(str) + '-Q' + self.df['quarter'].astype(str)
        self.df['yearmonth'] = self.df['date'].dt.strftime('%Y-%m')
    
    def filter_data(self, start_date=None, end_date=None, vehicle_types=None, manufacturers=None):
        """
        Filter the data based on date range, vehicle types, and manufacturers.
        
        Parameters:
        -----------
        start_date : str or datetime
            Start date for filtering (inclusive)
        end_date : str or datetime
            End date for filtering (inclusive)
        vehicle_types : list
            List of vehicle types to include
        manufacturers : list
            List of manufacturers to include
            
        Returns:
        --------
        pandas.DataFrame
            Filtered dataframe
        """
        filtered_df = self.df.copy()
        
        if start_date:
            filtered_df = filtered_df[filtered_df['date'] >= pd.to_datetime(start_date)]
        
        if end_date:
            filtered_df = filtered_df[filtered_df['date'] <= pd.to_datetime(end_date)]
        
        if vehicle_types:
            filtered_df = filtered_df[filtered_df['vehicle_type'].isin(vehicle_types)]
        
        if manufacturers:
            filtered_df = filtered_df[filtered_df['manufacturer'].isin(manufacturers)]
        
        return filtered_df
    
    def get_total_registrations(self, filtered_df=None, groupby='yearmonth'):
        """
        Get total registrations grouped by a time period.
        
        Parameters:
        -----------
        filtered_df : pandas.DataFrame
            Pre-filtered dataframe, if None, uses the full dataset
        groupby : str
            Time period to group by ('year', 'yearquarter', 'yearmonth')
            
        Returns:
        --------
        pandas.DataFrame
            Dataframe with total registrations by time period
        """
        if filtered_df is None:
            filtered_df = self.df
        
        return filtered_df.groupby(groupby)['registrations'].sum().reset_index()
    
    def get_registrations_by_category(self, filtered_df=None, groupby='yearmonth'):
        """
        Get registrations grouped by vehicle type and time period.
        
        Parameters:
        -----------
        filtered_df : pandas.DataFrame
            Pre-filtered dataframe, if None, uses the full dataset
        groupby : str
            Time period to group by ('year', 'yearquarter', 'yearmonth')
            
        Returns:
        --------
        pandas.DataFrame
            Dataframe with registrations by vehicle type and time period
        """
        if filtered_df is None:
            filtered_df = self.df
        
        return filtered_df.groupby([groupby, 'vehicle_type'])['registrations'].sum().reset_index()
    
    def get_registrations_by_manufacturer(self, filtered_df=None, groupby='yearmonth'):
        """
        Get registrations grouped by manufacturer and time period.
        
        Parameters:
        -----------
        filtered_df : pandas.DataFrame
            Pre-filtered dataframe, if None, uses the full dataset
        groupby : str
            Time period to group by ('year', 'yearquarter', 'yearmonth')
            
        Returns:
        --------
        pandas.DataFrame
            Dataframe with registrations by manufacturer and time period
        """
        if filtered_df is None:
            filtered_df = self.df
        
        return filtered_df.groupby([groupby, 'manufacturer'])['registrations'].sum().reset_index()
    
    def calculate_yoy_growth(self, data, time_col, value_col='registrations', group_col=None):
        """
        Calculate Year-over-Year (YoY) growth.
        
        Parameters:
        -----------
        data : pandas.DataFrame
            Dataframe containing time series data
        time_col : str
            Column name containing time periods
        value_col : str
            Column name containing values to calculate growth for
        group_col : str
            Column name for grouping (e.g., 'vehicle_type', 'manufacturer')
            
        Returns:
        --------
        pandas.DataFrame
            Dataframe with YoY growth calculations
        """
        # Extract year from time column if it's in a format like '2022-Q1' or '2022-01'
        if 'year' not in time_col.lower():
            data = data.copy()
            if 'Q' in str(data[time_col].iloc[0]):
                data['year'] = data[time_col].str.split('-').str[0].astype(int)
            else:
                data['year'] = pd.to_datetime(data[time_col]).dt.year
        else:
            data = data.copy()
            data['year'] = data[time_col]
        
        # Group by year and optional group column
        if group_col:
            yearly_data = data.groupby(['year', group_col])[value_col].sum().reset_index()
            # Calculate YoY growth for each group
            result = []
            for group in yearly_data[group_col].unique():
                group_data = yearly_data[yearly_data[group_col] == group].sort_values('year')
                # Convert year to integer if it's a string
                if isinstance(group_data['year'].iloc[0], str):
                    group_data['year'] = group_data['year'].astype(int)
                group_data['previous_year'] = group_data['year'] - 1
                group_data = pd.merge(
                    group_data, 
                    group_data[['year', value_col]].rename(columns={value_col: f'prev_{value_col}', 'year': 'previous_year'}),
                    on='previous_year',
                    how='left'
                )
                group_data['yoy_growth'] = ((group_data[value_col] - group_data[f'prev_{value_col}']) / 
                                           group_data[f'prev_{value_col}'] * 100)
                result.append(group_data)
            return pd.concat(result)
        else:
            yearly_data = data.groupby('year')[value_col].sum().reset_index()
            yearly_data = yearly_data.sort_values('year')
            # Convert year to integer if it's a string
            if isinstance(yearly_data['year'].iloc[0], str):
                yearly_data['year'] = yearly_data['year'].astype(int)
            yearly_data['previous_year'] = yearly_data['year'] - 1
            yearly_data = pd.merge(
                yearly_data, 
                yearly_data[['year', value_col]].rename(columns={value_col: f'prev_{value_col}', 'year': 'previous_year'}),
                on='previous_year',
                how='left'
            )
            yearly_data['yoy_growth'] = ((yearly_data[value_col] - yearly_data[f'prev_{value_col}']) / 
                                       yearly_data[f'prev_{value_col}'] * 100)
            return yearly_data
    
    def calculate_qoq_growth(self, data, time_col, value_col='registrations', group_col=None):
        """
        Calculate Quarter-over-Quarter (QoQ) growth.
        
        Parameters:
        -----------
        data : pandas.DataFrame
            Dataframe containing time series data
        time_col : str
            Column name containing time periods (must be in format 'YYYY-QN')
        value_col : str
            Column name containing values to calculate growth for
        group_col : str
            Column name for grouping (e.g., 'vehicle_type', 'manufacturer')
            
        Returns:
        --------
        pandas.DataFrame
            Dataframe with QoQ growth calculations
        """
        # Ensure time_col is in the correct format
        if 'Q' not in str(data[time_col].iloc[0]):
            raise ValueError("Time column must be in format 'YYYY-QN' for QoQ calculations")
        
        data = data.copy()
        
        # Extract year and quarter
        data['year'] = data[time_col].str.split('-').str[0].astype(int)
        data['quarter'] = data[time_col].str.split('Q').str[1].astype(int)
        
        # Create a numeric representation for sorting
        data['period_num'] = data['year'] * 10 + data['quarter']
        
        # Group by period and optional group column
        if group_col:
            quarterly_data = data.groupby(['period_num', 'year', 'quarter', group_col])[value_col].sum().reset_index()
            # Calculate QoQ growth for each group
            result = []
            for group in quarterly_data[group_col].unique():
                group_data = quarterly_data[quarterly_data[group_col] == group].sort_values('period_num')
                group_data['previous_period'] = group_data['period_num'] - 1
                # Handle year boundary (Q4 to Q1)
                group_data.loc[group_data['quarter'] == 1, 'previous_period'] = \
                    (group_data.loc[group_data['quarter'] == 1, 'year'] - 1) * 10 + 4
                
                group_data = pd.merge(
                    group_data, 
                    group_data[['period_num', value_col]].rename(columns={value_col: f'prev_{value_col}', 'period_num': 'previous_period'}),
                    on='previous_period',
                    how='left'
                )
                group_data['qoq_growth'] = ((group_data[value_col] - group_data[f'prev_{value_col}']) / 
                                           group_data[f'prev_{value_col}'] * 100)
                result.append(group_data)
            return pd.concat(result)
        else:
            quarterly_data = data.groupby(['period_num', 'year', 'quarter'])[value_col].sum().reset_index()
            quarterly_data = quarterly_data.sort_values('period_num')
            quarterly_data['previous_period'] = quarterly_data['period_num'] - 1
            # Handle year boundary (Q4 to Q1)
            quarterly_data.loc[quarterly_data['quarter'] == 1, 'previous_period'] = \
                (quarterly_data.loc[quarterly_data['quarter'] == 1, 'year'] - 1) * 10 + 4
            
            quarterly_data = pd.merge(
                quarterly_data, 
                quarterly_data[['period_num', value_col]].rename(columns={value_col: f'prev_{value_col}', 'period_num': 'previous_period'}),
                on='previous_period',
                how='left'
            )
            quarterly_data['qoq_growth'] = ((quarterly_data[value_col] - quarterly_data[f'prev_{value_col}']) / 
                                         quarterly_data[f'prev_{value_col}'] * 100)
            return quarterly_data
    
    def get_vehicle_types(self):
        """
        Get list of all vehicle types in the dataset.
        
        Returns:
        --------
        list
            List of vehicle types
        """
        return sorted(self.df['vehicle_type'].unique())
    
    def get_manufacturers(self, vehicle_type=None):
        """
        Get list of all manufacturers in the dataset, optionally filtered by vehicle type.
        
        Parameters:
        -----------
        vehicle_type : str
            Vehicle type to filter manufacturers by
            
        Returns:
        --------
        list
            List of manufacturers
        """
        if vehicle_type:
            return sorted(self.df[self.df['vehicle_type'] == vehicle_type]['manufacturer'].unique())
        return sorted(self.df['manufacturer'].unique())
    
    def get_date_range(self):
        """
        Get the min and max dates in the dataset.
        
        Returns:
        --------
        tuple
            (min_date, max_date)
        """
        return (self.df['date'].min(), self.df['date'].max())