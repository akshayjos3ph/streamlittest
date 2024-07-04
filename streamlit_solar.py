"""
Author: Akshay Joseph
Version: 1.0
Date: 2024-07-04
Description: This script creates a Streamlit dashboard to fetch and forecast solar energy generation data for the next 14 days.
"""

import streamlit as st
import pandas as pd
import datetime
from fetch_solar_data import fetch_solar_data
from forecast_solar_data import forecast_solar_data

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

def forecast_data(file_path, output_file_path):
    """
    Generate a solar forecast based on the provided data for the next 14 days.

    Args:
        file_path (str): Path to the input data file.
        output_file_path (str): Path to the output forecast file.

    Returns:
        pd.DataFrame: The solar forecast data.
    """
    forecast_solar_data(input_file_path=file_path, output_file_path=output_file_path, forecast_column='solar_actual', unit='MWh')
    return load_data(output_file_path)

def main():
    """
    Main function to run the Streamlit app.
    """
    st.title("Solar Forecast Dashboard")

    data_file_path = 'DE_solar_energy_last_1_month.csv'
    forecast_file_path = 'forecasted_solar_energy.csv'
    
    # Check if data needs to be updated
    if 'last_update' not in st.session_state:
        st.session_state['last_update'] = None

    data_source = "None"
    
    if st.button("Update Data"):
        api_key = st.secrets['api_key']  # Fetch the API key from Streamlit secrets
        data_fetched = fetch_solar_data(api_key, filename=data_file_path)
        if data_fetched:
            forecast = forecast_data(data_file_path, forecast_file_path)
            save_forecast(forecast, forecast_file_path)
            st.session_state['last_update'] = datetime.datetime.now()
            st.session_state['forecast'] = forecast
            st.success("Data updated and forecast saved successfully!")
            data_source = "API"
        else:
            st.error("Failed to load data from API.")
            forecast = load_data(forecast_file_path)
            if forecast is not None:
                st.session_state['forecast'] = forecast
                data_source = "Local file"
            else:
                st.error("Failed to load forecast data from local file.")
                st.session_state['forecast'] = None
                data_source = "None"
    else:
        forecast = load_data(forecast_file_path)
        if forecast is not None:
            st.session_state['forecast'] = forecast
            data_source = "Local file"

    df = load_data(data_file_path)
    if df is not None:
        st.subheader("Latest Solar Data")
        st.write(df.iloc[-1])  # Display only the last updated value

    if 'forecast' in st.session_state and st.session_state['forecast'] is not None:
        st.write(f"Last updated: {st.session_state['last_update'].strftime('%Y-%m-%d %H:%M:%S') if st.session_state['last_update'] else 'Never'} (Source: {data_source})")
        st.subheader("Solar Forecast Data")
        st.write(st.session_state['forecast'].iloc[-1])  # Display only the last forecast value

        # Debugging output to check DataFrame columns
        st.write("Forecast DataFrame Columns:", st.session_state['forecast'].columns)

        # Check if 'datetime_Europe_Brussels' is in columns
        if 'datetime_Europe_Brussels' in st.session_state['forecast'].columns:
            # Plot the forecast data
            st.line_chart(st.session_state['forecast'].set_index('datetime_Europe_Brussels')['Forecast (MWh)'])
        else:
            st.error("'datetime_Europe_Brussels' column is missing in the forecast data.")
    else:
        st.warning("No forecast data available. Click 'Update Data' to load data.")

if __name__ == "__main__":
    main()
