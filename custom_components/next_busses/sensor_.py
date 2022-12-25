from __future__ import annotations

from contextlib import suppress
from datetime import datetime, timedelta
from http import HTTPStatus

import requests
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import CONF_NAME, UnitOfTime
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
import homeassistant.util.dt as dt_util

DEFAULT_NAME = "Next Bus"
ICON = "mdi:bus"

SCAN_INTERVAL = timedelta(minutes=1)
TIME_STR_FORMAT = "%H:%M"


OPTIONS_SCHEMA = vol.Schema({
    vol.Required(): str,
})
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required("url"): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string
    }
)

ELEMENT_NAME = "transportation-data-card"
ELEMENT_PATH = "custom_elements/next_busses.html"

sensors = []

def setup_platform(hass: HomeAssistant, config: ConfigType, add_entities: AddEntitiesCallback, discovery_info: DiscoveryInfoType | None = None,) -> None:
    """Set up the Dublin public transport sensor."""
    fetch_data(hass, config, add_entities)

def fetch_data(hass: HomeAssistant, config: ConfigType, add_entities: AddEntitiesCallback):
    response = requests.get(config["url"])
    data = response.json()
    for i, item in enumerate(data):
        time = item["time"] # datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
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
        sensors.append(VRNPublicTransportSensor(sensor_id, ))
    add_entities(sensors)

class VRNPublicTransportSensor(SensorEntity):
    """Implementation of an VRN public transport sensor."""

    _attr_attribution = "Data provided by Verkehrsverbund Rhein Nahe und Öffi"

    def __init__(self, id, platform, line, from_, to, time, timespan, minutes, name):
        """Initialize the sensor."""
        self._name = name
        self._unique_id = id
        self._times = self._state = None
        
        self.attributes = {
            platform = platform
            line = line
            from_ = from_
            to = to
            time = time
            timespan = timespan
            minutes = minutes
        }
        

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        if self._times is not None:
            next_up = "None"
            if len(self._times) > 1:
                next_up = f"{self._times[1][ATTR_ROUTE]} in "
                next_up += self._times[1][ATTR_DUE_IN]

            return {
                ATTR_DUE_IN: self._times[0][ATTR_DUE_IN],
                ATTR_DUE_AT: self._times[0][ATTR_DUE_AT],
                ATTR_STOP_ID: self._stop,
                ATTR_ROUTE: self._times[0][ATTR_ROUTE],
                ATTR_NEXT_UP: next_up,
            }

    @property
    def native_unit_of_measurement(self):
        """Return the unit this state is expressed in."""
        return UnitOfTime.MINUTES

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return ICON

    def update(self) -> None:
        """Get the latest data from opendata.ch and update the states."""
        self.data.update()
        self._times = self.data.info
        with suppress(TypeError):
            self._state = self._times[0][ATTR_DUE_IN]