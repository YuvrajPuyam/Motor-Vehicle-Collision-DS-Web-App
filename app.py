import numpy as np
import pandas as pd

import pydeck as pdk
import streamlit as st
import plotly.express as px

DATA_PATH = 'Motor_Vehicle_Collisions_-_Crashes.csv'

st.title("Motor Vehicle Collisions in NYC")
st.markdown("### Dashboard to show Motor Vehicle Collisions in NYC")


@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_PATH, nrows=nrows, parse_dates=[
                       ['CRASH_DATE', 'CRASH_TIME']])
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    def lowercase(x): return str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={'crash_date_crash_time': 'date/time'},
                inplace=True, errors="raise")
    return data


data = load_data(100000)  # loading the first 1,00,000 rows of data
original_data = data.copy()

MAX_INJURED_PEOPLE = data.max(axis=0, skipna=True)['injured_persons']

st.header('Where are the most number of people injured in NYC?')
injured_people = st.slider(
    'Number of people injured in Vehicle Collisions', np.int(0), np.int(MAX_INJURED_PEOPLE), step=np.int(1))
st.map(data.query('injured_persons >= @injured_people')
       [['latitude', 'longitude']].dropna(how='any'))


st.header('How many people are injured during a given time of the day?')
hour = st.slider('Hour to look at', 0, 23)
data = data[data['date/time'].dt.hour == hour]

midpoint = (np.average(data['latitude']), np.average(data['longitude']))
st.header(
    f'Vehicle Collisions between {hour % 24}:00 and {(hour + 1) % 24}:00')
st.write(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state={
        'latitude': midpoint[0],
        'longitude': midpoint[1],
        'zoom': 11,
        'pitch': 50
    },
    layers=[
        pdk.Layer(
            'HexagonLayer',
            data=data[['date/time', 'latitude', 'longitude']],
            get_position=['longitude', 'latitude'],
            radius=100,
            extruded=True,
            pickable=True,
            elevation_scale=4,
            elevation_range=[0, 1000],
        ),
    ],
))

st.subheader(
    f'Breakdown by minute between {hour % 24}:00 and {(hour + 1) % 24}:00')
filtered_data = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour+1))
]
hist = np.histogram(
    filtered_data['date/time'].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({'minutes': range(60), 'crashes': hist})
fig = px.bar(chart_data, x='minutes', y='crashes',
             hover_data=['minutes', 'crashes'], height=400)
st.write(fig)

st.header('Top 5 dangerous streets by affected type')
select = st.selectbox('Affected type of people', [
                      'Pedestrians', 'Cyclists', 'Motorists'])

if select == 'Pedestrians':
    st.write(original_data.query('injured_pedestrians >= 1')[['on_street_name', 'injured_pedestrians']].sort_values(
        by='injured_pedestrians', ascending=False).dropna(how='any')[:5])

elif select == 'Cyclists':
    st.write(original_data.query('injured_cyclists >= 1')[['on_street_name', 'injured_cyclists']].sort_values(
        by='injured_cyclists', ascending=False).dropna(how='any')[:5])

elif select == 'Motorists':
    st.write(original_data.query('injured_motorists >= 1')[['on_street_name', 'injured_motorists']].sort_values(
        by='injured_motorists', ascending=False).dropna(how='any')[:5])

if st.checkbox('Show Raw Data', False):
    st.subheader('Raw Data:')
    st.write(original_data)
