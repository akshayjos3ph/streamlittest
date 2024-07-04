"""
Author: Akshay Joseph
Version: 1.0
Date: 2024-07-04
Description: This script creates a Streamlit dashboard to fetch and forecast solar energy generation data for the next 14 weeks.
"""

import streamlit as st
import pandas as pd
import os
import datetime

from solar_forecast import get_solar_forecast
from fetch_and_save_solar_data import get_data

def load_data(file_path):
    """
    Load data from a CSV file.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        pd.DataFrame: The loaded data as a DataFrame.
    """
    try:
        df = pd.read_csv(file_path, parse_dates=['utc_timestamp'], index_col='utc_timestamp')
        return df
    except FileNotFoundError:
        st.error(f"The file {file_path} was not found.")
        return None
    except ValueError as e:
        st.error(f"Error parsing the CSV file: {e}")
        return None

def save_forecast(forecast, file_path):
    """
    Save forecast data to a CSV file.

    Args:
        forecast (list): The forecast data.
        file_path (str): The path to the CSV file.
    """
    df = pd.DataFrame(forecast)
    df.to_csv(file_path, index=False)

def forecast_data(data):
    """
    Generate a solar forecast based on the provided data for the next 14 weeks.

    Args:
        data (dict): The solar data fetched from the API.

    Returns:
        list: The solar forecast data.
    """
    return get_solar_forecast(data, weeks=14)

def is_update_needed(last_update_time, interval_hours=1):
    """
    Check if the data needs to be updated based on the specified interval.

    Args:
        last_update_time (datetime): The timestamp of the last update.
        interval_hours (int): The interval in hours to determine if an update is needed.

    Returns:
        bool: True if an update is needed, False otherwise.
    """
    now = datetime.datetime.now()
    if last_update_time is None:
        return True
    elapsed_time = now - last_update_time
    return elapsed_time.total_seconds() >= interval_hours * 3600

def main():
    """
    Main function to run the Streamlit app.
    """
    st.title("Solar Forecast Dashboard")

    data_file_path = 'DE_solar_energy_last_14_days.csv'
    forecast_file_path = 'forecasted_solar_energy.csv'
    
    # Check if data needs to be updated
    if 'last_update' not in st.session_state:
        st.session_state['last_update'] = None

    if st.button("Update Data") or is_update_needed(st.session_state['last_update']):
        data = get_data(st.secrets["api"]["key"])
        if data:
            forecast = forecast_data(data)
            save_forecast(forecast, forecast_file_path)
            st.session_state['last_update'] = datetime.datetime.now()
            st.session_state['forecast'] = forecast
            st.success("Data updated and forecast saved successfully!")
        else:
            st.error("Failed to load data.")

    df = load_data(data_file_path)
    if df is not None:
        st.dataframe(df.head())

    if 'forecast' in st.session_state:
        st.write("Last updated:", st.session_state['last_update'].strftime("%Y-%m-%d %H:%M:%S"))
        st.dataframe(pd.DataFrame(st.session_state['forecast']))
    else:
        st.warning("No forecast data available. Click 'Update Data' to load data.")

if __name__ == "__main__":
    main()
