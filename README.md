# Car Subscription and Search Bot - README

## Overview

This project is a Telegram bot built with the `aiogram` framework. The bot allows users to subscribe to specific car models, receive updates about new car listings, and browse through different car brands and models. The bot scrapes data from external sources (like OTOMOTO) to provide users with up-to-date information about car listings.

## Features

- **Subscription to Car Updates**: Users can subscribe to specific car brands and models. The bot periodically checks for new listings and notifies the user about them.
- **Car Search**: Users can search for cars by brand and model and browse through available listings.
- **Main Menu**: A user-friendly interface that allows users to access subscription options, search for cars, and learn more about the bot.
- **Notifications**: The bot periodically checks for updates and notifies subscribed users about new car listings.
- **Pagination**: Users can browse through car listings with pagination buttons ("Next" and "Previous").

## Technologies Used

- **Python 3.9+**
- **aiogram**: A modern framework for Telegram bot development.
- **Asyncio**: For asynchronous tasks and background operations.
- **ThreadPoolExecutor**: For running blocking tasks in the background.
- **dotenv**: For handling environment variables securely.
- **Selenium/Web Scraper**: A custom `Scrapper` class is used to scrape car listing data from external websites.

## Prerequisites

1. Python 3.9+ installed on your system.
2. Telegram account to interact with the bot.
3. Access to a Telegram Bot API token (create one via [BotFather](https://core.telegram.org/bots#botfather)).
4. ChromeDriver installed (required for Selenium Web Scraping).

