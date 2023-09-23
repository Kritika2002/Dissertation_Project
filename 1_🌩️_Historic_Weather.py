import streamlit as st

from Dashboard_Home import convert_df 

params = st.experimental_get_query_params()
print('query params', params)

st.subheader('Weather History :lightning:')

connection = st.experimental_connection("postgresql", type="sql")


from_date = st.date_input('STARTING date from which to load data:')

till_date = st.date_input('ENDING date till which to load data:')

cities = connection.query('SELECT name FROM cities;')

# print('cities', cities['name'].tolist())


selected_cities = st.multiselect('Choose cities for which to display data', cities['name'].tolist(), default=params.get('city'))

selected_cities = ', '.join(f"'{city}'" for city in selected_cities)

if (from_date > till_date):
  st.error('Please enter an ending date later than the starting date')

print(selected_cities)

weather_df = connection.query(f'''
        SELECT cities.name, ts, max_temperature, min_temperature, rain_probability
        FROM observed_weather
        INNER JOIN cities ON cities.id = observed_weather.city_id
        WHERE ts > '{from_date.isoformat()}' AND ts < '{till_date.isoformat()}'
        { f"AND cities.name IN ({selected_cities})" if selected_cities else ''}
        ORDER BY cities.name, ts DESC;
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
  # st.line_chart(weather_df, x='ts', y = ['max_temperature', 'min_temperature'], color='name')

  chart = {
    "encoding": {
            "x": {
                "timeUint": "day",
                "field": "ts",
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
                "field": "max_temperature",
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
                "field": "min_temperature",
                "type": "quantitative",
                "title": "Temp (low)°C"
            },
            "color": {"field": "name", "type": "nominal", "title": "City name"},
        },
      },
    ]
  }

  st.subheader('Scatter plot of historic min (🔽) and max (🔼) temperature observations:')

  st.vega_lite_chart(
        weather_df, chart, theme="streamlit", use_container_width=False, width = 900, scale=1.5
    )

else:
  st.warning('No data to display, please select a different time range')