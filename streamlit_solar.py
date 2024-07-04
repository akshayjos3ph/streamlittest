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

from fetch_solar_data import fetch_solar_data
from get_solar_forecast import get_solar_forecast

def load_data(file_path):
    """
    Load data from a CSV file.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        pd.DataFrame: The loaded data as a DataFrame.
    """
    try:
        df = pd.read_csv(file_path, parse_dates=['datetime_Europe_Brussels'], index_col='datetime_Europe_Brussels')
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
        forecast (pd.DataFrame): The forecast data.
        file_path (str): The path to the CSV file.
    """
    forecast.to_csv(file_path)

def forecast_data(data):
    """
    Generate a solar forecast based on the provided data for the next 14 weeks.

    Args:
        data (pd.DataFrame): The solar data fetched from the API.

    Returns:
        pd.DataFrame: The solar forecast data.
    """
    return get_solar_forecast(data, weeks=14)

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

    if st.button("Update Data"):
        data = fetch_solar_data(st.secrets["api"]["key"])
        if data is not None:
            df_data = pd.DataFrame(data)
            forecast = forecast_data(df_data)
            save_forecast(forecast, forecast_file_path)
            st.session_state['last_update'] = datetime.datetime.now()
            st.session_state['forecast'] = forecast
            st.success("Data updated and forecast saved successfully!")
        else:
            st.error("Failed to load data.")
            st.session_state['forecast'] = load_data(forecast_file_path)

    df = load_data(data_file_path)
    if df is not None:
        st.subheader("Latest Solar Data")
        st.dataframe(df.head())

    if 'forecast' in st.session_state and st.session_state['forecast'] is not None:
        st.write("Last updated:", st.session_state['last_update'].strftime("%Y-%m-%d %H:%M:%S") if st.session_state['last_update'] else "Never")
        st.subheader("Solar Forecast Data")
        st.dataframe(st.session_state['forecast'])
    else:
        st.warning("No forecast data available. Click 'Update Data' to load data.")

if __name__ == "__main__":
    main()
