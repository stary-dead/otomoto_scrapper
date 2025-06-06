# Otomoto Scrapper - Car Listing & Notification Bot

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)

## 📖 Overview

Otomoto Scrapper is a comprehensive solution for automated car listing monitoring and notification. It's built as a Telegram bot that scrapes automobile marketplace websites (including Kleinanzeigen and Otomoto) to deliver real-time updates on car listings based on user-defined criteria. The project demonstrates advanced web scraping techniques, asynchronous programming, and interactive Telegram bot development.

## 🚀 Features

- **Multi-source Web Scraping**: Extract car listings from various sources including Kleinanzeigen and Otomoto
- **Custom Filtering**: Filter cars by brand, model, price range, year, mileage, fuel type, and transmission
- **Personalized Subscriptions**: Users can create multiple saved searches with different criteria
- **Real-time Notifications**: Automated alerts when new matching listings are found
- **Interactive UI**: Clean Telegram interface with inline buttons for navigation
- **Detailed Car Information**: View comprehensive listing details including images and seller information
- **Pagination Support**: Browse through multiple search results with ease

## 🛠️ Technologies

- **Python 3.9+**
- **aiogram**: Modern Telegram Bot API framework
- **Selenium**: Advanced web scraping and browser automation
- **BeautifulSoup4**: HTML parsing for data extraction
- **asyncio**: Asynchronous programming for non-blocking operations
- **pytest**: Comprehensive testing framework

## 📋 Prerequisites

1. Python 3.9 or higher
2. Chrome/Chromium browser (for the Selenium WebDriver)
3. Telegram account
4. Bot API token from [BotFather](https://t.me/botfather)

## ⚙️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/otomoto_scrapper.git
   cd otomoto_scrapper
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development and testing
   ```

4. Create a `.env` file in the project root with your configuration:
   ```
   BOT_API_TOKEN=your_telegram_bot_token_here
   # Add other configuration variables as needed
   ```

## 🚦 Usage

1. Start the bot:
   ```bash
   python main.py
   ```

2. Open Telegram and search for your bot by username

3. Start interacting with the bot by sending the `/start` command

4. Use the menu to:
   - Search for cars
   - Create and manage subscriptions
   - View saved searches
   - Receive notifications about new listings

## 👨‍💻 Development

### Project Structure

```
otomoto_scrapper/
├── articles/              # Car listing models
├── filters/               # Search filtering logic
├── handlers/              # Telegram message handlers
├── scrappers/             # Web scraping modules
├── tests/                 # Test suite
│   ├── mocks/             # Mock objects for testing
│   └── ...                # Test modules
├── utils/                 # Helper utilities
├── .env                   # Environment variables (not in repo)
├── main.py                # Application entry point
└── README.md              # This documentation
```

### Main Components

- **Articles**: Data models for car listings
- **Filters**: Search filters and criteria logic
- **Handlers**: Telegram bot conversation flows
- **Scrappers**: Web scraping implementations for different sources
- **Tests**: Comprehensive test suite

## 🧪 Testing

The project includes a comprehensive test suite using pytest. Tests are organized to verify functionality of all major components.

To run the tests:

```bash
# Run all tests
python -m pytest tests/

# Run tests with verbose output
python -m pytest tests/ -v
```

### Mock Testing

The project uses mock objects to test components independently:

```python
# Example of a mock test
def test_filter_apply(kleinzengen_filter, kleinzengen_article):
    # Test filtering logic with mock objects
    kleinzengen_filter.min_price = 5000
    kleinzengen_filter.max_price = 15000
    assert kleinzengen_filter.apply(kleinzengen_article) is True
```

## 🔍 Future Enhancements

- Add support for more car marketplaces
- Implement machine learning for price prediction
- Add image recognition for car condition assessment
- Create a web dashboard interface

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

- Your Name
- [Your GitHub](https://github.com/yourusername)
- [Your LinkedIn](https://linkedin.com/in/yourprofile)

---

If you find this project useful or have suggestions for improvements, please open an issue or submit a pull request!

