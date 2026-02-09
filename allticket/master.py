from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests

from tester import get_page_destination_data, save_concert

def get_all_concert_links(listing_url):
    links = []
    
    edge_options = Options()
    edge_options.add_argument("--headless=new") 

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    edge_options.add_argument(f'user-agent={user_agent}')

    edge_options.add_argument("--disable-gpu")
    edge_options.add_argument("--window-size=1920,1080")
    edge_options.add_argument("--disable-blink-features=AutomationControlled")
    edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    DRIVER_PATH = "msedgedriver.exe" 
    service = Service(executable_path=DRIVER_PATH)
    driver = webdriver.Edge(service=service, options=edge_options)

    try:
        print(f"🌍 Accessing listing page: {listing_url}")
        driver.get(listing_url)
        time.sleep(3) # Wait for initial load

        # Wait for buttons
        print("⏳ Waiting for 'Buy Now' buttons...")
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".btn-buy-now"))
            )
        except:
            print("⚠️ Could not find buttons. Page might be empty or loading slowly.")
            return []

        # 2. Get Initial Count
        buttons = driver.find_elements(By.CSS_SELECTOR, ".ticket .btn")
        total_events = len(buttons)
        print(f"🔍 Found {total_events} events. Starting Loop...")

        for i in range(total_events):
            try:
                # Re-locate elements (DOM refreshes after back button)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".btn-buy-now"))
                )
                current_buttons = driver.find_elements(By.CSS_SELECTOR, ".btn-buy-now")
                
                if i >= len(current_buttons):
                    print(f"⚠️ Index {i} skipped (buttons changed).")
                    continue

                target_button = current_buttons[i]
                
                # Scroll to it
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_button)
                time.sleep(1)

                # Click using JS (More reliable)
                print(f"👆 Clicking event #{i+1}...")
                driver.execute_script("arguments[0].click();", target_button)

                # Wait for URL change
                WebDriverWait(driver, 10).until(lambda d: "/event/" in d.current_url)
                
                # Grab URL
                current_url = driver.current_url
                print(f"🔗 Found: {current_url}")
                
                if current_url not in links:
                    links.append(current_url)

                # Go Back
                driver.back()
                time.sleep(3) # Wait for list to reload

            except Exception as e:
                print(f"❌ Error on event #{i+1}: {e}")
                try:
                    if "category/concert" not in driver.current_url:
                        driver.back()
                        time.sleep(3)
                except:
                    pass

    except Exception as e:
        print(f"❌ Critical Script Error: {e}")
    finally:
        driver.quit()
    
    return links

def trigger_cleanup(origin_name):
    url = "http://127.0.0.1:8000/api/concerts/cleanup"
    try:
        # ส่ง origin ไปบอก backend ว่าเจ้าไหนที่สแกนเสร็จแล้ว
        res = requests.post(url, json={"origin": origin_name}, timeout=10)
        print(f"\n🧹 Cleanup Status ({origin_name}): {res.status_code}")
        print(f"   Deleted (Soft): {res.json().get('deleted_count', 0)} items")
    except Exception as e:
        print(f"   ❌ Cleanup Failed: {e}")

if __name__ == "__main__":
    MAIN_PAGE_URL = "https://www.allticket.com/category/concert" 
    ORIGIN_NAME = "All Ticket"

    print("🚀 Starting AllTicket Scraper (Visible Mode)...")
    
    concert_urls = get_all_concert_links(MAIN_PAGE_URL)
    
    print(f"\n📂 Total unique concerts found: {len(concert_urls)}")
    print("-" * 50)

    for i, url in enumerate(concert_urls):
        print(f"\n[{i+1}/{len(concert_urls)}] Processing: {url}")
        try:
            concert_data = get_page_destination_data(url, headless=True, timeout=20)
            
            if concert_data:
                print(f"✅ Name: {concert_data.get('name')}")
                save_concert(concert_data) 
            else:
                print("⚠️ Data extraction failed.")
        except Exception as e:
            print(f"❌ Failed to process {url}: {e}")
        pass

    print("\n------------------------------------------------")
    print("🧹 Starting Cleanup process for missing concerts...")
    trigger_cleanup(ORIGIN_NAME)
    print("------------------------------------------------")

    print("\n🎉 All Done!")