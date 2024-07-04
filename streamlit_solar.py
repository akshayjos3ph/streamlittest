import streamlit as st
import pandas as pd

@st.cache_data
def load_data(file_path):
    try:
        # Load the CSV file and parse dates
        df = pd.read_csv(file_path, parse_dates=['cet_cest_timestamp'], index_col='cet_cest_timestamp')
        
        # Check if 'DE_solar_generation_actual' column exists
        if 'DE_solar_generation_actual' not in df.columns:
            st.error("The file does not contain a 'DE_solar_generation_actual' column.")
            return None
        
        return df
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Define the file path to your CSV file
file_path = "path_to_your_csv_file.csv"

# Load the data
df = load_data(file_path)

# Check if data is loaded successfully
if df is not None:
    st.write("Data loaded successfully.")
    st.write(df.head())
else:
    st.write("Data could not be loaded.")
