from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
from urllib.parse import urljoin

from tester import get_page_destination_data, save_concert

def get_all_concert_links(listing_url):
    """
    ฟังก์ชันสำหรับเข้าไปหน้า 'รวมคอนเสิร์ต' และดึงลิงก์ทั้งหมดออกมา
    (ปรับปรุงสำหรับ Next.js และ HTML โครงสร้างใหม่)
    """
    links = []
    
    edge_options = Options()
    edge_options.add_argument("--headless=new")  # ใช้โหมดใหม่
    edge_options.add_argument("--window-size=1920,1080")
    
    # ปลอม User-Agent (สำคัญมาก)
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    edge_options.add_argument(f'user-agent={user_agent}')
    
    # ปิดการตรวจจับ Bot
    edge_options.add_argument("--disable-blink-features=AutomationControlled")
    edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    edge_options.add_experimental_option('useAutomationExtension', False)
    edge_options.add_argument("--log-level=3")
    
    DRIVER_PATH = "msedgedriver.exe" 
    service = Service(executable_path=DRIVER_PATH)
    driver = webdriver.Edge(service=service, options=edge_options)

    try:
        print(f"🌍 Accessing listing page: {listing_url}")
        driver.get(listing_url)

        # รอให้หน้าโหลด: รอให้เจอ tag <a> ที่มี href ขึ้นต้นด้วย /events/
        print("⏳ Waiting for content to load...")
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href^='/events/']"))
            )
        except Exception:
            print("⚠️ Warning: Initial wait timed out (Web might be slow).")

        # Auto-Scroll
        print("⏳ Scrolling...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2.5) # พักนานนิดนึงให้ Next.js render ของ
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        print("🔍 Extracting links...")

        # วิธีที่ 1 หา <a> ที่ href มีคำว่า /events/
        elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/events/']")
        
        # วิธีที่ 2 (แผนสำรอง): ถ้าวิธีแรกได้น้อย หรือไม่ได้เลย ให้ใช้ Javascript ดึง
        if len(elements) == 0:
            print("⚠️ Selenium found 0 elements, trying JavaScript injection...")
            # สคริปต์ JS ดึงทุก Link ที่มีคำว่า /events/
            js_links = driver.execute_script("""
                var links = [];
                var elements = document.querySelectorAll("a[href*='/events/']");
                elements.forEach(e => links.push(e.href));
                return links;
            """)
            
            for raw_link in js_links:
                if "/events/" in raw_link and "login" not in raw_link:
                     # JS บางทีคืนค่าเป็น Relative path ต้องเช็ค
                    full_url = urljoin(listing_url, raw_link)
                    if full_url not in links:
                        links.append(full_url)
        else:
            # Loop ปกติจาก Selenium Elements
            for a in elements:
                try:
                    href = a.get_attribute("href")
                    if href and "/events/" in href and "login" not in href:
                        full_url = urljoin(listing_url, href)
                        if full_url not in links:
                            links.append(full_url)
                except:
                    continue

    except Exception as e:
        print(f"❌ Error getting links: {e}")
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
    # หน้า Ticketier
    MAIN_PAGE_URL = "https://www.ticketier.com/events"
    ORIGIN_NAME = "Ticketier"

    print("🚀 Starting Ticketier Master Scraper...")
    
    # 1. หาลิงก์ทั้งหมด
    concert_urls = get_all_concert_links(MAIN_PAGE_URL)
    
    print(f"\n📂 Total unique concerts found: {len(concert_urls)}")
    print("-" * 50)

    # 2. วนลูปดึงข้อมูลทีละลิงก์
    for i, url in enumerate(concert_urls):
        print(f"\n[{i+1}/{len(concert_urls)}] Processing: {url}")
        
        try:
            # เรียกฟังก์ชันจาก ticketier.py
            concert_data = get_page_destination_data(url, headless=True, timeout=20)
            
            if concert_data:
                print(f"   ✅ Name: {concert_data.get('name')}")
                save_concert(concert_data) # บันทึกข้อมูล
            else:
                print("   ⚠️ Data extraction failed or empty.")
                
        except Exception as e:
            print(f"   ❌ Failed to process {url}: {e}")
        pass

    print("\n------------------------------------------------")
    print("🧹 Starting Cleanup process for missing concerts...")
    trigger_cleanup(ORIGIN_NAME)
    print("------------------------------------------------")

    print("\n🎉 All Done!")