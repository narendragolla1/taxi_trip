# import streamlit as st
# import pandas as pd
# import requests
# import json

# st.title("Taxi Trip Data Explorer")

# # Fetch Data from Flask API (replace with your actual API URL)
# API_URL = 'http://127.0.0.1:5000/yellow_trips'
# response = requests.get(API_URL)
# if response.status_code == 200:
#     taxi_data = pd.DataFrame(json.loads(response.text))

#     # Convert "NULL" to None in airport_fee column
#     taxi_data['airport_fee'] = taxi_data['airport_fee'].astype(str).str.replace('NULL', '', regex=False)

#     # Filtering (with type conversion and handling for equal min/max)
#     st.sidebar.header("Filter Data")
#     passenger_count_options = taxi_data['passenger_count'].unique()
#     passenger_count = st.sidebar.selectbox("Passenger Count", passenger_count_options)
#     vendor_id_options = taxi_data['VendorID'].unique()
#     vendor_id = st.sidebar.selectbox("Vendor ID", vendor_id_options)
    
#     # Calculate min_fare and max_fare
#     min_fare = float(taxi_data['fare_amount'].min())
#     max_fare = float(taxi_data['fare_amount'].max())

#     # Check if min_fare and max_fare are equal
#     if min_fare == max_fare:
#         max_fare += 0.1  # Slightly increase the max_fare 
    
#     # Determine valid slider values
#     min_fare_slider = min(0.0, min_fare) # Ensure min_fare_slider is not less than 0
#     max_fare_slider = max(0.0, max_fare) # Ensure max_fare_slider is not less than 0

#     min_fare = st.sidebar.number_input("Minimum Fare Amount", min_value=min_fare_slider, value=min_fare_slider)
#     max_fare = st.sidebar.number_input("Maximum Fare Amount", min_value=min_fare, value=max_fare_slider)  

#     # Apply filters to the DataFrame
#     filtered_data = taxi_data[
#         (taxi_data['passenger_count'] == passenger_count) &
#         (taxi_data['VendorID'] == vendor_id) &
#         (taxi_data['fare_amount'] >= min_fare) &
#         (taxi_data['fare_amount'] <= max_fare)
#     ]

#     # Display Options
#     st.header("Data Table")
#     st.dataframe(filtered_data)

#     # Chart Options
#     st.header("Visualizations")
#     chart_type = st.selectbox("Choose chart type", ["None", "Bar Chart", "Scatter Plot"])

#     if chart_type == "Bar Chart":
#         x_axis = st.selectbox("Select X-axis", filtered_data.columns)
#         st.bar_chart(filtered_data[x_axis].value_counts())

#     elif chart_type == "Scatter Plot":
#         x_axis = st.selectbox("Select X-axis", filtered_data.columns)
#         y_axis = st.selectbox("Select Y-axis", filtered_data.columns)
#         st.scatter_chart(filtered_data[[x_axis, y_axis]])

# else:
#     st.error("Error fetching data from the API")
