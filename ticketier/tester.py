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
from utils.constants import months_map, valid_provinces


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
            name_selector = "body > main > div > div.relative > div.relative.p-6 > div > div.flex.flex-col.gap-6.rounded-card.bg-white.p-4.lg\:flex-row.lg\:gap-10 > div.flex.flex-1.flex-col > div.h6.lg\:h5.text-primary"
            name_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, name_selector))
            )
            name = name_element.text
        except:
            name = None

        # EVENT TYPE
        try:
            event_type_selector = "body > main > div > div.ms\:mt-14.mx-auto.mt-8.flex.max-w-7xl.flex-col.gap-6.px-4.sm\:px-26 > div > div.flex.grow.flex-col.gap-10 > div.flex.flex-col.gap-8 > div.flex.flex-row.items-center.gap-4 > p.b4-bold.cursor-pointer.rounded-full.border.border-solid.border-gray-200.px-\[20px\].py-1.uppercase.text-accent.hover\:bg-gray-50"
            event_type_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, event_type_selector))
            )
            if event_type_element.text == "MUSIC FESTIVALS":
                event_type = "เทศกาลดนตรี"
            elif event_type_element.text == "CONCERTS":
                event_type = "คอนเสิร์ต"
        except:
            event_type = None

        # DESCRIPTION
        description = "No Description"
        try:
            description_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.event-description")
                )
            )
            description = description_element.text
        except:
            description = "No Description"

        # IMAGE
        image_src = None
        try:
            image_selector = r"body > main > div > div.relative > div.relative.p-6 > div > div.flex.flex-col.gap-6.rounded-card.bg-white.p-4.lg\:flex-row.lg\:gap-10 > div.relative.aspect-\[5\/7\].w-full.overflow-hidden.rounded-brand.lg\:h-\[28rem\].lg\:w-fit > img.object-cover.lg\:hidden"

            image_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, image_selector))
            )

            image_src = image_element.get_attribute("src")

            if not image_src:
                image_src = image_element.get_attribute("srcset")

        except:
            image_src = None

        # PRICE MIN & MAX
        price_min, price_max = None, None
        try:
            # Selector เดิมของคุณ
            price_selector = "body > main > div > div.relative > div.relative.p-6 > div > div.flex.flex-col.gap-6.rounded-card.bg-white.p-4.lg\:flex-row.lg\:gap-10 > div.flex.flex-1.flex-col > div.mt-4.flex.flex-col.gap-2 > div:nth-child(4) > span.b3.flex-1.pt-1"
            
            price_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, price_selector))
            )
            price_text = price_element.text
            # ตัวอย่าง text: "Early Cow 2,000 THB / VIP Cow 4,000 THB"
            
            # ใช้ Regex ค้นหาตัวเลขทั้งหมด (รวมถึงที่มีลูกน้ำ เช่น 2,000)
            # \d+ = ตัวเลข, [,]* = มี comma หรือไม่ก็ได้
            import re
            matches = re.findall(r'[\d,]+', price_text)
            
            prices = []
            for m in matches:
                # ลบ comma ออกแล้วแปลงเป็น int
                clean_num = m.replace(",", "")
                # เช็คว่าเป็นตัวเลขล้วนๆ (ป้องกันกรณีเจอเครื่องหมายแปลกๆ)
                if clean_num.isdigit():
                    prices.append(int(clean_num))
            
            if prices:
                price_min = min(prices) # ราคาต่ำสุด (2000)
                price_max = max(prices) # ราคาสูงสุด (4000)

                # If min and max are the same, set max to None
                if price_min == price_max:
                    price_max = None
                
        except:
            price_min, price_max = None, None

        # LATITUDE & LONGITUDE
        latitude, longitude = None, None
        try:
            map_selector = r"body > main > div > div.relative > div.relative.p-6 > div > div.flex.flex-col.gap-6.rounded-card.bg-white.p-4.lg\:flex-row.lg\:gap-10 > div.flex.flex-1.flex-col > div.mt-4.flex.flex-col.gap-2 > div:nth-child(5) > div > a"
            
            map_link_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, map_selector))
            )
            map_url = map_link_element.get_attribute("href")

            if map_url:
                driver.execute_script("window.open(arguments[0]);", map_url)
                driver.switch_to.window(driver.window_handles[-1])

                try:
                    consent_xpath = "//button[@aria-label='Accept all'] | //span[contains(text(), 'Accept all')] | //span[contains(text(), 'ยอมรับทั้งหมด')]"
                    WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, consent_xpath))
                    ).click()
                except:
                    pass

                try:
                    WebDriverWait(driver, 15).until(
                        lambda d: "@" in d.current_url or "q=" in d.current_url or "/place/" in d.current_url
                    )
                except:
                    pass

                current_map_url = driver.current_url

                import re
                match = re.search(r'@([-.\d]+),([-.\d]+)', current_map_url)
                
                if not match:
                    match = re.search(r'q=([-.\d]+),([-.\d]+)', current_map_url)
                
                if not match:
                     match = re.search(r'!3d([-.\d]+)!4d([-.\d]+)', current_map_url)

                if match:
                    latitude = match.group(1)
                    longitude = match.group(2)

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

        except:
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            latitude, longitude = None, None

        # DATE SALE
        date_sale = None
        try:
            sale_selector = 'body > main > div > div.relative > div.relative.p-6 > div > div.flex.flex-col.gap-6.rounded-card.bg-white.p-4.lg\:flex-row.lg\:gap-10 > div.flex.flex-1.flex-col > div.mt-4.flex.flex-col.gap-2 > div:nth-child(1) > div > span.b3'
            
            sale_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, sale_selector))
            )
            
            # ตัดแบ่งข้อความด้วย " | " ก่อน (เช่น "5 Sep 2025 | 10:00 AM")
            sale_text_full = sale_element.text.upper()
            sale_text_date_part = sale_text_full.split("|")[0].strip()# ได้ "5 Sep 2025"
            
            # ตัดแบ่งช่องว่างเพื่อแยก วัน เดือน ปี
            sale_parts = sale_text_date_part.split(" ") # ได้ ['5', 'Sep', '2025']

            if len(sale_parts) == 3:
                day = int(sale_parts[0])
                month_str = sale_parts[1]
                year = int(sale_parts[2]) # ปีเป็น ค.ศ. อยู่แล้ว (2025) ไม่ต้องลบ
                
                month = months_map.get(month_str, 1) # แปลงชื่อเดือนเป็นตัวเลข
                
                date_sale = datetime.date(year, month, day)
            
        except:
            date_sale = None

        # DATE START & END
        try:
            date_selector = 'body > main > div > div.relative > div.relative.p-6 > div > div.flex.flex-col.gap-6.rounded-card.bg-white.p-4.lg\:flex-row.lg\:gap-10 > div.flex.flex-1.flex-col > div.mt-4.flex.flex-col.gap-2 > div:nth-child(2) > span.b3.flex-1.pt-1'
            date_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, date_selector))
            )
            date_text = date_element.text.strip()

            date_parts = date_text.split(" ")
            date_parts = [p for p in date_parts if p.strip()]

            # Case A: แบบระบุเดือนทั้งคู่ (ยาว 6) -> "06 ธ.ค. - 07 ธ.ค. 2025"
            if len(date_parts) == 6 and "-" in date_parts:
                start_day = int(date_parts[0])
                start_month_str = date_parts[1]
                
                end_day = int(date_parts[3])
                end_month_str = date_parts[4]
                
                year_str = date_parts[5]
                year = int(year_str)

                start_month = months_map.get(start_month_str, 1)
                end_month = months_map.get(end_month_str, 1)

                date_start = datetime.date(year, start_month, start_day)
                date_end = datetime.date(year, end_month, end_day)

            # Case B: แบบเดือนเดียว (ยาว 5) -> "06 - 07 ธ.ค. 2025"
            elif len(date_parts) == 5 and "-" in date_parts:
                start_day = int(date_parts[0])
                end_day = int(date_parts[2])
                month_str = date_parts[3]
                year_str = date_parts[4]

                month = months_map.get(month_str, 1)
                year = int(year_str)

                date_start = datetime.date(year, month, start_day)
                date_end = datetime.date(year, month, end_day)

            # Case C: วันเดียว (ยาว 3) -> "06 ธ.ค. 2025"
            elif len(date_parts) == 3:
                day = int(date_parts[0])
                month_str = date_parts[1]
                year_str = date_parts[2]

                month = months_map.get(month_str, 1)
                year = int(year_str)

                date_start = datetime.date(year, month, day)
                date_end = date_start
            
            else:
                date_start, date_end = None, None

        except:
            date_start, date_end = None, None

        # START TIME
        time_start = None
        try:
            time_selector = 'body > main > div > div.relative > div.relative.p-6 > div > div.flex.flex-col.gap-6.rounded-card.bg-white.p-4.lg\:flex-row.lg\:gap-10 > div.flex.flex-1.flex-col > div.mt-4.flex.flex-col.gap-2 > div:nth-child(3) > span.b3.flex-1.pt-1'
            time_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, time_selector))
            )
            time_text = time_element.text.strip()
            # Example data: "Gate opens 12:00 PM onwards" or "9.30"

            match = re.search(r'(\d{1,2})[:.](\d{2})(?:\s*([APap]\.?[Mm]\.?))?', time_text)

            if match:
                hour = int(match.group(1))
                minute = int(match.group(2))
                ampm = match.group(3) # This will be "PM", "am", etc., or None

                # 2. Add Convert Logic (12h -> 24h)
                if ampm:
                    ampm_clean = ampm.replace(".", "").upper() # Normalize to "PM" or "AM"
                    
                    if ampm_clean == "PM" and hour != 12:
                        hour += 12
                    elif ampm_clean == "AM" and hour == 12:
                        hour = 0

                # Format specifically as H:i:s (e.g., "09:30:00")
                time_start = f"{hour:02}:{minute:02}:00"
            else:
                time_start = None

        except:
            time_start = None

        # VENUE NAME
        venue_name = None
        try:
            venue_selector = r'body > main > div > div.relative > div.relative.p-6 > div > div.flex.flex-col.gap-6.rounded-card.bg-white.p-4.lg\:flex-row.lg\:gap-10 > div.flex.flex-1.flex-col > div.mt-4.flex.flex-col.gap-2 > div:nth-child(5) > div > span.b3-bold.text-primary'
            
            venue_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, venue_selector))
            )
            venue_name = venue_element.text.strip()

        except:
            venue_name = None

        # PROVINCE
        province = None
        try:
            province_selector = r'body > main > div > div.relative > div.relative.p-6 > div > div.flex.flex-col.gap-6.rounded-card.bg-white.p-4.lg\:flex-row.lg\:gap-10 > div.flex.flex-1.flex-col > div.mt-4.flex.flex-col.gap-2 > div:nth-child(5) > div > span.b3.text-gray-400'
            
            province_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, province_selector))
            )
            raw_province_text = province_element.text.strip()

            # วนลูปเช็คว่ามีจังหวัดไหนอยู่ในข้อความ raw_province_text บ้าง
            matched_province = None
            for p in valid_provinces:
                # ใช้ .lower() เพื่อเปรียบเทียบแบบไม่สนตัวพิมพ์เล็กใหญ่ (Case Insensitive)
                if p.lower() in raw_province_text.lower():
                    matched_province = p
                    break # เจอแล้วหยุดทันที (ได้จังหวัดแรกที่เจอ)
            
            province = matched_province
            print(f"Debug Province: Raw='{raw_province_text}' -> Extracted='{province}'")

        except:
            province = None

        return {
            "name": name,
            "event_type": event_type,
            "description": description,
            "picture_url": image_src,
            "start_sale_date": str(date_sale) if date_sale else None,
            "start_show_date": str(date_start) if date_start else None,
            "end_show_date": str(date_end) if date_end else None,
            "start_show_time": time_start,
            "price_min": price_min,
            "price_max": price_max,
            "latitude": latitude,
            "longitude": longitude,
            "venue_name": venue_name,
            "province_name": province,
            "ticket_link": url,
            "origin": "Ticketier"
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
    url = "https://www.ticketier.com/events/baekhyun2025"
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
