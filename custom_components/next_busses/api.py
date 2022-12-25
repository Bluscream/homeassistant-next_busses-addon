import json
import logging
import requests
from homeassistant import exceptions
_LOGGER = logging.getLogger(__name__)
_RequestTimeout = 30  # seconds
# _DefaultHeaders = {
#     "Content-Type": "application/json",
#     "Accept": "application/json"
# }
class VRNAPI:
    """Interface to the API."""
    def __init__(self, hass, url = "http://minopia.de/api/mvg/"):
        """Init dummy hub."""
        self._hass = hass
        self.base_url = url
    def getData(self, stop, platforms, max_results, meta=False):
        """Retrieve real-time public transportation information for the specified stop and platforms.
        Parameters:
            - stop (str): The stop ID for which to retrieve information.
            - platforms (str): A comma-separated list of platforms for which to retrieve information.
            - max_results (int): The maximum number of results to retrieve.
            - meta (bool): Whether to include metadata in the response.
        Returns:
            A list of dictionaries containing the real-time public transportation information for each result.
        """
        try:
            _LOGGER.debug("Next Busses - Making API request")
            params = {
                "stop": stop,
                "platforms": platforms,
                "max": max_results,
                "meta": meta,
            }
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            response = requests.get(self.base_url, params=params, headers=headers, timeout=_RequestTimeout)
            if response.status_code == 200:
                data = response.json()
                results = []
                for i in range(1, max_results + 1):
                    result = data[str(i)]
                    result_dict = {
                        "time": result["time"],
                        "minutes": result["minutes"],
                        "line": result["line"],
                        "from": result["from"],
                        "to": result["to"],
                        "platform": result["platform"],
                    }
                    results.append(result_dict)
                return results
            else: raise Exception(f"Failed to retrieve real-time information: {response.status_code}")
        except Exception as exception:
            _LOGGER.error("Unable to fetch data from API. %s", exception)
class OutOfRetries(exceptions.HomeAssistantError):
    """Error to indicate too many error attempts."""
