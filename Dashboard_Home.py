#dashboard page for the system

#import libraries
import streamlit as st
import pandas as pd
import folium
from datetime import datetime

from streamlit_folium import st_folium

st.set_page_config(
    page_title="Dashboard Home",
    page_icon="🌦️",
)

st.header(':partly_sunny_rain: Welcome to the Dashboard :partly_sunny_rain:')

st.success('''            
  **👈 Select pages from the sidebar**
''')

st.subheader('City map points for weather data:')
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')


def gen_current_city_data_html(conn, city_name=None):
  print('city_name', city_name)
  weather_df = conn.query(f'''
    SELECT DISTINCT ON (cities.name) cities.name, ts, max_temperature, min_temperature, rain_probability
    FROM observed_weather
    INNER JOIN cities ON cities.id = observed_weather.city_id
    { f"WHERE cities.name = '{city_name}'" if city_name else ''}
    ORDER BY cities.name, ts DESC;
  ''')

  print('weather_df:', weather_df)

  if (len(weather_df.index) == 0):
    return 'No data found!'
  elif (len(weather_df.index) > 1):
    return weather_df
  else:
    row = weather_df.head(1).to_dict('records')[0]
    print('weather_row:', row)
    return f'''
      <h2> {row['name'].capitalize()} </h2>
      <h5>
      Max_temp: {row['max_temperature']} °C
      Min_temp: {row['min_temperature']} °C
      Rainfall_amount: {row['rain_probability']} mm
      </h5>
      See historic data:<br>
      <a href="/Historic_Weather?city={city_name}" target="_empty">Weather</a><br>
      <a href="/Historic_Forecast?city={city_name}" target="_empty">Forecast</a><br>
      <a href="/Sunrise_Sunset?city={city_name}" target="_empty">Sunrise & Sunset</a>

    '''
  
connection = st.experimental_connection("postgresql", type="sql")
st.sidebar.success("Select a page above.")

data_update = connection.query("SELECT ts FROM observed_weather ORDER BY ts DESC LIMIT 1;")

st.info('Data last updated at: ' + datetime.strftime(data_update.iloc[0]['ts'], '%Y-%m-%d %H-%M-%S'))


df = connection.query("SELECT * FROM cities;", ttl='5m')

# for row in df.itertuples():
#   st.write(f"{row.name}")

# st.map(df)

m = folium.Map(location=[28.266889, 84.568511], zoom_start=6.8)

for row in df.itertuples():
  print(row)
  folium.Marker([row.latitude, row.longitude], tooltip=row.name.capitalize(), popup=folium.Popup(gen_current_city_data_html(connection, row.name)), lazy=True).add_to(m)



st_data = st_folium(m, width=750)

all_cities_df = gen_current_city_data_html(connection)
print('all cities:: ', all_cities_df)

st.subheader("Current weather data observation:")


csv = convert_df(all_cities_df)
st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name='all_cities_current_weather.csv',
    mime='text/csv',
)

st.dataframe(all_cities_df, hide_index=True)
