import requests
from bs4 import BeautifulSoup
import os
import json
from dotenv import load_dotenv

print("== Script started ==")

load_dotenv()

url = os.getenv('URL')
user_agent = os.getenv('USER_AGENT')
timeout = int(os.getenv('TIMEOUT'))

headers = {'User-Agent': user_agent}

try:
    response = requests.get(url, headers=headers, timeout=timeout)
    print("Status Code:", response.status_code)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        title_tag = soup.find('h1', class_='bfsTitle remove-margin')
        title = title_tag.get_text(strip=True) if title_tag else 'Title not found'

        location_tag = soup.select_one('span.f-l.cs-800.flex-center.g8.opacity-70')
        location = location_tag.get_text(strip=True) if location_tag else 'Location not found'

        country = 'USA' if 'MA' in location else 'Unknown'

        def get_main_span_text(span):
            if span:
                return span.contents[0].strip() if span.contents else None
            return None

        spans = soup.find_all('span', class_='normal flex-center g4')

        asking_price = get_main_span_text(spans[0]) if len(spans) > 0 else 'Not found'
        cash_flow = get_main_span_text(spans[1]) if len(spans) > 1 else 'Not found'
        gross_revenue = get_main_span_text(spans[2]) if len(spans) > 2 else 'Not found'
        ebitda = get_main_span_text(spans[3]) if len(spans) > 3 else 'Not found'
        ff_and_e = get_main_span_text(spans[4]) if len(spans) > 4 else 'Not found'
        inventory = get_main_span_text(spans[5]) if len(spans) > 5 else 'Not found'
        rent = get_main_span_text(spans[6]) if len(spans) > 6 else 'Not found'
        established = get_main_span_text(spans[7]) if len(spans) > 7 else 'Not found'

        desc_div = soup.find('div', class_='businessDescription f-m word-break')
        description = desc_div.get_text(strip=True) if desc_div else 'Description not found'

        details_section = soup.find('dl', id='ctl00_ctl00_Content_ContentPlaceHolder1_wideProfile_listingDetails_dlDetailedInformation')
        detailed_info = {}

        if details_section:
            dts = details_section.find_all('dt')
            dds = details_section.find_all('dd')
            for dt, dd in zip(dts, dds):
                label = dt.get_text(strip=True).rstrip(':')
                value = dd.get_text(strip=True)
                detailed_info[label] = value

        website_tag = soup.find('a', id='ctl00_ctl00_Content_ContentPlaceHolder1_wideProfile_listingDetails_hlWebsite')
        website = website_tag['href'] if website_tag else 'Not found'

        data = {
            "Title": title,
            "Location": location,
            "Country": country,
            "Asking Price": asking_price,
            "Cash Flow": cash_flow,
            "Gross Revenue": gross_revenue,
            "EBITDA": ebitda,
            "FF&E": ff_and_e,
            "Inventory": inventory,
            "Rent": rent,
            "Established": established,
            "Business Description": description,
            "Business Website": website,
            "Detailed Information": detailed_info
        }

        with open('business_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print("Data saved to business_data.json")

    else:
        print("Failed to fetch page. Status code:", response.status_code)

except requests.exceptions.Timeout:
    print("Request timed out.")
except requests.exceptions.RequestException as e:
    print("Request failed:", e)

print("== Script finished ==")
