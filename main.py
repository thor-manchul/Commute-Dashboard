import os
from dotenv import load_dotenv
from models import TomTomClient, Commute

class CommuteApp:
    """
    The main controller class for the Commute Dashboard.

    This class handles the application lifecycle, including environment
    configuration, user interaction, and coordination with the TomTom API.
    """
    def __init__(self):
        """
        Initializes the application and loads environment variables.
        """
        load_dotenv()
        self.api_key = os.environ.get("API_KEY")
        self.client = None

    def initialize_client(self) -> bool:
        """
        Validates the API credentials and sets up the TomTom client.

        Returns:
            bool: True if the client was initialized successfully, False otherwise.
        """

        if not self.api_key:
            print("Error: API key not provided in .env file")
            return False
        self.client = TomTomClient(self.api_key)
        return True





