import os
from dotenv import load_dotenv
from models import TomTomClient, Commute

class CommuteApp:
    def __init__(self):
        """Set up and configuration """
        load_dotenv()
        self.api_key = os.environ.get("API_KEY")
        self.client = None

