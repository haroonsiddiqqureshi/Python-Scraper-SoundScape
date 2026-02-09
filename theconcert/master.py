from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from urllib.parse import urljoin

# นำเข้าฟังก์ชันจากไฟล์ the_concert.py (ต้องวางไฟล์ไว้ที่เดียวกัน)
from tester import get_page_destination_data, save_concert

def get_all_concert_links(listing_url):
    """
    ฟังก์ชันสำหรับเข้าไปหน้า 'รวมคอนเสิร์ต' และดึงลิงก์ทั้งหมดออกมา
    """
    links = []
    
    edge_options = Options()
    edge_options.add_argument("--log-level=3")
    edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    edge_options.add_argument("--headless")
    edge_options.add_argument("--window-size=1920,1080")
    
    DRIVER_PATH = "msedgedriver.exe" 
    service = Service(executable_path=DRIVER_PATH)
    driver = webdriver.Edge(service=service, options=edge_options)

    try:
        print(f"🌍 Accessing listing page: {listing_url}")
        driver.get(listing_url)

        # ---------------------------------------------------------
        # 1. Auto-Scroll: เลื่อนลงเพื่อโหลดรายการคอนเสิร์ตให้ครบ
        # ---------------------------------------------------------
        print("⏳ Scrolling to load all concerts...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        # วนลูปเลื่อนลงเรื่อยๆ (ปรับจำนวนรอบหรือเงื่อนไขได้ตามต้องการ)
        # ถ้าคอนเสิร์ตเยอะมาก อาจจะจำกัดรอบ loop ไว้ เช่น for _ in range(10):
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2) # รอโหลด
            
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("✅ Scroll finished (End of page reached).")
                break
            last_height = new_height
        # ---------------------------------------------------------

        print("🔍 Extracting links...")

        # ---------------------------------------------------------
        # 2. ใช้ Selector หาลิงก์คอนเสิร์ต
        # จากไฟล์ HTML ที่คุณเคยส่งมา ลิงก์จะอยู่ใน div.concert-list
        # ---------------------------------------------------------
        target_selector = "div.concert-list a"
        
        try:
            # รอให้ Element ปรากฏ
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, target_selector))
            )
            
            # ดึง <a> tags ทั้งหมด
            a_elements = driver.find_elements(By.CSS_SELECTOR, target_selector)
            print(f"   Found {len(a_elements)} potential links.")

            for a in a_elements:
                try:
                    href = a.get_attribute("href")
                    
                    # กรองเฉพาะลิงก์ที่เป็นหน้าคอนเสิร์ต (/concert/...)
                    # และไม่เอาลิงก์ที่เป็นหน้า Login หรือหน้าอื่นๆ
                    if href and "/concert/" in href and "login" not in href:
                        
                        full_url = urljoin(listing_url, href)
                        
                        # เช็คซ้ำป้องกันลิงก์เบิ้ล
                        if full_url not in links:
                            links.append(full_url)
                            # print(f"      + Found: {full_url}") # Uncomment ถ้าอยากเห็นลิงก์ไหลมา
                            
                except Exception:
                    continue

        except Exception as e:
            print(f"⚠️ Could not find concert elements: {e}")
        # ---------------------------------------------------------

    except Exception as e:
        print(f"❌ Error getting links: {e}")
    finally:
        driver.quit()
    
    return links

if __name__ == "__main__":
    # URL หน้ารวมคอนเสิร์ตของ The Concert
    MAIN_PAGE_URL = "https://www.theconcert.com/concert" 

    print("🚀 Starting The Concert Master Scraper...")
    
    # 1. ไปกวาดลิงก์มาให้หมด
    concert_urls = get_all_concert_links(MAIN_PAGE_URL)
    
    print(f"\n📂 Total unique concerts found: {len(concert_urls)}")
    print("-" * 50)

    # 2. วนลูปส่งแต่ละลิงก์ไปให้ตัว Scraper หลักทำงาน
    for i, url in enumerate(concert_urls):
        print(f"\n[{i+1}/{len(concert_urls)}] Processing: {url}")
        
        try:
            # เรียกใช้ฟังก์ชันจาก the_concert.py
            # timeout 20 วินาที เพื่อให้เวลาโหลดแผนที่/รูป
            concert_data = get_page_destination_data(url, headless=True, timeout=20)
            
            if concert_data:
                print(f"   ✅ Name: {concert_data.get('name')}")
                save_concert(concert_data)
            else:
                print("   ⚠️ Data extraction failed or empty.")
                
        except Exception as e:
            print(f"   ❌ Failed to process {url}: {e}")

    print("\n🎉 All Done!")