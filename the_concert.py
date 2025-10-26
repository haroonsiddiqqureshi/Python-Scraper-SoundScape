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
            name_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "div.concert-title-box > h1",
                    )
                )
            )
            name = name_element.text
        except:
            name = None

        description = "No Description"

        try:
            description_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "div.note-editing-area > div.note-editable",
                    )
                )
            )
            description = description_element.text
        except:
            description = "No Description"

        try:
            image_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "#_main-body > div > div.container > div.concert-section-top > div.row > div.col-lg-5 > div > img",
                    )
                )
            )
            image_src = image_element.get_attribute("src")
        except:
            image_src = "https://www.facebook.com/"

        try:
            price_min_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "#_main-body > div > div.container > div.concert-section-top > div.row > div.col-lg-7 > div.side-box-btn > div > div.col-xl-6.col-sm-12.title-con > span.price",
                    )
                )
            )
            if price_min_element:
                price_min_text = price_min_element.text.replace("฿", "").strip()
                price_min = int(price_min_text)
        except:
            price_min = 0

        try:
            date_show_time_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "#date_showdate",
                    )
                )
            )

            months = {
                "ม.ค.": 1,
                "ก.พ.": 2,
                "ม.ค.": 3,
                "ม.ษ.": 4,
                "พ.ค.": 5,
                "ม.ย.": 6,
                "ก.ค.": 7,
                "ส.ค.": 8,
                "ก.ย.": 9,
                "ต.ค.": 10,
                "พ.ย.": 11,
                "ธ.ค.": 12,
            }

            date_split = date_show_time_element.text.split(" ")

            month = months[date_split[3]]
            year = "20" + date_split[-1]

            start_sale_date = f"{year}-{month}-{date_split[0]}"
            end_sale_date = f"{year}-{month}-{date_split[2]}"

        except:
            start_sale_date = None
            end_sale_date = None

        try:
            showtime_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "#date_showtime",
                    )
                )
            )

            text_split = showtime_element.text.split(" ")

            start_show_time = f"{text_split[0]}:00"
            end_show_time = f"{text_split[2]}:00"

        except:
            start_show_time = None
            end_show_time = None

        try:
            location_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "#_main-body > div > div.container > div.concert-section-top > div.row > div.col-lg-7 > div.concert-title-box > div.location-box > div > div > span > a",
                    )
                )
            )
            location = location_element.get_attribute("href").split("query=")[1].split(",")
            latitude = location[0]
            longitude = location[1]

        except:
            latitude = None
            longitude = None

        try:
            venue_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "#_main-body > div > div.container > div.concert-section-top > div.row > div.col-lg-7 > div.concert-title-box > div.location-box > div > div > span"
                    )
                )
            )
            venue_name = venue_element.text.strip("ดูเส้นทาง")

        except:
            venue_name = None

        return {
            "name": name or 'No Name',
            "description": description or 'No description',
            "picture_url": image_src,
            "price_min": price_min,
            "start_sale_date": start_sale_date,
            "end_sale_date": end_sale_date,
            "start_show_time": start_show_time,
            "end_show_time": end_show_time,
            "ticket_link" : url,
            "latitude" : latitude,
            "longitude" : longitude,
            "venue_name" : venue_name,
        }

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


def save_concert(data):
    """
    Sends a POST request to save a new concert and handles the response,
    including validation errors and connection issues.
    """
    url = "http://127.0.0.1:8000/api/concerts"

    try:
        # Set a timeout for the request to prevent hanging indefinitely
        res = requests.post(url, json=data, timeout=10)

        # Check for a successful creation status code
        if res.status_code == 201:
            print("Concert saved successfully. 🎉")
            # Optionally, you might want to print the newly created concert data
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

            print(f"Failed to save concert. Status Code {res.status_code}: {message}")

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
    url = "https://www.theconcert.com/concert/4507"

    res = requests.get(url)

    if res.status_code == 200:
        data = get_page_destination_data(url, headless=True, timeout=10)
        if data:
            # print(data)
            save_concert(data)
    else:
        print(f"Failed to retrieve the page. Status code: {res.status_code}")
