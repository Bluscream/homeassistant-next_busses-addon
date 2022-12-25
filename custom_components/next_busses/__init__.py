"""The next_busses component."""

import requests
import voluptuous as vol
import homeassistant.components.frontend.html as html

# Define the schema for the options that the addon supports
OPTIONS_SCHEMA = vol.Schema({
    vol.Required("url"): str,
})

ELEMENT_NAME = "transportation-data-card"
ELEMENT_PATH = "custom_elements/next_busses.html"

async def fetch_data(hass):
    # Get the value of the "url" option
    url = vol.get("url")

    # Fetch data from the URL
    response = requests.get(url)
    data = response.json()

    # Keep track of the sensors that have been created
    sensors = []

    # Iterate through the data and create a sensor for each item
    for i, item in enumerate(data):
        time = item["time"]
        minutes = item["minutes"]
        timespan = item["timespan"]
        line = item["line"]
        from_ = item["from"]
        to = item["to"]
        platform = item["platform"]

        # Create a unique ID for the sensor based on the route information
        sensor_id = f"next_bus_{i + 1}"

        # Set the state of the sensor to the route information
        hass.states.async_set(sensor_id, f"{time} ({minutes} minutes)")

        # Add the sensor to the list of sensors
        sensors.append(sensor_id)

async def setup(hass, config):
    # Validate the config options using the schema
    config = OPTIONS_SCHEMA(config)

    # Run the fetch_data function every hour
    hass.helpers.event.async_track_time_interval(fetch_data, hass, minute=1)

async def stop(hass, config):
    # Delete the sensors that were created when the addon was started
    for sensor in sensors:
        hass.states.async_remove(sensor)
