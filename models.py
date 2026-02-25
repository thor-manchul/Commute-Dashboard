import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class TomTomClient:
    """
    Service class that handles all geocoding and routing requests to the TomTom API

    Attributes:
        api_key (str): The developer API key used for authentication.
    """
    def __init__(self, api_key: str):
        """
        Initializes the TomTomClient with a secure API key.

        Args:
            api_key (str): The TomTom API key retrieved from environment variables.
        """
        self.api_key = api_key
        self.search_url = "https://api.tomtom.com/search/2/search"
        self.routing_url = "https://api.tomtom.com/routing/1/calculateRoute"


    def get_coords(self, address: str) -> Optional[str]:
        """
        Converts a physical address string into geographic coordinates (latitude and longitude).

        Args:
            address (str): The address or landmark to locate.

        Returns:
            Optional[str]: A 'lat,lon' string if found, otherwise None.
        """
        url = f"{self.search_url}/{address}.json?key={self.api_key}&limit=1"
        response = requests.get(url).json()
        if not response.get('results'):
            return None
        pos = response['results'][0]['position']
        return f"{pos['lat']},{pos['lon']}"



    def get_route_data(self, start_coords: str, end_coords: str, arrival_time: str, mode: str) -> Dict[str, Any]:
        """
        Retrieves routing data including travel time and traffic information.

        Args:
            start_coords (str): Starting coordinates in 'lat,lon' format.
            end_coords (str): Destination coordinates in 'lat,lon' format.
            arrival_time (str): Desired arrival time in ISO format (YYYY-MM-DDTHH:MM:SS).
            mode (str): Mode of transport (e.g., 'car', 'pedestrian', 'bicycle').

        Returns:
            Dict[str, Any]: The raw JSON response from the TomTom Routing API.
        """
        params = {
            "key": self.api_key,
            "arriveAt": arrival_time,
            "traffic": "true",
            "travelMode": mode
        }
        url = f"{self.routing_url}/{start_coords}:{end_coords}/json"
        return requests.get(url, params=params).json()



class Commute:
    """
    A data model representing a calculated commute trip.

    Attributes:
        minutes (int): Total travel duration in minutes.
        arrival_dt (datetime): The target arrival time object.
        leave_dt (datetime): The calculated required departure time object.
    """
    def __init__(self, travel_seconds: int, arrival_iso:str):
        """
        Processes raw travel data into a human-readable commute plan.

        Args:
            travel_seconds (int): Raw travel time duration in seconds.
            arrival_iso (str): The desired arrival time in ISO format.
        """
        self.minutes = travel_seconds // 60
        self.arrival_dt = datetime.fromisoformat(arrival_iso)
        # Calculate departure by subtracting travel time from arrival time
        self.leave_dt = self.arrival_dt - timedelta(seconds=travel_seconds)

    def display(self) -> str:
        """
        Returns a formatted summary of the commute results.

        Returns:
            str: A string containing the travel duration and recommended departure time.
        """
        return f"⏰ {self.minutes} mins | 🚀 Leave by: {self.leave_dt.strftime('%I:%M %p')}"