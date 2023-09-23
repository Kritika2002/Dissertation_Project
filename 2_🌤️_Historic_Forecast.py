import streamlit as st

from Dashboard_Home import convert_df 

params = st.experimental_get_query_params()
print('query params', params)

st.subheader('Forecast History :sun_small_cloud: ')

connection = st.experimental_connection("postgresql", type="sql")

from_date = st.date_input('STARTING date from which to load data:')

till_date = st.date_input('ENDING date till which to load data:')

cities = connection.query('SELECT name FROM cities;')

# print('cities', cities['name'].tolist())


selected_cities = st.multiselect('Choose cities for which to display data', cities['name'].tolist(), default=params.get('city'))


selected_cities = ', '.join(f"'{city}'" for city in selected_cities)

print(selected_cities)

if (from_date > till_date):
  st.error('Please enter an ending date later than the starting date')

weather_df = connection.query(f'''
        SELECT cities.name, for_day, expected_temperature_low, expected_temperature_high, rain_probability
        FROM forecast
        INNER JOIN cities ON cities.id = forecast.city_id
        WHERE for_day > '{from_date.isoformat()}' AND for_day < '{till_date.isoformat()}'
        { f"AND cities.name IN ({selected_cities})" if selected_cities else ''}
        ORDER BY cities.name, for_day DESC;
    ''')

print(weather_df)

if (len(weather_df.index) !=0):
  csv = convert_df(weather_df)

  st.download_button(
      label="Download data as CSV",
      data=csv,
      file_name='all_cities_historic_weather.csv',
      mime='text/csv',
  )

  st.dataframe(weather_df, hide_index=True)
  chart = {
    "encoding": {
            "x": {
                "timeUint": "day",
                "field": "for_day",
                "type": "temporal",
                "title": "Time",
            },
    },
    "layer":
    [
      {
        "mark": {"type": "point", "shape":"triangle-up", "filled":"false", "size":120},
        "encoding": {
            "y": {
                "field": "expected_temperature_high",
                "type": "quantitative",
                "title": "Temp (high)°C"
            },
            "color": {"field": "name", "type": "nominal"},
        },
      },
      {
        "mark": {"type": "point", "shape":"triangle-down", "filled":"false", "size":120},
        "encoding": {
            "y": {
                "field": "expected_temperature_low",
                "type": "quantitative",
                "title": "Temp (low)°C"
            },
            "color": {"field": "name", "type": "nominal", "title": "City name"},
        },
      },
    ]
  }

  st.subheader('Scatter plot of historic min (🔽) and max (🔼) temperature forecasts:')


  st.vega_lite_chart(
        weather_df, chart, theme="streamlit", use_container_width=False, width = 900, scale=1.5
    )
  
else:
  st.warning('No data to display, please select a different time range')