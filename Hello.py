"""
Class: CS230--Section 001
Name: Colton Destrampe
Description: Final Project
I pledge that I have completed the programming assignment
independently.
I have not copied the code from a student or any source.
I have not given my code to any student.
"""
import streamlit as st
import pandas as pd
import pydeck as pdk

# Load the dataset with caching
@st.cache_data
def load_data():
    data = pd.read_csv('bostoncrime2023.csv')
    return data

data = load_data()

# Define functions to handle data manipulation
def get_most_common_crimes_by_district(df, district):
    # Filter the data by the district
    filtered_data = df[df['DISTRICT'] == district]
    # Count the frequency of each offense description
    crime_counts = filtered_data['OFFENSE_DESCRIPTION'].value_counts().head(10)
    return crime_counts

def crime_frequency_by_time(df, time_range, selected_crime_types):
    # Adjust the filter to handle the case when the end time is 24
    if time_range[1] == 24:
        time_range = (time_range[0], 0)
        next_day = True
    else:
        next_day = False

    # Filter by hour range
    if next_day:
        # Include crimes from the start time to the end of the day and from the start of the next day
        time_filtered_df = df[(df['HOUR'] >= time_range[0]) | (df['HOUR'] == time_range[1])]
    else:
        time_filtered_df = df[df['HOUR'].between(time_range[0], time_range[1] - 1)]

    # If specific crime types are selected, further filter the data
    if selected_crime_types:
        time_filtered_df = time_filtered_df[time_filtered_df['OFFENSE_DESCRIPTION'].isin(selected_crime_types)]

    # Count the frequency of crimes
    crime_counts = time_filtered_df['OFFENSE_DESCRIPTION'].value_counts()
    return crime_counts

def crime_trends_over_months(df):
    df['MONTH'] = pd.to_datetime(df['OCCURRED_ON_DATE']).dt.month
    return df.groupby('MONTH')['INCIDENT_NUMBER'].count()

# Set up Streamlit interface elements
st.title("Exploring Boston’s Crime: An Interactive Journey Through Data")

# Sidebar elements
st.sidebar.header("Customize Visualizations")  # Main header for the sidebar

# District selection
st.sidebar.subheader("Visual 1: Choose District for Crime Data")  # Subheader for district filter
district_options = data['DISTRICT'].dropna().unique()
district_options.sort()
default_district_index = 0  # Set the first district as the default
district = st.sidebar.selectbox('', options=district_options, index=default_district_index)

# Crime type selection
st.sidebar.subheader("Visual 2: Filter by Crime Type")  # Subheader for crime type filter
crime_type_options = data['OFFENSE_DESCRIPTION'].dropna().unique()
crime_type_options.sort()
crime_type = st.sidebar.multiselect('', options=crime_type_options)

# Time frame selection
st.sidebar.subheader("Visual 2: Set Time Range for Crime Data")  # Subheader for time frame filter
time_frame = st.sidebar.slider('', 0, 24, (0, 24))

# Main page content
st.header("Crime Data Overview")

# Display most common crimes in selected district
st.subheader(f"Visual 1: Most common crimes in District {district}")
common_crimes_data = get_most_common_crimes_by_district(data, district)
st.bar_chart(common_crimes_data)

# Display crime frequency by time of day with crime type filtering
if time_frame and crime_type:
    st.subheader(f"Visual 2: Crime frequency from {time_frame[0]}:00 to {time_frame[1]}:00 for selected crime types")
    crime_time_data = crime_frequency_by_time(data, time_frame, crime_type)
    st.bar_chart(crime_time_data)
else:
    st.subheader(f"Visual 2: Crime frequency from {time_frame[0]}:00 to {time_frame[1]}:00")
    crime_time_data = crime_frequency_by_time(data, time_frame, [])
    st.bar_chart(crime_time_data)

# Display crime trends over the months
st.subheader("Visual 3: Crime trends over the months in 2023")
crime_trends_data = crime_trends_over_months(data)
st.line_chart(crime_trends_data)

# Map of Crime Locations with Heatmap
st.subheader("Visual 4: Heatmap of Crime Locations")
map_data = data[['Lat', 'Long']].dropna(how="any")

# Define a heatmap layer
heatmap_layer = pdk.Layer(
    "HeatmapLayer",
    data=map_data,
    opacity=0.9,
    get_position='[Long, Lat]',
    threshold=0.5,
    radius_pixels=60,
)

# Render the heatmap on the map
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=map_data['Lat'].mean(),
        longitude=map_data['Long'].mean(),
        zoom=11,
        pitch=50,
    ),
    layers=[heatmap_layer],
))

# Thank you for an incredible semester Prof. Masloff!
