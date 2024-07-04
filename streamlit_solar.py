import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import nbformat
from nbconvert import PythonExporter

# Streamlit app title
st.title('Solar Generation in Germany: Actual vs Predicted')

# Function to extract data from Jupyter notebooks
def extract_data_from_notebook(notebook_path):
    with open(notebook_path) as f:
        nb = nbformat.read(f, as_version=4)
    exporter = PythonExporter()
    source, _ = exporter.from_notebook_node(nb)
    return source

# Extracting data and model parameters from the notebooks
model_notebook_path = '/mnt/data/ModelSolar.ipynb'
data_notebook_path = '/mnt/data/DataSolar.ipynb'

model_code = extract_data_from_notebook(model_notebook_path)
data_code = extract_data_from_notebook(data_notebook_path)

# Executing the code to get the data and model parameters
exec(model_code)
exec(data_code)

# Assuming the data and model parameters are now available in variables like `df`, `sarima_order`, and `sarima_seasonal_order`
# (Make sure the notebooks save data into these variables or adjust the code accordingly)

# Example of how you might access the variables
# df = pd.DataFrame(...)  # Replace with the actual data extraction code from the notebook
# sarima_order = (1, 1, 1)  # Replace with actual SARIMA order from the notebook
# sarima_seasonal_order = (1, 1, 1, 12)  # Replace with actual SARIMA seasonal order from the notebook

if 'df' in locals():
    # Display the SARIMA model parameters
    st.subheader('SARIMA Model Parameters')
    if 'sarima_order' in locals() and 'sarima_seasonal_order' in locals():
        st.write(f"Order: {sarima_order}")
        st.write(f"Seasonal Order: {sarima_seasonal_order}")
    else:
        st.write("SARIMA model parameters not found in the dataset.")

    # Filtering the dataset for solar generation data in Germany
    solar_data_actual = df['DE_solar_generation_actual']
    solar_data_predicted = df['DE_solar_generation_predicted'] if 'DE_solar_generation_predicted' in df.columns else None
    
    # Resampling data to daily frequency
    daily_solar_actual = solar_data_actual.resample('D').sum()
    daily_solar_predicted = solar_data_predicted.resample('D').sum() if solar_data_predicted is not None else None

    # Plotting the actual data
    st.subheader('Daily Solar Generation Actual')
    st.line_chart(daily_solar_actual)

    if daily_solar_predicted is not None:
        # Plotting the actual and predicted data
        st.subheader('Daily Solar Generation: Actual vs Predicted')
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(daily_solar_actual, label='Observed')
        ax.plot(daily_solar_predicted, label='Predicted', linestyle='--')
        ax.legend()
        st.pyplot(fig)
else:
    st.info('Failed to load data. Please check the notebooks and try again.')
