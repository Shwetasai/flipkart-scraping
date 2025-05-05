from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.action_chains import ActionChains
from supabase import create_client, Client
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from selenium.common.exceptions import TimeoutException

driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://blinkit.com/")

wait = WebDriverWait(driver, 20)
actions = ActionChains(driver)

SUPABASE_URL = 'https://rnimvmsikqqtphckorjk.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJuaW12bXNpa3FxdHBoY2tvcmprIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NTk5MzY0NiwiZXhwIjoyMDYxNTY5NjQ2fQ.vVjAdbuIcTxIyU1nxY7LI9KyntA4ro51DAW89n-_EkE'
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
#location entry
try:
    search_input = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//input[@placeholder="search delivery location"]')
    ))
    driver.execute_script("arguments[0].scrollIntoView(true);", search_input)
    time.sleep(2)
    search_input.clear()
    search_input.send_keys("Delhi")
    wait.until(EC.presence_of_all_elements_located(
        (By.XPATH, '//div[contains(@class, "LocationSearchList__LocationListContainer-sc-93rfr7-0")]')
    ))

    first_suggestion = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '(//div[contains(@class, "LocationSearchList__LocationListContainer-sc-93rfr7-0")])[1]')
    ))
    driver.execute_script("arguments[0].scrollIntoView(true);", first_suggestion)
    time.sleep(1)
    actions.move_to_element(first_suggestion).click().perform()
    time.sleep(5)
except Exception as e:
    print("❌ Failed to set location to Delhi:", str(e))
    driver.quit()
    exit()

#login
try:
    login_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//div[@class="ProfileButton__Container-sc-975teb-3 liSUTa"]')
    ))
    login_button.click()
    phone_input = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//input[@data-test-id="phone-no-text-box"]')
    ))
    phone_input.send_keys("8533846404")
    continue_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//button[contains(text(), "Continue")]')
    ))
    continue_button.click()
    print("🚨 Please manually enter the OTP in the browser within the next 30 seconds...")
    time.sleep(30)

except Exception as e:
    print("❌ Login failed:", str(e))
    driver.quit()
    exit()
print("✅ Login complete.")

###go to search projects(fruits)
try:
    time.sleep(2)    
    search_placeholder = wait.until(EC.element_to_be_clickable((
        By.CLASS_NAME, "SearchBar__PlaceholderContainer-sc-16lps2d-0"
    )))
    search_placeholder.click()

    search_input = wait.until(EC.presence_of_element_located((
        By.TAG_NAME, "input"
    )))
    wait.until(EC.element_to_be_clickable((By.TAG_NAME, "input")))

    search_input.clear()
    search_input.send_keys("fruits")
    time.sleep(3)
except Exception as e:
    print("❌ Failed to search:", repr(e))

#scrape all data 
possible_times = driver.find_elements(By.CSS_SELECTOR, "div[class*='uppercase']")
reached_time_global = ''
for el in possible_times:
    text = el.text.strip()
    if "MIN" in text.upper():
        reached_time_global = text
        break

actions = ActionChains(driver)
prev_count = 0
same_count_repeat = 0
max_repeats = 6

while True:
    products = driver.find_elements(By.CSS_SELECTOR, 'div[data-pf="reset"].tw-relative.tw-flex.tw-h-full.tw-flex-col')

    if products:
        last = products[-1]
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            actions.move_to_element(last).perform()
        except:
            pass

    time.sleep(2)
    current_count = len(products)
    print(f"Products loaded: {current_count}")

    if current_count == prev_count:
        same_count_repeat += 1
        if same_count_repeat >= max_repeats:
            break
    else:
        same_count_repeat = 0
        prev_count = current_count
existing_keys = set()
try:
    response = supabase.table('fruitss_data').select('product_name', 'weight').execute()
    if hasattr(response, 'data') and response.data:
        for item in response.data:
            key = f"{item['product_name']}|{item['weight']}"
            existing_keys.add(key)
except Exception as e:
    print(f"Failed to fetch existing records: {e}")
data = []
seen_products = set()
for product in products:
    try:
        product_name = product.find_element(By.CSS_SELECTOR, 'div.tw-text-300.tw-font-semibold.tw-line-clamp-2').text
    except:
        product_name = ''

    try:
        actual_price = product.find_element(By.CSS_SELECTOR, 'div.tw-line-through').text
    except:
        actual_price = ''

    try:
        selling_price = product.find_element(By.CSS_SELECTOR, 'div.tw-text-200.tw-font-semibold').text
    except:
        selling_price = ''

    try:
        discount = product.find_element(By.CSS_SELECTOR, 'div.tw-absolute.tw-z-20.tw-w-5').text
    except:
        discount = ''

    try:
        weight = product.find_element(By.CSS_SELECTOR, 'div.tw-text-200.tw-font-medium.tw-line-clamp-1').text
    except:
        weight = ''
    if not product_name:
        continue
    key = f"{product_name}|{weight}"
    if key in seen_products:
        continue
    key = f"{product_name}|{weight}"
    if key in seen_products or key in existing_keys:
        continue
    seen_products.add(key)
    
    record = {
        'product_name': product_name,
        'actual_price': actual_price,
        'selling_price': selling_price,
        'discount': discount,
        'weight': weight,
        'reached_time': reached_time_global
    }
    data.append(record)
print(f"Collected {len(data)} unique products.")

#add product in cart
product_list = [
    {"name": "Kiran Watermelon (Tarbuj)", "qty": 2},
    {"name": "Green Grapes 500 g", "qty": 3},
    {"name": "Banana", "qty": 1}
]

for item in product_list:
    name = item["name"]
    qty = item["qty"]
    
    try:
        product = wait.until(EC.presence_of_element_located(
            (By.XPATH, f'//div[contains(text(), "{name}")]')
        ))
        product_card = product.find_element(By.XPATH, './ancestor::div[contains(@class, "tw-flex tw-w-full tw-flex-col")]')
        add_button = product_card.find_element(By.XPATH, './/div[text()="ADD"]')

        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", add_button)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", add_button)
        time.sleep(1)

        if qty > 1:
            for _ in range(qty - 1):
                try:
                    plus_button = product_card.find_element(By.XPATH, './/button[2]/span[contains(@class, "icon-plus")]')
                    driver.execute_script("arguments[0].click();", plus_button)
                    time.sleep(0.5)
                except Exception as e:
                    print(f"❌ '+' button not found or not clickable for '{name}': {e}")
                    break

        try:
            product_card.find_element(By.XPATH, f'.//div[contains(text(), "{qty}")]')
            print(f'"{name}" added to cart with quantity {qty}.')
        except:
            try:
                wait.until(EC.presence_of_element_located(
                    (By.XPATH, '//div[contains(@class, "CartButton__Badge") and text()!=""]')
                ))
                print(f'"{name}" likely added with quantity {qty} (verified by badge).')
            except:
                print(f'Cart not updated properly for "{name}".')

    except Exception as e:
        print(f'Error adding "{name}": {e}')

#billing details
time.sleep(3)
try:
    cart_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'CartButton__Container')]"))
    )
    cart_button.click()
    cart_popup = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//div[text()='Items total']"))
    )

    item_total_original = wait.until(
        EC.presence_of_element_located((By.XPATH,
            "(//div[text()='Items total']/ancestor::div[contains(@class,'BillCard__BillItemLeft')]/following-sibling::div//span[@data-pf='reset'])[2]"
        ))
    ).text

    item_total_discounted = wait.until(
    EC.presence_of_element_located((By.XPATH,
        "//div[text()='Items total']/ancestor::div[contains(@class,'BillCard__BillItemLeft')]/following-sibling::div//span/span[2]"
    ))
    ).text

    delivery_charge = wait.until(
    EC.presence_of_element_located((By.XPATH,
        "//div[text()='Delivery charge']/ancestor::div[contains(@class,'BillCard__BillItemLeft')]/following-sibling::div//span[@data-pf='reset']"
    ))
    ).text

    handling_charge = wait.until(
    EC.presence_of_element_located((By.XPATH,
        "//div[text()='Handling charge']/ancestor::div[contains(@class,'BillCard__BillItemLeft')]/following-sibling::div//span[@data-pf='reset']"
    ))
    ).text

    grand_total = wait.until(
    EC.presence_of_element_located((By.XPATH,
        "//div[text()='Grand total']/ancestor::div[contains(@class,'BillCard__BillItemLeft')]/following-sibling::div//div[@data-pf='reset' and contains(@class,'tw-font-semibold')]"
    ))
    ).text

    from datetime import datetime

    bill_record = {
    'item_total_original': item_total_original.replace("₹", "").strip(),
    'item_total_discounted': item_total_discounted.replace("₹", "").strip(),
    'delivery_charge': delivery_charge.replace("₹", "").strip(),
    'handling_charge': handling_charge.replace("₹", "").strip(),
    'grand_total': grand_total.replace("₹", "").strip(),
    'timestamp': datetime.now().isoformat()
}
    try:
        response = supabase.table('billing_data').insert(bill_record).execute()

        if response.data:
            print("✅ Bill data inserted into Supabase.")
        else:
            print("⚠️ Insert may have failed. Response data is empty.")
    except TimeoutException:
        print("❌ Timeout: Cart details did not load.")
    except Exception as e:
        print("❌ Error during scraping or saving:", repr(e))


finally:
    driver.quit()
