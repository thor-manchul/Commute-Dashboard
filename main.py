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
        self.api_key = os.environ.get("TOMTOM_API_KEY")
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
        print(" 🚗 SMART COMMUTE DASHBOARD")
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

    def run(self) -> None:
        """
        Main application loop that coordinates the end-to-end commute calculation.

        Handles initialization, user input gathering, geocoding, and routing
        while managing errors and user exit requests.
        """
        if not self.initialize_client():
            return

        print("\n🌟 Welcome to Smart Commute Dashboard!")

        while True:
            try:
                # 1. Gather validated input
                start, end, arrival, mode = self._get_user_input()

                # 2. Convert addresses to coordinates
                print("\n🔍 Looking up addresses...")
                start_coords = self.client.get_coords(start)
                end_coords = self.client.get_coords(end)

                if not start_coords or not end_coords:
                    print("❌ Could not find one or both addresses. Please be more specific.")
                    continue

                # 3. Calculate the route
                print("🚗 Calculating route...")
                route_data = self.client.get_route_data(start_coords, end_coords, arrival, mode)

                # 4. Handle API logic errors
                if not route_data or 'routes' not in route_data:
                    print("❌ Could not calculate route. Check your parameters or arrival time.")
                    continue

                # 5. Process and display results
                travel_seconds = route_data['routes'][0]['summary']['travelTimeInSeconds']
                commute = Commute(travel_seconds, arrival)

                print("\n" + "=" * 30)
                print("📊 COMMUTE RESULTS")
                print("=" * 30)
                print(commute.display())
                print("=" * 30)

                # 6. Exit or Continue
                again = input("\n🔄 Calculate another route? (y/n): ").strip().lower()
                if again != 'y':
                    print("\n👋 Thank you for using Smart Commute Dashboard!")
                    break

            except KeyboardInterrupt:
                print("\n\n👋 Program terminated by user. Goodbye!")
                break
            except Exception as e:
                # In a cybersecurity context, you might use generic error messages
                # to avoid information disclosure.
                print(f"\n❌ An unexpected error occurred. Please try again.")



if __name__ == "__main__":
    app = CommuteApp()
    app.run()
