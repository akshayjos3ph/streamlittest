"""
Author: Akshay Joseph
Version: 1.0
Date: 2024-07-04
Description: This script creates a Streamlit dashboard to fetch and forecast solar energy generation data for the next 14 days.
"""
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from fetch_solar_data import fetch_solar_data  # Import the fetch function
from forecast_solar_data import forecast_solar_data  # Import the forecast function

# Title and description
st.title('Next 14-Day Solar Energy Forecast')
st.write('This dashboard shows the forecast of solar energy for the next 14 days in MWh.')

# Load data
@st.cache_resource
def load_data(file_path):
    data = pd.read_csv(file_path)
    data['datetime_Europe_Brussels'] = pd.to_datetime(data['datetime_Europe_Brussels'])
    return data

# Function to fetch and save solar data
def fetch_and_forecast_solar_data():
    api_key = st.secrets["api_key"]
    fetch_solar_data(api_key)
    forecast_solar_data('DE_solar_energy_last_1_month.csv', 'forecasted_solar_energy.csv', 'solar_actual_MWh', 'MWh')
    st.session_state['fetch_date'] = datetime.now()

# File path for forecast data
forecast_file_path = 'forecasted_solar_energy.csv'

# Load forecast data
forecast_data = load_data(forecast_file_path)

# Plotting the forecast data
chart = alt.Chart(forecast_data).mark_bar().encode(
    x='datetime_Europe_Brussels:T',
    y='Forecast (MWh):Q',
    tooltip=['datetime_Europe_Brussels', 'Forecast (MWh)']
).properties(
    title='14-Day Solar Energy Forecast'
)

st.altair_chart(chart, use_container_width=True)

# Button to fetch the solar data and update forecast
if st.button('Update Data'):
    fetch_and_forecast_solar_data()

# Display last fetch date
if 'fetch_date' in st.session_state:
    fetch_date = st.session_state['fetch_date']
    st.markdown(f"<p style='font-size: small;'>Last data fetch date: {fetch_date.strftime('%Y-%m-%d %H:%M:%S')}</p>", unsafe_allow_html=True)
