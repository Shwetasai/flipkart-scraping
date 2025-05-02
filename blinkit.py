from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json
from selenium.webdriver.common.action_chains import ActionChains

driver = webdriver.Chrome()
url = 'https://blinkit.com/s/?q=fruits'
driver.get(url)
time.sleep(5)

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
            #driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'end'});", last)
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


data = []

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


    data.append({
        'product_name': product_name,
        'actual_price': actual_price,
        'selling_price': selling_price,
        'discount': discount,
        'weight': weight,
        'reached_time': reached_time_global  
    })

with open('fruits_data.json', 'w', encoding='utf-8') as json_file:
    json.dump(data, json_file, indent=4, ensure_ascii=False)

driver.quit()


