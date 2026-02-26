# 🚗 Smart Commute Dashboard

![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/status-active-success)

A professional Python-based CLI utility that calculates optimal departure times using real-time traffic data from the TomTom Routing and Search APIs. This project demonstrates clean architecture, object-oriented design, and comprehensive input validation.

---

## 🛡️ Core Features

- **Geocoding Engine**: Converts physical addresses and landmarks into precise geographic coordinates
- **Live Traffic Integration**: Leverages TomTom's routing algorithms to account for current road conditions and traffic delays
- **Robust Input Validation**: Enforces ISO 8601 timestamp formats, validates travel modes, and checks for future arrival times
- **Professional Documentation**: Fully implemented PEP 8 type hinting and comprehensive docstrings

---

## 🛠️ Technical Stack

- **Language**: Python 3.12+
- **APIs**: TomTom Routing API, TomTom Search API
- **Key Libraries**: `requests`, `python-dotenv`, `datetime`

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.12 or higher
- A [TomTom Developer Account](https://developer.tomtom.com/) (free tier available)

### 1. Clone the Repository
```bash
git clone https://github.com/thor-manchul/smart-commute-dashboard.git
cd smart-commute-dashboard
```

### 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate     # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:
```env
Copy the template: cp .env.example .env

Open .env and enter your TomTom API key.

TOMTOM_API_KEY=your_tomtom_api_key_here
```

> **Security Note**: The `.env` file is git-ignored to protect your API credentials.

---

## 📖 Usage

Run the application:
```bash
python main.py
```

### Example Input
```
📍 Start Address: University of Calgary
🏁 Destination: Chinook Centre
⏰ Arrival Time (YYYY-MM-DDTHH:MM:SS): 2026-02-26T08:30:00
🚲 Mode (car/bicycle/pedestrian) [car]: car
```

### Example Output
```
✅ Input validated successfully!
🔍 Looking up addresses...
🚗 Calculating route...

==============================
📊 COMMUTE RESULTS
==============================
⏰ Travel Time: 18 mins | 🚀 Leave by: 08:12 AM
==============================
```

---

## 📂 Project Structure
```
smart-commute-dashboard/
├── main.py           # Application controller and user interaction
├── models.py         # TomTomClient (API service) and Commute (data model)
├── .env              # API credentials (git-ignored)
├── .gitignore        # Excludes sensitive files
├── requirements.txt  # Python dependencies
├── LICENSE           # MIT License
└── README.md         # Project documentation
```

---

## 🏗️ Architecture

This project follows a **Service-Oriented Architecture (SOA)** with clear separation of concerns:

### `main.py` - Application Controller (Presentation Layer)
Manages application lifecycle, user input validation, and coordinates API calls.

**Key Features:**
- Class-level constants for configuration
- Comprehensive input validation with `datetime.fromisoformat()`
- Future time validation
- User-friendly error messages with emoji indicators

### `models.py` - Service Layer (Business Logic)

**`TomTomClient`** (Service): Handles all external API communication with proper error handling, timeouts, and retry logic.

**`Commute`** (Data Model): Encapsulates commute calculation logic and formats output.

**Design Pattern**: Controller-Service-Model architecture ensures loose coupling and makes the codebase testable and maintainable.

---

## 🧪 Input Validation

The application enforces strict validation:

- ✅ Non-empty fields (addresses and arrival time)
- ✅ Minimum 3-character addresses
- ✅ ISO 8601 datetime format (`YYYY-MM-DDTHH:MM:SS`)
- ✅ Future arrival times only
- ✅ Valid travel modes: `car`, `bicycle`, `pedestrian`

---

## 🔒 Security Best Practices

- **Environment Variable Protection**: API keys stored in `.env` and excluded from version control
- **Input Sanitization**: All user inputs sanitized with `.strip()` to prevent injection of malformed data
- **Request Timeouts**: 10-second timeouts prevent hanging connections and resource exhaustion
- **Error Handling**: Comprehensive exception handling prevents exposure of sensitive stack traces
- **Rate Limit Protection**: Validation loop prevents infinite retry cycles that could trigger API key revocation
- **Future Time Validation**: Prevents processing of past timestamps that could cause unexpected behavior

---

## 🚦 API Rate Limits

This project uses TomTom's free tier:
- **2,500 requests/day**
- Automatically capped (no overage charges)

---

## 🛣️ Future Enhancements

- [ ] Add support for multi-stop routes
- [ ] Implement route alternatives comparison
- [ ] Add transit mode support
- [ ] Create web interface with Flask/FastAPI
- [ ] Add unit tests with pytest
- [ ] Implement caching to reduce API calls

---

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

---

## 👤 Author

**Thor Manchul**
- GitHub: [@thor-manchul](https://github.com/thor-manchul)
- LinkedIn: [Thor Manchul](https://www.linkedin.com/in/thor-manchul-5857213a6/)

---

## 🙏 Acknowledgments

- [TomTom Developer Portal](https://developer.tomtom.com/) for providing the routing and search APIs
