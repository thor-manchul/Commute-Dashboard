import requests
from datetime import datetime, timedelta
from typing import Dict, Any


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


    def get_coords(self, address: str) -> str | None:
        """
        Converts a physical address string into geographic coordinates (latitude and longitude).

        Args:
            address (str): The address or landmark to locate.

        Returns:
            str | None: A 'lat,lon' string if found, otherwise None.
        """
        url = f"{self.search_url}/{address}.json?key={self.api_key}&limit=1"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            response_json = response.json()
        except requests.exceptions.HTTPError as e:
            print(f"❌ API Error for address '{address}': {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed for address '{address}': {e}")
            return None
        if not response_json.get('results'):
            return None
        pos = response_json['results'][0]['position']
        return f"{pos['lat']},{pos['lon']}"


    def get_route_data(self, start_coords: str, end_coords: str, arrival_time: str, mode: str) -> Dict[str, Any] | None:
        """
        Retrieves routing data including travel time and traffic information.

        Args:
            start_coords (str): Starting coordinates in 'lat,lon' format.
            end_coords (str): Destination coordinates in 'lat,lon' format.
            arrival_time (str): Desired arrival time in ISO format (YYYY-MM-DDTHH:MM:SS).
            mode (str): Mode of transport (e.g., 'car', 'pedestrian', 'bicycle').

        Returns:
            Dict[str, Any]: The raw JSON response from the TomTom Routing API, or None on error.
        """
        params = {
            "key": self.api_key,
            "arriveAt": arrival_time,
            "traffic": "true",
            "travelMode": mode
        }
        url = f"{self.routing_url}/{start_coords}:{end_coords}/json"
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"❌ API Error for route: {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None


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




class TelegramClient:
    """
    Service class that handles sending messages via the Telegram Bot API.
    """

    def __init__(self, bot_token: str):
        """
        Initializes the Telegram client.
        Args:
            bot_token (str): The HTTP API token provided by BotFather.
        """
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send_message(self, chat_id: str, text: str) -> bool:
        """
        Sends a text message to a specific Telegram Chat ID.

        Args:
            chat_id (str): The destination user's Chat ID.
            text (str): The message payload.

        Returns:
            bool: True if successful, False otherwise.
        """
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text
        }
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except requests.exceptions.HTTPError as e:
            print(f"\n❌ Telegram API Error: {e}")
            return False
        except requests.exceptions.RequestException as e:
            print(f"\n❌ Telegram Network Error: {e}")
            return False


    def validate_chat_id(self, chat_id: str) -> bool:
        """
            Validates that a chat ID is reachable by the bot before scheduling an alert.

            Args:
                chat_id (str): The Chat ID to validate.

            Returns:
                bool: True if the chat ID is reachable, False otherwise.
        """
        url = f"{self.base_url}/getChat"
        try:
            response = requests.get(url, params={"chat_id": chat_id}, timeout=10)
            response.raise_for_status()
            return response.json().get("ok", False)
        except requests.exceptions.RequestException:
            return False