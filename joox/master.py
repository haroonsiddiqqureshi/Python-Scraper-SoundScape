from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from urllib.parse import urljoin

# นำเข้าฟังก์ชันจากไฟล์ artist.py (ต้องวางไฟล์ artist.py ไว้ที่เดียวกัน)
from tester import get_page_destination_data, save_artist

def get_all_category_links(listing_url):
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

        print("⏳ Scrolling to load content...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        print("✅ Scroll finished. Extracting links...")

        # ==================================================================================
        # เป้าหมาย: ค้นหา <a> ที่อยู่ใน div.CateArtist
        # ตัวอย่าง HTML: <a href="/th/artists/193" ...>
        # ==================================================================================
        
        target_selector = "div.CateArtist a"
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, target_selector))
        )
        
        a_elements = driver.find_elements(By.CSS_SELECTOR, target_selector)
        print(f"   Found {len(a_elements)} potential category links.")

        for a in a_elements:
            try:
                href = a.get_attribute("href")
                title = a.get_attribute("title") # ดึงชื่อหมวดหมู่มาโชว์ด้วย (เช่น "ศิลปินไทย ชายเดี่ยว")
                
                # กรองลิงก์: เอาเฉพาะที่มีคำว่า /artist/ หรือ /artists/
                if href and ("artist" in href):
                    full_url = urljoin(listing_url, href)
                    
                    if full_url not in links:
                        links.append(full_url)
                        # print(f"      + Found Category: {title} -> {full_url}")
                        
            except Exception:
                continue
        # ==================================================================================

    except Exception as e:
        print(f"❌ Error getting links: {e}")
    finally:
        driver.quit()
    
    return links

if __name__ == "__main__":
    # URL หน้าหลักที่มีกล่องหมวดหมู่ศิลปิน
    MAIN_PAGE_URL = "https://www.joox.com/th/artists" 

    print("🚀 Starting Category Scraper...")
    
    # 1. ไปดึงลิงก์หมวดหมู่ (เช่น ศิลปินไทยชาย, หญิง)
    category_urls = get_all_category_links(MAIN_PAGE_URL)
    
    print(f"\n📂 Found {len(category_urls)} categories to process.")
    print("-" * 50)

    # 2. วนลูปเข้าไปเจาะดูแต่ละหมวดหมู่
    for i, url in enumerate(category_urls):
        print(f"\n[{i+1}/{len(category_urls)}] Processing Category: {url}")
        
        try:
            # เรียกใช้ฟังก์ชันเดิม (artist.py) เพื่อดึงรายชื่อศิลปินในหมวดนั้นๆ
            # เพิ่ม timeout หน่อยเผื่อหน้านั้นมีศิลปินเยอะ
            artist_data = get_page_destination_data(url, headless=True, timeout=30)
            
            if artist_data:
                print(f"   ✅ Extracted {len(artist_data)} artists from this category.")
                for item in artist_data:
                    save_artist(item)
            else:
                print("   ⚠️ No artists found in this category.")
                
        except Exception as e:
            print(f"   ❌ Failed to process {url}: {e}")

    print("\n🎉 All Done!")