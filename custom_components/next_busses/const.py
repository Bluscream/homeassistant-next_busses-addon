"""Constants for the next_busses integration."""

DOMAIN = "next_busses"

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_NAME, CONF_SCAN_INTERVAL
from datetime import timedelta

DEFAULT_NAME = "Next Bus"
ICON = "mdi:bus"
TIME_STR_FORMAT = "%H:%M"
ELEMENT_NAME = "transportation-data-card"
ELEMENT_PATH = "custom_elements/next_busses.html"

# Validation of the user's configuration
SEMS_CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required("url"): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(
            CONF_SCAN_INTERVAL, description={"suggested_value": 60}
        ): int  # , default=DEFAULT_SCAN_INTERVAL
    }
)