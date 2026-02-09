# Concert Scraper

This project is a Python-based web scraper designed to extract concert information from "theconcert.com". It uses `requests`, `BeautifulSoup`, and `Selenium` to parse an HTML file, follow links to individual concert pages, and extract detailed information. The scraped data is then sent to a local API endpoint.

## Features

-   Parses a local HTML file (`index.html`) to find concert links.
-   Navigates to each concert's page using Selenium.
-   Extracts details such as concert name, description, image, price, dates, and location.
-   Saves the extracted data by making a POST request to a local API.
-   Handles potential errors during web scraping and API communication.

## File Descriptions

-   `app.py`: The main script that reads `index.html`, finds all concert links, and orchestrates the scraping process by calling functions from `show.py`.
-   `show.py`: Contains the core scraping logic. It uses a headless Edge browser (via Selenium) to open concert pages and extract detailed information. It also includes the `save_concert` function to post the data to the API.
-   `index.html`: A static HTML file containing the list of concerts that the scraper uses as its starting point.
-   `requirements.txt`: A list of all the Python packages required to run the project.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/haroonsiddiqqureshi/Python-Scraper-SoundScape.git
    cd Python-Scraper-SoundScape
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Download the Edge WebDriver:**
    This project uses Selenium with Microsoft Edge. You need to download the correct version of `msedgedriver.exe` that matches your Edge browser version.
    -   You can download it from the [official Microsoft Edge WebDriver page](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/).
    -   Place the `msedgedriver.exe` file in the root of the project directory.

## Usage

1.  **Start the local API:**
    The `save_concert` function in `show.py` sends data to `http://127.0.0.1:8000/api/concerts`. Make sure you have a local server running that can receive POST requests at this endpoint.

2.  **Run the scraper:**
    To start the scraping process, run the `app.py` script:
    ```bash
    python app.py
    ```
    The script will process `index.html`, visit each concert link, and save the data.

## Dependencies

The project's dependencies are listed in `requirements.txt`. Key dependencies include:

-   `requests`
-   `beautifulsoup4`
-   `selenium`
-   `webdriver-manager`
