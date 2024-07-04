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
    # Display the first few rows of the dataframe for debugging purposes
    st.write("Data Preview:")
    st.write(df.head())

    # Filtering the dataset for solar generation data in Germany
    solar_data = df['DE_solar_generation_actual']
    # Resampling data to daily frequency
    daily_solar = solar_data.resample('D').sum()

    # Plotting the data
    st.subheader('Daily Solar Generation Actual')
    st.line_chart(daily_solar)

    # Adding a simple moving average for better visualization
    st.subheader('Daily Solar Generation with 7-Day Moving Average')
    daily_solar_7ma = daily_solar.rolling(window=7).mean()
    st.line_chart(daily_solar_7ma)

    # Plotting raw data and moving average together
    st.subheader('Solar Generation Data with Moving Average')
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(daily_solar, label='Observed')
    ax.plot(daily_solar_7ma, label='7-Day Moving Average', color='orange')
    ax.legend()
    st.pyplot(fig)
else:
    st.info('Failed to load data. Please check the file and try again.')
