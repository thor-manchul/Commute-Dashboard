import os
from dotenv import load_dotenv
from models import TomTomClient, Commute, TelegramClient
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger

class CommuteApp:
    """
    The main controller class for the Commute Dashboard.

    This class handles the application lifecycle, including environment
    configuration, user interaction, and coordination with the TomTom API.
    """

    VALID_MODES = ["car", "bicycle", "pedestrian"]
    DEFAULT_MODE = "car"
    TELEGRAM_LINK = "t.me/CommuteAlertBot"

    def __init__(self):
        """
        Initializes the application and loads environment variables.
        """
        load_dotenv()
        self.api_key = os.environ.get("TOMTOM_API_KEY")
        self.telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        self.client = None
        self.telegram_client = None

        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

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
        if self.telegram_token:
            self.telegram_client = TelegramClient(self.telegram_token)
        else:
            print("⚠️ Warning: TELEGRAM_BOT_TOKEN not found. Notifications disabled.")

        return True


    def _get_user_input(self) -> tuple[str, str, str, str] | None:
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

    def _get_chat_id(self) -> str:
        """
        Separately prompts the user for their Telegram Chat ID for notifications.
        Validates the chat ID against the Telegram API before accepting it.

        Returns:
            str: A validated chat ID, or an empty string if the user skips.
        """
        if not self.telegram_client:
            return ""

        print(f"\n📱 Want a 5-minute warning? Message {self.TELEGRAM_LINK} with 'START' to get your ID.")

        while True:
            chat_id = input("💬 Enter Chat ID (or press Enter to skip): ").strip()

            if not chat_id:
                return ""

            print("🔍 Validating Chat ID...")
            if self.telegram_client.validate_chat_id(chat_id):
                print("✅ Chat ID confirmed!")
                return chat_id
            else:
                print("❌ Could not reach that Chat ID. Check it and try again, or press Enter to skip.")

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
                chat_id = self._get_chat_id()

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

                if chat_id and self.telegram_client:
                    notify_time = commute.leave_dt - timedelta(minutes=5)
                    if notify_time > datetime.now():
                        # Standard flow: Plenty of time, schedule the 5-minute warning
                        msg = f"🚗 SMART COMMUTE ALERT 🚗\nYou need to leave for {end} in 5 minutes to arrive on time!"
                        self.scheduler.add_job(
                            self.telegram_client.send_message,
                            trigger=DateTrigger(run_date=notify_time),
                            args=[chat_id, msg]
                        )
                        print(f"✅ Telegram alert scheduled for {notify_time.strftime('%I:%M %p')}!")

                    elif commute.leave_dt > datetime.now():
                        # Edge case: They need to leave in LESS than 5 minutes
                        minutes_left = int((commute.leave_dt - datetime.now()).total_seconds() / 60)
                        print(f"🚨 URGENT: You only have {minutes_left} minutes to leave! Go now!")
                        # Send an immediate text instead of scheduling one
                        self.telegram_client.send_message(chat_id, f"🚨 URGENT: Leave in {minutes_left} minutes!")

                    else:
                        # Edge case: They are already late
                        print("❌ You are already late for this departure time.")


                # 6. Exit or Continue
                again = input("\n🔄 Calculate another route? (y/n): ").strip().lower()
                if again != 'y':
                    print("\n👋 Thank you for using Smart Commute Dashboard!")
                    self.scheduler.shutdown(wait=False)
                    break

            except KeyboardInterrupt:
                print("\n\n👋 Program terminated by user. Goodbye!")
                self.scheduler.shutdown(wait=False)
                break
            except Exception as e:
                print(f"\n❌ An unexpected error occurred. Please try again.")



if __name__ == "__main__":
    app = CommuteApp()
    app.run()
