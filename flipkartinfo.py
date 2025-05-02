import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from supabase import create_client, Client

url = "https://rnimvmsikqqtphckorjk.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJuaW12bXNpa3FxdHBoY2tvcmprIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NTk5MzY0NiwiZXhwIjoyMDYxNTY5NjQ2fQ.vVjAdbuIcTxIyU1nxY7LI9KyntA4ro51DAW89n-_EkE"
supabase: Client = create_client(url, key)

class SilentChrome(uc.Chrome):
    def __del__(self):
        try:
            if hasattr(self, "service") and hasattr(self.service, "process"):
                self.service.process.kill()
        except Exception:
            pass
        try:
            self.quit()
        except Exception:
            pass
def scrape_page(page_number):
    options = uc.ChromeOptions()
    options.add_argument("--headless")  

    driver = SilentChrome(options=options, version_main=135)

    url = f"https://www.flipkart.com/clothing-and-accessories/saree-and-accessories/saree/women-saree/pr?sid=clo,8on,zpd,9og&page={page_number}&otracker=categorytree&otracker=nmenu_sub_Women_0_Sarees"
    driver.get(url)

    try:
        close_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'✕')]"))
        )
        close_btn.click()
        time.sleep(2)
    except:
        pass

    titles = driver.find_elements(By.CLASS_NAME, "WKTcLC.BwBZTg")
    prices = driver.find_elements(By.CLASS_NAME, "Nx9bqj")
    discounts = driver.find_elements(By.CLASS_NAME, "UkUFwK")
    companies = driver.find_elements(By.CLASS_NAME, "syl9yP")

    sarees_data = []
    for title, price, discount, company in zip(titles, prices, discounts, companies):
        item = {
            "page": page_number,
            "title": title.text.strip(),
            "price": price.text.strip(),
            "discount": discount.text.strip(),
            "company": company.text.strip()
        }
        sarees_data.append(item)

    driver.quit()
    return sarees_data

total_pages = 20  
for page in range(1, total_pages + 1):
    page_data = scrape_page(page)
    
    for item in page_data:
        existing_item = supabase.table("saree_data").select("title").eq("title", item["title"]).execute()
        
        if not existing_item.data:  
            supabase.table("saree_data").insert(item).execute()

print("Data inserted into Supabase successfully.")
