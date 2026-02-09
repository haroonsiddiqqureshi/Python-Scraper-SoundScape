from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import requests
import datetime
import time 

def get_page_destination_data(url, headless=False, timeout=10):
    edge_options = Options()
    
    edge_options.add_argument("--log-level=3")
    edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    if headless:
        edge_options.add_argument("--headless")
        edge_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
        )
    
    edge_options.add_argument("--window-size=1920,1080")
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

        print("⏳ Start scrolling to load all artists...")
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("✅ Scrolling finished.")
                break
            last_height = new_height

        try:
            artist_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.PostArtist"))
            )

            artists = []
            print(f"🔍 Found {len(artist_elements)} elements. Extracting data...")

            for i, artist_element in enumerate(artist_elements):
                try:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", artist_element)
                    time.sleep(0.1)

                    name_element = artist_element.find_element(By.CSS_SELECTOR, "div.PostArtistName")
                    name_artist = name_element.text

                    picture_element = artist_element.find_element(By.CSS_SELECTOR, "div.rezyImageFrame > img")
                    
                    picture_artist = picture_element.get_attribute("src")

                    if not picture_artist:
                        picture_artist = picture_element.get_attribute("data-src")

                    if (
                        picture_artist == "https://static.joox.com/pc/prod/static/di/default/default-artist@300.png"
                    ):
                        picture_artist = None

                    artists.append({
                        "name" : name_artist,
                        "picture_url" : picture_artist
                    })

                except Exception as inner_e:
                    print(f"⚠️ Skipping artist index {i}: {inner_e}")
                    continue

        except Exception as e:
            print(f"Error finding elements: {e}")
            artists = None

        return artists

    except FileNotFoundError as fne:
        print(f"Error: {fne}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if driver:
            driver.quit()


def save_artist(data):
    url = "http://127.0.0.1:8000/api/artists"
    try:
        res = requests.post(url, json=data, timeout=10)
        
        if res.status_code in [200, 201]:
            print(f"✅ Saved/Processed: {data['name']}")
        elif res.status_code == 422:
            print(f"❌ Validation Error: {res.json()}")
        else:
            print(f"⚠️ Failed: {res.status_code} - {res.text}")
            
    except Exception as e:
        print(f"Request Error: {e}")


if __name__ == "__main__":
    url = "https://www.joox.com/th/artists/266"
    res = requests.get(url)

    if res.status_code == 200:
        data = get_page_destination_data(url, headless=True, timeout=20)
        if data:
            print(f"🎉 Total artists collected: {len(data)}")
            for artist in data:
                print(artist)
                # save_artist(artist)
    else:
        print(f"Failed to retrieve page: {res.status_code}")