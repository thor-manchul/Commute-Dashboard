import requests
from datetime import datetime, timedelta

class TomTomClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.search_url = "https://api.tomtom.com/search/2/search"
        self.routing_url = "https://api.tomtom.com/routing/1/calculateRoute"

    def get_coords(self, address):
        url = f"{self.search_url}/{address}.json?key={self.api_key}&limit=1"
        response = requests.get(url).json()
        if not response.get('results'):
            return None
        pos = response['results'][0]['position']
        return f"{pos['lat']},{pos['lon']}"

    def get_route_data(self, start_coords, end_coords, arrival_time, mode):
        params = {
            "key": self.api_key,
            "arriveAt": arrival_time,
            "traffic": "true",
            "travelMode": mode
        }
        url = f"{self.routing_url}/{start_coords}:{end_coords}/json"
        return requests.get(url, params=params).json()




class Commute:
    def __init__(self, travel_seconds, arrival_iso):
        self.minutes = travel_seconds // 60
        self.arrival_dt = datetime.fromisoformat(arrival_iso)
        self.leave_dt = self.arrival_dt - timedelta(seconds=travel_seconds)

    def display(self):
        return f"⏰ {self.minutes} mins | 🚀 Leave by: {self.leave_dt.strftime('%I:%M %p')}"