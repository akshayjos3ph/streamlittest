import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Streamlit app title
st.title('Solar Generation in Germany')

# Function to load data from a CSV file
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path, parse_dates=['cet_cest_timestamp'], index_col='cet_cest_timestamp')
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Path to the CSV file
file_path = './ForecastOutput.csv'

# Load the dataset
df = load_data(file_path)

if df is not None:
    # Filtering the dataset for solar generation data in Germany
    solar_data = df['DE_solar_generation_actual']
    # Resampling data to daily frequency
    daily_solar = solar_data.resample('D').sum()

    # Plotting the data
    st.subheader('Daily Solar Generation Actual')
    st.line_chart(daily_solar)

    # Plotting raw data
    st.subheader('Solar Generation Data')
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(daily_solar, label='Observed')
    ax.legend()
    st.pyplot(fig)
else:
    st.info('Failed to load data. Please check the file and try again.')
