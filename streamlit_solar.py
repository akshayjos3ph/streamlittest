"""
Author: Akshay Joseph
Version: 1.0
Date: 2024-07-04
Description: This script creates a Streamlit dashboard to fetch and forecast solar energy generation data.
"""

import streamlit as st
import datetime
import pandas as pd
from solar_forecast import get_solar_forecast
from fetch_and_save_solar_data import get_data

def load_data():
    """
    Load data using the provided API key from Streamlit secrets.

    Returns:
        data (dict): The solar data fetched from the API or None if an error occurs.
    """
    api_key = st.secrets["api"]["key"]
    if not api_key:
        st.error("API key is not set. Please set the API key in the secrets.toml file.")
        return None
    return get_data(api_key)

def forecast_data(data):
    """
    Generate a solar forecast based on the provided data.

    Args:
        data (dict): The solar data fetched from the API.

    Returns:
        forecast (list): The solar forecast data.
    """
    return get_solar_forecast(data)

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

    # Check if data needs to be updated
    if 'last_update' not in st.session_state:
        st.session_state['last_update'] = None

    if st.button("Update Data") or is_update_needed(st.session_state['last_update']):
        data = load_data()
        if data:
            forecast = forecast_data(data)
            st.session_state['last_update'] = datetime.datetime.now()
            st.session_state['forecast'] = forecast
            st.success("Data updated successfully!")
        else:
            st.error("Failed to load data.")

    if 'forecast' in st.session_state:
        st.write("Last updated:", st.session_state['last_update'].strftime("%Y-%m-%d %H:%M:%S"))
        st.dataframe(pd.DataFrame(st.session_state['forecast']))
    else:
        st.warning("No forecast data available. Click 'Update Data' to load data.")

if __name__ == "__main__":
    main()
