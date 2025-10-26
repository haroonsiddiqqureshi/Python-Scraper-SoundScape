from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import requests
import datetime


def get_page_destination_data(url, headless=False, timeout=10):
    edge_options = Options()

    if headless:
        edge_options.add_argument("--headless")
        edge_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
        )

    edge_options.add_argument("--no-sandbox")
    edge_options.add_argument("--disable-dev-shm-usage")
    edge_options.add_argument("--disable-gpu")
    edge_options.add_argument("--disable-extensions")

    driver = None

    DRIVER_PATH = "msedgedriver.exe"

    service = Service(executable_path=DRIVER_PATH)

    try:
        if not os.path.exists(DRIVER_PATH):
            raise FileNotFoundError(f"Edge Driver file not found at: {DRIVER_PATH}")

        driver = webdriver.Edge(service=service, options=edge_options)
        driver.set_page_load_timeout(timeout)

        driver.get(url)

        try:
            artist_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (
                        By.CSS_SELECTOR,
                        "div.PostArtist",
                    )
                )
            )

            artists = []

            for artist_element in artist_elements:
                name_element = artist_element.find_element(
                    By.CSS_SELECTOR, "div.PostArtistName"
                )
                name_artist = name_element.text

                picture_element = artist_element.find_element(
                    By.CSS_SELECTOR, "div.rezyImageFrame> img"
                )
                picture_artist = picture_element.get_attribute("src")
                # if (
                #     picture_artist
                #     == "https://static.joox.com/pc/prod/static/di/default/default-artist@300.png"
                # ):
                #     picture_artist = None
                
                artists.append({
                    "name" : name_artist,
                    "picture_url" : picture_artist
                })
        except:
            artists = None

        return artists

    except FileNotFoundError as fne:
        print(f"Error: {fne}")
        print(
            "\n💡 Please ensure you have downloaded 'msedgedriver.exe' and updated the DRIVER_PATH variable with the correct file location."
        )
    except Exception as e:
        error_message = str(e)
        print(f"An error occurred: {error_message}")
    finally:
        if driver:
            driver.quit()


def save_artist(data):
    """
    Sends a POST request to save a new artist and handles the response,
    including validation errors and connection issues.
    """
    url = "http://127.0.0.1:8000/api/artists"

    try:
        # Set a timeout for the request to prevent hanging indefinitely
        res = requests.post(url, json=data, timeout=10)

        # Check for a successful creation status code
        if res.status_code == 201:
            print("Artist saved successfully. 🎉")
            # Optionally, you might want to print the newly created artist data
            # print(f"Details: {res.json()}")

        # Handle validation errors (422 Unprocessable Entity)
        elif res.status_code == 422:
            try:
                error_data = res.json()
                print(
                    f"Validation Error (422): {error_data.get('message', 'Validation error')}"
                )

                # Print individual field errors if available
                errors = error_data.get("errors")
                if errors:
                    print("\nDetailed Errors:")
                    for field, messages in errors.items():
                        print(f"  - {field}: {', '.join(messages)}")
            except requests.exceptions.JSONDecodeError:
                print(
                    f"Validation Error (422): Could not decode JSON response. Response text: {res.text}"
                )

        # Handle other non-success status codes
        else:
            try:
                # Attempt to get a message from the JSON response
                message = res.json().get("message", "No message provided")
            except requests.exceptions.JSONDecodeError:
                # If JSON decoding fails, use the raw status code and text
                message = f"Could not decode JSON response. Text: {res.text}"

            print(f"Failed to save artist. Status Code {res.status_code}: {message}")

    # Catch network/connection-related exceptions (e.g., server down, DNS error, timeout)
    except requests.exceptions.ConnectionError:
        print(
            f"Connection Error: Could not connect to the API at {url}. Is the server running?"
        )
    except requests.exceptions.Timeout:
        print("Timeout Error: The request took too long to complete.")
    except requests.exceptions.RequestException as e:
        # Catch any other requests-related exception
        print(f"An unexpected request error occurred: {e}")


if __name__ == "__main__":
    url = "https://www.joox.com/th/artists/266"

    res = requests.get(url)

    if res.status_code == 200:
        data = get_page_destination_data(url, headless=True, timeout=10)
        if data:
            for artist in data :
                # print(artist)
                save_artist(artist)
    else:
        print(f"Failed to retrieve the page. Status code: {res.status_code}")
