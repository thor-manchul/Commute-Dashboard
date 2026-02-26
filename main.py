import os
from dotenv import load_dotenv
from models import TomTomClient, Commute
from datetime import datetime

class CommuteApp:
    """
    The main controller class for the Commute Dashboard.

    This class handles the application lifecycle, including environment
    configuration, user interaction, and coordination with the TomTom API.
    """

    VALID_MODES = ["car", "bicycle", "pedestrian"]
    DEFAULT_MODE = "car"

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


    def _get_user_input(self) -> tuple[str, str, str, str]:
        """
        Prompts user for details and validates both time format and travel mode.

        Returns:
            tuple: A validated tuple of (start, end, arrival, mode).
        """

        print("\n" + "=" * 30)
        print("SMART COMMUTE DASHBOARD")
        print("=" * 30)

        while True:
            start = input("📍 Start Address: ").strip()
            end = input("🏁 Destination: ").strip()
            arrival = input("⏰ Arrival Time (YYYY-MM-DDTHH:MM:SS): ").strip()
            mode = input(
                f"🚲 Mode ({'/'.join(self.VALID_MODES)}) [{self.DEFAULT_MODE}]: ").strip().lower() or self.DEFAULT_MODE

            # Validate non-empty fields
            if not all([start, end, arrival]):
                print("\n❌ Error: All fields are required.")
                continue

            # Validate minimum address length
            if len(start) < 3 or len(end) < 3:
                print("\n❌ Error: Addresses must be at least 3 characters.")
                continue

            # Validate and parse arrival time
            try:
                arrival_dt = datetime.fromisoformat(arrival)
                if arrival_dt <= datetime.now():
                    print("\n❌ Error: Arrival time must be in the future.")
                    continue
            except ValueError:
                print("\n❌ Error: Invalid time format.")
                print("   Example: 2026-12-25T09:30:00")
                continue

            # Validate travel mode
            if mode not in self.VALID_MODES:
                print(f"\n❌ Error: '{mode}' is invalid. Choose: {', '.join(self.VALID_MODES)}")
                continue

            print("\n✅ Input validated successfully!")
            return start, end, arrival, mode



