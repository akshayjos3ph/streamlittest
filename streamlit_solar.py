"""
Author: Akshay Joseph
Version: 1.0
Date: 2024-07-04
Description: This script creates a Streamlit dashboard to fetch and forecast solar energy generation data for the next 14 days.
"""

import streamlit as st
import pandas as pd
import altair as alt

# Load data
@st.cache
def load_data(file_path):
    data = pd.read_csv(file_path)
    data['datetime_Europe_Brussels'] = pd.to_datetime(data['datetime_Europe_Brussels'])
    return data

# File path
file_path = 'forecasted_solar_energy.csv'

# Load data
data = load_data(file_path)

# Title and description
st.title('14-Day Solar Energy Forecast')
st.write('This dashboard shows the forecast of solar energy for the next 14 days in MWh.')

# Plotting
chart = alt.Chart(data).mark_bar().encode(
    x='datetime_Europe_Brussels:T',
    y='Forecast (MWh):Q',
    tooltip=['datetime_Europe_Brussels', 'Forecast (MWh)']
).properties(
    title='14-Day Solar Energy Forecast'
)

st.altair_chart(chart, use_container_width=True)

