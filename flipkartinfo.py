import time
import csv
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

def scrape_page(page_number):
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    driver = uc.Chrome(options=options)

    url = f"https://www.flipkart.com/clothing-and-accessories/saree-and-accessories/saree/women-saree/pr?sid=clo,8on,zpd,9og&page={page_number}&otracker=categorytree&otracker=nmenu_sub_Women_0_Sarees"
    driver.get(url)
    time.sleep(5)

    try:
        close_btn = driver.find_element(By.XPATH, "//button[contains(text(),'✕')]")
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
            "title": title.text,
            "price": price.text,
            "discount": discount.text,
            "company": company.text
        }
        sarees_data.append(item)

    driver.quit()
    return sarees_data

total_pages = 10
all_data = {}
csv_data = []

for page in range(1, total_pages + 1):
    page_data = scrape_page(page)
    all_data[f"page {page}"] = page_data
    for item in page_data:
        csv_data.append({
            "page": page,
            "title": item["title"],
            "price": item["price"],
            "discount": item["discount"],
            "company": item["company"]
        })

with open("flipkart_sarees_all.json", "w", encoding="utf-8") as jsonfile:
    json.dump(all_data, jsonfile, ensure_ascii=False, indent=4)

print("Data saved to 'flipkart_sarees_all.csv' and 'flipkart_sarees_all.json'.")
