import requests
from bs4 import BeautifulSoup
import smtplib 
import os 
import datetime 
import csv      
import time

# --- CLOUD CONFIGURATION ---
MY_EMAIL = os.environ.get("MY_EMAIL") 
MY_PASSWORD = os.environ.get("MY_PASSWORD")
DESTINATION_EMAIL = os.environ.get("DESTINATION_EMAIL")

# --- THE SHOPPING MALL (Option A: Hardcore AI & Gaming) ---
products = [
    # 🥇 PRIMARY TARGET: Acer Predator Helios Neo 16 (i9-14900HX / RTX 4070)
    # Note: If i9 is out of stock on Amazon, this link tracks the i7-14700HX variant which is also a beast.
    { 
        "name": "Acer Predator Helios Neo 16 (i9/i7 RTX 4070)", 
        "url": "https://www.amazon.in/dp/B0CX8WZYC3", # CHECK LINK: Verify this matches the RTX 4070 model
        "target_price": 150000 
    },

    # 🥈 SECONDARY TARGET: Lenovo Legion Pro 5i (i7-14650HX / RTX 4070)
    # The gold standard for cooling.
    { 
        "name": "Lenovo Legion Pro 5i (RTX 4070)", 
        "url": "https://www.amazon.in/dp/B0D1Y5231P", # CHECK LINK: Search "Lenovo Legion Pro 5i RTX 4070" to confirm
        "target_price": 150000 
    },

    # 🥉 BACKUP OPTION: ASUS ROG Strix G16 (i9 / RTX 4060/4070)
    # A great alternative if the others are too expensive.
    { 
        "name": "ASUS ROG Strix G16", 
        "url": "https://www.amazon.in/dp/B0C3R3X4G7", 
        "target_price": 140000 
    },

    # 🍎 THE REFERENCE (To see how cheap Macs get)
    { 
        "name": "MacBook Air M4 (Reference)", 
        "url": "https://www.amazon.in/dp/B0DZDDKTQZ", 
        "target_price": 100000 
    }
]

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "https://www.google.com/"
}

def send_alert(name, price, link):
    print(f"📧 Sending email for {name}...")
    subject = f"PRICE DROP: {name} is Rs. {price}!"
    body = f"The price of {name} dropped to Rs. {price}.\nBuy it here: {link}"
    msg = f"Subject: {subject}\n\n{body}"
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(MY_EMAIL, MY_PASSWORD)
        server.sendmail(MY_EMAIL, DESTINATION_EMAIL, msg)
        print("✅ Email Sent Successfully!")
        server.quit()
    except Exception as e:
        print(f"🚫 Error: {e}")

def get_price_amazon(soup):
    price_container = soup.find(id="corePriceDisplay_desktop_feature_div")
    if price_container:
        all_prices = price_container.find_all(class_="a-price-whole")
        extracted_prices = []
        for p in all_prices:
            text = p.get_text().strip().replace(",", "").replace(".", "")
            if text.isdigit():
                price_val = int(text)
                if price_val > 1000: 
                    extracted_prices.append(price_val)
        if extracted_prices:
            return min(extracted_prices)
    return None

def check_price(product):
    url = product["url"]
    target_price = product["target_price"]
    name = product["name"]

    print(f"🔎 Checking {name}...")
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            current_price = None

            if "amazon" in url:
                current_price = get_price_amazon(soup)
            else:
                print(f"⚠️ Unknown website for {name}")
                return

            if current_price:
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"💰 {name}: Rs. {current_price}")
                
                file_path = 'price_history.csv'
                is_new_file = not os.path.exists(file_path)
                with open(file_path, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    if is_new_file:
                            writer.writerow(['Timestamp', 'Product', 'Price', 'Website'])
                    site_name = "Amazon" 
                    writer.writerow([current_time, name, current_price, site_name])
                    print(f"✅ Saved data for {name}")

                if current_price < target_price:
                    print("🚨 Target Met!")
                    if MY_EMAIL and MY_PASSWORD:
                        send_alert(name, current_price, url)
                else:
                    print("Price is still high.")
            else:
                print(f"⚠️ Could not find price on page for {name}")
        else:
            print(f"❌ Status Code {response.status_code} for {name}")
            
    except Exception as e:
        print(f"🚫 Error checking {name}: {e}")

print("--- Starting Mall Check ---")
for item in products:
    check_price(item)
    print("-" * 30)
