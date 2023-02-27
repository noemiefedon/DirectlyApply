from abc import ABC, abstractmethod
import re

import numpy as np
import requests


class LocatorError(Exception):
    pass


class GeoPointConverterError(LocatorError):
    pass


def geo_point_to_latitude_and_longitude(point: str) -> (float, float):
    """
    Returns the latitude and the longitude of a point

    Argument:
    point (str): the geography point following the format 'POINT(-122.04619996 47.62540000)'

    Outputs:
    tuple with two elements:
    - latitude (float): the latitude of the point
    - longitude (float): the longitude of the point
    """
    pattern = r"(?<![a-zA-Z:])[-+]?\d*\.?\d+"
    all_numbers = re.findall(pattern, point)
    all_floats = [float(elem) for elem in all_numbers]
    assert len(all_floats) == 2
    longitude, latitude = all_floats
    assert -180 <= latitude <= 180
    assert -180 <= longitude <= 180
    return latitude, longitude


class LocatorStrategyError(LocatorError):
    pass


# Strategy interface for the locator
class LocatorStrategy(ABC):
    @abstractmethod
    def execute(self, latitude: float, longitude: float) -> str:
        """
        returns the name of the US state corresponding to a latitude and longitude

        Arguments:
        latitude (float): the latitude of a geographical point
        longitude (float): the longitude of a geographical point

        Outputs:
        the US state where the geographical point is situated (str)
        """
        pass


class HerokuAppLocatorStrategy(LocatorStrategy):
    def execute(self, latitude: float, longitude: float) -> str:
        """
        returns the name of the US state corresponding to a latitude and longitude based on the API:
        https://us-state-api.herokuapp.com

        Arguments:
        latitude (float): the latitude of a geographical point
        longitude (float): the longitude of a geographical point

        Outputs:
        the US or Canadian state where the geographical point is situated (str)

        Possible improvement for the "locator":
        If location not found in US, we could look at neighbour points with increasing distance from geographical point
        and use the state of the first US/Canadian state found. But this approach is not good if we have erroneous
        points! A solution to that last problem could be to define an upper bound for the neighbourhood check and
        classify the points not identified in the US as belonging to the "Other" state.

        Other remark:
        Returning an error for the location not found in the US is not great as running the locator is not fast and
        the script is interrupted.
        """
        # deal with locations not in the US
        if np.isclose(latitude, 42.31954001) and np.isclose(longitude, -83.02434):
            return "Ontario"
        if np.isclose(latitude, 38.72090002) and np.isclose(longitude, -75.076):
            return "Delaware"
        try:
            url = f"https://us-state-api.herokuapp.com/?lat={latitude}&lon={longitude}"
            response = requests.get(url).json()
            return response["state"]["name"]
        except Exception as e:
            raise LocatorStrategyError(e)
