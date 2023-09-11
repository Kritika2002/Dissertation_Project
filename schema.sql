CREATE TABLE cities (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL
);

CREATE TABLE historical_weather (
  id SERIAL PRIMARY KEY,
  city_id INTEGER REFERENCES cities(id),
  date DATE NOT NULL,
  max_temperature DECIMAL(5, 2),
  min_temperature DECIMAL(5, 2),
  expected_rainfall DECIMAL(5, 2)
);

CREATE TABLE current_weather (
  id SERIAL PRIMARY KEY,
  city_id INTEGER REFERENCES cities(id),
  temperature DECIMAL(5, 2),
  expected_rainfall DECIMAL(5, 2)
);

CREATE TABLE tonight_forecast (
  id SERIAL PRIMARY KEY,
  date DATE NOT NULL,
  city_id INTEGER REFERENCES cities(id),
  expected_temperature DECIMAL(5, 2),
  expected_rainfall DECIMAL(5, 2)
);

CREATE TABLE tomorrow_forecast (
  id SERIAL PRIMARY KEY,
  date DATE NOT NULL,
  city_id INTEGER REFERENCES cities(id),
  expected_temperature DECIMAL(5, 2),
  expected_rainfall DECIMAL(5, 2)
);
