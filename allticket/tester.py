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
from utils.constants import months_map, province_map
from utils.geocoder import get_coordinates

def get_page_destination_data(url, headless=True, timeout=10):
    edge_options = Options()
    edge_options.add_argument("--log-level=3")
    edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    if headless:
        edge_options.add_argument("--headless=new") 
        edge_options.add_argument("--window-size=1920,1080")
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        edge_options.add_argument(f'user-agent={user_agent}')
        edge_options.add_argument("--disable-blink-features=AutomationControlled")

    driver = None
    DRIVER_PATH = "msedgedriver.exe"
    service = Service(executable_path=DRIVER_PATH)

    try:
        if not os.path.exists(DRIVER_PATH):
            raise FileNotFoundError(f"Edge Driver file not found at: {DRIVER_PATH}")

        driver = webdriver.Edge(service=service, options=edge_options)
        driver.set_page_load_timeout(timeout)

        driver.get(url)

        driver.execute_script("window.scrollTo(0, 300);")
        time.sleep(2) 

        # NAME
        name = None
        try:
            # Look for an h4 tag anywhere inside the header container
            name_selector = ".eventDescHeader h4"
            
            # Wait for VISIBILITY, not just presence (ensures it's rendered)
            name_element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, name_selector))
            )
            name = name_element.text.strip()
        except:
            name = None

        # DESCRIPTION
        description = "No Description"
        try:
            info_wrapper = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//div[contains(@class, 'wrapper-event-info')]")
                )
            )
            description = info_wrapper.text.strip()

        except:
            description = "No Description"

        # IMAGE
        image_src = None
        try:
            image_selector = ".eventDescHeader img"
            
            image_element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, image_selector))
            )

            image_src = image_element.get_attribute("src")
            if not image_src:
                image_src = image_element.get_attribute("srcset")
            
        except:
            image_src = None

        # DATE START & END
        date_start, date_end = None, None

        try:
            header_element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".eventDescHeader"))
            )
            full_text = header_element.text.upper() # Convert to UPPER for easier matching
            
            # Remove commas to prevent parsing errors (e.g. "Aug 12, 2024")
            full_text = full_text.replace(",", " ")
                        
            # Construct regex pattern for months
            month_pattern = "|".join(months_map.keys()) 
            
            # Search for: "12 AUG 2024" or "12 - 14 AUG 2024"
            date_regex = re.compile(r"(\d{1,2})\s*(?:-\s*(\d{1,2}))?\s+(" + month_pattern + r")\s+(\d{4})")
            
            match = date_regex.search(full_text)

            if match:
                start_day = int(match.group(1))
                end_day_str = match.group(2) # Might be None
                month_str = match.group(3)
                year = int(match.group(4))
                
                month = months_map.get(month_str, 1)

                date_start = datetime.date(year, month, start_day)
                
                if end_day_str:
                    # It is a range (e.g., 12 - 14 AUG)
                    end_day = int(end_day_str)
                    date_end = datetime.date(year, month, end_day)
                else:
                    # Single date
                    date_end = date_start            

        except:
            date_start, date_end = None, None

        # SHOW TIME
        show_time = None
        try:
            header_element = driver.find_element(By.CSS_SELECTOR, ".eventDescHeader")
            full_text = header_element.text
            
            time_match = re.search(r'\b(\d{1,2})[:.](\d{2})(?:\s*([APap]\.?[Mm]\.?))?\b', full_text)
            
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2))
                ampm = time_match.group(3) # This will be "PM", "P.M.", "am", or None
                
                # Logic: Convert 12-hour to 24-hour if AM/PM is detected
                if ampm:
                    ampm_clean = ampm.replace(".", "").upper() # Normalize to "PM" or "AM"
                    
                    if ampm_clean == "PM" and hour != 12:
                        hour += 12
                    elif ampm_clean == "AM" and hour == 12:
                        hour = 0
                
                # Format strictly as HH:MM (e.g., 01:00 PM -> 13:00)
                show_time = f"{hour:02}:{minute:02}:00"
        except:
            show_time = None

        # PRICE MIN & MAX
        price_min, price_max = None, None
        try:
            price_element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//*[contains(@class, 'eventDescHeader')]//*[contains(text(), 'THB') or contains(text(), 'บาท')]")
                )
            )
            price_text = price_element.text

            # DATA CLEANING
            matches = re.findall(r'[\d,]+', price_text)
            
            prices = []
            for m in matches:
                # Remove commas
                clean_num = m.replace(",", "")
                
                if clean_num.isdigit():
                    val = int(clean_num)
                    if val != 2024 and val != 2025 and val != 2026 and val != 2027 and val != 2028: 
                        prices.append(val)
            
            # Calculate Min/Max
            if prices:
                price_min = min(prices)
                price_max = max(prices)
            
            # If Min and Max are the same, set Max to None
            if price_min == price_max:
                price_max = None
        except:
            price_min, price_max = None, None

        # VENUE NAME && PROVINCE
        venue_name, province = None, None
        try:
            venue_name_element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".eventDescHeader"))
            )
            all_spans = venue_name_element.find_elements(By.TAG_NAME, "span")

            # ดึงข้อความดิบจาก Span ตัวที่ 3
            raw_text = all_spans[2].text.strip()

            # ------------------------------------------
            # 1. หา VENUE NAME (ตัดคำพวก อ., จ., , ออก)
            # ------------------------------------------
            temp_name = raw_text
            if "อ." in temp_name:
                temp_name = temp_name.split("อ.")[0]
            elif "จ." in temp_name:
                temp_name = temp_name.split("จ.")[0]
            elif "," in temp_name:
                temp_name = temp_name.split(",")[0]

            # คลีนตัวอักษรพิเศษออกจากชื่อสถานที่
            clean_text = re.sub(r'[,\-\.\(\)]', ' ', temp_name)
            venue_name = re.sub(r'\s+', ' ', clean_text).strip()

            # ------------------------------------------
            # PROVINCE MATCHING
            # ------------------------------------------
            matched_province = None
            raw_text_lower = raw_text.lower()

            # Iterate through our merged map
            for search_term, official_name in province_map.items():
                if search_term in raw_text_lower:
                    matched_province = official_name
                    break 

            province = matched_province
            print(f"Debug Province: Raw='{raw_text}' -> Extracted='{province}'")
        except:
            venue_name = None

        # LATITIDE & LONGITUDE
        latitude, longitude = None, None
            
        if venue_name:
            print(f"🔎 Geocoding: {venue_name}, {province}...")
                
            lat, lng = get_coordinates(venue_name, province)
                
            if lat:
                latitude = lat
                longitude = lng
                print(f"✅ Coordinates Found: {latitude}, {longitude}")
            else:
                print(f"❌ Coordinates Not Found for: {venue_name}")

        return {
            "name": name,
            "event_type": "คอนเสิร์ต",
            "description": description,
            "picture_url": image_src,
            "start_show_date": str(date_start) if date_start else None,
            "end_show_date": str(date_end) if date_end else None,
            "start_show_time": show_time,
            "price_min": price_min,
            "price_max": price_max,
            "latitude": latitude,
            "longitude": longitude,
            "venue_name": venue_name,
            "province_name": province,
            "ticket_link": url,
            "origin": "All Ticket"
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
    url = "https://www.allticket.com/event/BILLKIN_FEELQUENCY"
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