import pytest
from datetime import datetime
from models import Commute, TomTomClient
from requests.exceptions import HTTPError


@pytest.mark.parametrize("mode, expected_params", [
    ("car", "car"),
    ("bicycle", "bicycle"),
    ("pedestrian", "pedestrian")
])
def test_get_route_data_modes(mocker, mode, expected_params):
    """Test that different travel modes are correctly passed to the API."""
    mock_get = mocker.patch('models.requests.get')
    mock_get.return_value.raise_for_status.return_value = None
    mock_get.return_value.json.return_value = {"routes": []}

    client = TomTomClient("fake_key")
    # Call the method with the parameterized mode
    client.get_route_data("51,-114", "51,-115", "2026-12-25T09:00:00", mode)

    # Check that requests.get was called with the correct travelMode
    called_args, called_kwargs = mock_get.call_args
    assert called_kwargs['params']['travelMode'] == expected_params

def test_commute_calculation():
    """Test that the commute math correctly subtracts travel time."""
    arrival_time = "2026-12-25T09:30:00"
    travel_seconds = 1800  # 30 minutes

    commute = Commute(travel_seconds, arrival_time)

    assert commute.minutes == 30
    assert commute.leave_dt.strftime('%H:%M:%S') == "09:00:00"


def test_get_coords_no_results(mocker):
    """Test that empty API results return None."""
    mock_get = mocker.patch('models.requests.get')
    mock_get.return_value.raise_for_status.return_value = None
    mock_get.return_value.json.return_value = {"results": []}

    client = TomTomClient("fake_api_key")
    assert client.get_coords("Nowhere") is None


def test_get_coords_success(mocker):
    """Test successful coordinate retrieval by faking the API response."""
    # 1. Set up the mock API response
    mock_response = {
        "results": [{"position": {"lat": 51.0447, "lon": -114.0719}}]
    }

    # 2. Intercept the 'requests.get' call in models.py
    mock_get = mocker.patch('models.requests.get')
    mock_get.return_value.json.return_value = mock_response
    mock_get.return_value.raise_for_status.return_value = None

    # 3. Run the function
    client = TomTomClient("fake_api_key")
    coords = client.get_coords("Calgary Tower")

    # 4. Assert the outcome
    assert coords == "51.0447,-114.0719"
    mock_get.assert_called_once()  # Ensures we actually made the faked request


def test_get_coords_http_error(mocker):
    """Test that the application handles API failures gracefully."""
    mock_get = mocker.patch('models.requests.get')

    # Force requests to raise an HTTPError
    mock_get.return_value.raise_for_status.side_effect = HTTPError("401 Unauthorized")

    client = TomTomClient("fake_api_key")
    coords = client.get_coords("Invalid Address")

    assert coords is None


def test_commute_invalid_time_format():
    """Test that invalid time strings throw the correct exception."""
    bad_time = "Tomorrow at 9 AM"  # Not an ISO format

    # We expect this specific block of code to crash with a ValueError
    with pytest.raises(ValueError):
        Commute(travel_seconds=1800, arrival_iso=bad_time)