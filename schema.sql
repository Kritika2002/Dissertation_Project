-- Create table for cities
CREATE TABLE IF NOT EXISTS cities (
  id      INT2 PRIMARY KEY,
  name    varchar(255) NOT NULL
  );

-- Create table for forecast
CREATE TABLE IF NOT EXISTS forecast (
  id SERIAL PRIMARY KEY,
  for_day date NOT NULL,
  city_id INTEGER REFERENCES cities(id) NOT NULL,
  expected_temperature_low DECIMAL(3,0),
  expected_temperature_high DECIMAL(3,0),
  rain_probability DECIMAL(2, 0),
  weather_class INT2 -- 0 for today, 1 for tonight, 2 for tomorrow
  );

-- Create table for observed_weather
CREATE TABLE IF NOT EXISTS observed_weather (
	id SERIAL PRIMARY KEY,
	city_id INTEGER REFERENCES cities(id) NOT NULL,
	max_temperature DECIMAL(5, 2),
	min_temperature DECIMAL(5, 2),
	rain_probability DECIMAL(2, 0),
	ts TIMESTAMP NOT NULL
);

-- Create table for sun_info
CREATE TABLE IF NOT EXISTS sun_info (
	id SERIAL PRIMARY KEY,
	city_id INTEGER REFERENCES cities(id) NOT NULL,
	for_day date NOT NULL,
	sunrise time,
	sunset time
);

-- Insert city id and names for cities
INSERT INTO cities (id,name)
VALUES
(21,'dadeldhura'),
(22,'dipayal'),
(23,'dhangadi'),
(24,'birendranagar'),
(25,'nepalgunj'),
(26,'jumla'),
(27,'ghorahi'),
(28,'pokhara'),
(29,'bhairahawa'),
(30,'simara'),
(31,'kathmandu'),
(32,'okhaldhunga'),
(1,'taplejung'),
(33,'dhankuta'),
(34,'biratnagar'),
(38,'janakpur'),
(35,'jomsom'),
(36,'dharan'),
(37,'lumle'),
(39,'jiri');