import sys
import os
import re
import requests
import datetime
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.constants import months_map
from utils.geocoder import get_province_thailand

def get_page_destination_data(url, headless=False, timeout=10):
    edge_options = Options()
    edge_options.add_argument("--log-level=3")
    edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    if headless:
        edge_options.add_argument("--headless=new") 
        edge_options.add_argument("--window-size=1920,1080")
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        edge_options.add_argument(f'user-agent={user_agent}')
        edge_options.add_argument("--disable-blink-features=AutomationControlled")
        edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        edge_options.add_experimental_option('useAutomationExtension', False)

    driver = None
    DRIVER_PATH = "msedgedriver.exe"
    service = Service(executable_path=DRIVER_PATH)

    try:
        if not os.path.exists(DRIVER_PATH):
            raise FileNotFoundError(f"Edge Driver file not found at: {DRIVER_PATH}")

        driver = webdriver.Edge(service=service, options=edge_options)
        driver.set_page_load_timeout(timeout)

        driver.get(url)

        # ---------------------------------------------------------
        # Auto-Scroll
        # ---------------------------------------------------------
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        # ---------------------------------------------------------

        # NAME
        try:
            name_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.concert-title-box > h1"))
            )
            name = name_element.text
        except:
            name = None

        # EVENT TYPE
        try:
            event_type_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#_main-body > div > div.container > div.concert-section-top > div.row > div.col-lg-7 > div.concert-title-box > div.genre-box > ul > li"))
            )
            event_type = event_type_element.text
        except:
            event_type = None


        # DESCRIPTION
        description = "No Description"
        try:
            description_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.note-editing-area > div.note-editable"))
            )
            description = description_element.text
        except:
            description = "No Description"

        # IMAGE (ปรับปรุงใหม่)
        image_src = None
        try:
            image_selector = "#_main-body > div > div.container > div.concert-section-top > div.row > div.col-lg-5 > div > img"
            
            image_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, image_selector))
            )
            
            # Scroll ไปหารูป
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", image_element)
            time.sleep(0.5)

            image_src = image_element.get_attribute("src")
            
            # เช็ค data-src หรือกรณีรูปยังไม่โหลด
            if not image_src or "default" in image_src or "data:image" in image_src:
                temp_src = image_element.get_attribute("data-src")
                if temp_src:
                    image_src = temp_src
                    
        except:
            image_src = None

        # PRICE MIN
        try:
            price_min_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.price"))
            )
            price_min = int(price_min_element.text.strip(" ฿").replace(",", ""))
        except:
            price_min = 0

        # LATITUDE & LONGITUDE
        try:
            map_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.location-direct > a"))
            )
            map_url = map_element.get_attribute("href")
            lat_long = map_url.split("query=")[1]
            latitude, longitude = lat_long.split(",")
        except:
            latitude, longitude = None, None

        # PROVINCE
        province = None
        if latitude and longitude:
            print(f"🔎 Reverse Geocoding: {latitude}, {longitude}...")
            province = get_province_thailand(latitude, longitude)
            if province:
                print(f"✅ Province Found: {province}")
            else:
                print(f"❌ Province Not Found for: {latitude}, {longitude}")

        # VENUE NAME
        try:
            venue_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.location-direct"))
            )
            venue_text = venue_element.text.split(" ดูเส้นทาง")
            venue_name = venue_text[0]
        except:
            venue_name = None

        # DATE START & END
        try:
            date_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#date_showdate"))
            )
            date_text = date_element.text

            date_parts = date_text.split(" ")
            
            if len(date_parts) == 7 and "-" in date_parts[3]:  # Case: "31 ธ.ค. 25 - 1 ม.ค. 26"
                start_day = int(date_parts[0])
                end_day = int(date_parts[4])
                start_month_str = date_parts[1]
                end_month_str = date_parts[5]
                start_year_str = date_parts[2]
                end_year_str = date_parts[6]
                
                start_month = months_map.get(start_month_str, 1)
                end_month = months_map.get(end_month_str, 1)
                start_year = int(start_year_str) + 2000
                end_year = int(end_year_str) + 2000
                
                date_start = datetime.date(start_year, start_month, start_day)
                date_end = datetime.date(end_year, end_month, end_day)

            elif len(date_parts) == 6 and "-" in date_parts[2]:  # Case: "30 ม.ค. - 1 ก.พ. 26"
                start_day = int(date_parts[0])
                end_day = int(date_parts[3])
                start_month_str = date_parts[1]
                end_month_str = date_parts[4]
                year_str = date_parts[5]
                
                start_month = months_map.get(start_month_str, 1)
                end_month = months_map.get(end_month_str, 1)
                year = int(year_str) + 2000 
                
                date_start = datetime.date(year, start_month, start_day)
                date_end = datetime.date(year, end_month, end_day)

            elif len(date_parts) == 5 and "-" in date_parts[1]:  # Case: "26 - 31 ธ.ค. 25"
                start_day = int(date_parts[0])
                end_day = int(date_parts[2])
                month_str = date_parts[3]
                year_str = date_parts[4]
                
                month = months_map.get(month_str, 1)
                year = int(year_str) + 2000 
                
                date_start = datetime.date(year, month, start_day)
                date_end = datetime.date(year, month, end_day)

            # NOT DONE
            elif len(date_parts) == 3:  # Case: "27 ธ.ค. 25"
                day = int(date_parts[0])
                month_str = date_parts[1]
                year_str = date_parts[2]
                
                month = months_map.get(month_str, 1)
                year = int(year_str) + 2000
                
                date_start = datetime.date(year, month, day)
                date_end = None
            else:
                 date_start, date_end = None, None

        except:
            date_start, date_end = None, None

        return {
            "name": name,
            "event_type": event_type,
            "description": description,
            "picture_url": image_src,
            "start_show_date": str(date_start) if date_start else None,
            "end_show_date": str(date_end) if date_end else None,
            "price_min": price_min,
            "latitude": latitude,
            "longitude": longitude,
            "venue_name": venue_name,
            "province_name": province,
            "ticket_link": url,
            "origin": "The Concert"
        }

    except Exception as e:
        print(f"Error processing {url}: {e}")
        return None
    finally:
        if driver:
            driver.quit()

def save_concert(data):
    """
    Sends a POST request to save a new concert and handles the response.
    """
    url = "http://127.0.0.1:8000/api/concerts"

    try:
        res = requests.post(url, json=data, timeout=10)

        if res.status_code == 201:
            print(f"Concert '{data.get('name')}' saved successfully. 🎉")
        elif res.status_code == 422:
            try:
                error_data = res.json()
                print(f"Validation Error (422): {error_data}")
            except requests.exceptions.JSONDecodeError:
                print(f"Validation Error (422): Could not decode JSON response.")
        else:
            try:
                 message = res.json().get("message", "No message provided")
            except:
                 message = res.text
            print(f"Failed to save concert. Status Code {res.status_code}: {message}")

    except requests.exceptions.ConnectionError:
        print(f"Connection Error: Could not connect to API at {url}")
    except requests.exceptions.RequestException as e:
        print(f"An unexpected request error occurred: {e}")

if __name__ == "__main__":
    url = "https://www.theconcert.com/concert/4564" 
    print(f"🚀 Starting scraper test for: {url}")

    # แนะนำให้ลองปิด headless=False ในรอบแรกเพื่อดูว่า Browser เปิดขึ้นมาจริงไหม
    data = get_page_destination_data(url, headless=True, timeout=20)

    if data:
        print("\n--- Extracted Data ---")
        for key, value in data.items():
            print(f"{key}: {value}")
        print("----------------------\n")
        # save_concert(data)
    else:
        print("❌ No data extracted or failed to load page.")