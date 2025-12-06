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

# --- THE SHOPPING MALL (10 Item Dream List) ---
products = [
    # --- APPLE ---
    { "name": "MacBook Air M4 (13-inch)", "url": "https://www.amazon.in/dp/B0DZDDKTQZ", "target_price": 110000 },
    { "name": "MacBook Pro M4 (14-inch)", "url": "https://www.amazon.in/dp/B0DZDDK21R", "target_price": 155000 },
    
    # --- GAMING (HIGH END) ---
    { "name": "Lenovo Legion 5 Pro (RTX 4070)", "url": "https://www.amazon.in/dp/B0CX8WZYC3", "target_price": 145000 },
    { "name": "ASUS ROG Zephyrus G14", "url": "https://www.amazon.in/dp/B09T9CQ5DR", "target_price": 135000 },
    { "name": "HP Omen 16 (RTX 4060)", "url": "https://www.amazon.in/dp/B0C2D1P9F8", "target_price": 105000 },
    { "name": "Dell Alienware m16", "url": "https://www.amazon.in/dp/B0C3R3X4G7", "target_price": 180000 },

    # --- GAMING (BUDGET/MID) ---
    { "name": "Acer Predator Helios Neo 16", "url": "https://www.amazon.in/dp/B0C2D1P9F8", "target_price": 110000 },
    { "name": "MSI Katana 15", "url": "https://www.amazon.in/dp/B0C3R3X4G7", "target_price": 95000 },

    # --- CODING WORKHORSES ---
    { "name": "Dell XPS 15", "url": "https://www.amazon.in/dp/B0C3R3X4G7", "target_price": 200000 },
    { "name": "ASUS Vivobook Pro 15 OLED", "url": "https://www.amazon.in/dp/B0C3R3X4G7", "target_price": 85000 }
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
    """Specific logic for extracting price from Amazon"""
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

def get_price_flipkart(soup):
    """Specific logic for extracting price from Flipkart"""
    # Flipkart usually uses this class for the main price
    price_element = soup.find(class_="Nx9bqj CxhGGd") 
    if price_element:
        text = price_element.get_text().strip().replace(",", "").replace("₹", "")
        if text.isdigit():
            return int(text)
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

            # --- SITE DETECTION LOGIC ---
            if "amazon" in url:
                current_price = get_price_amazon(soup)
            elif "flipkart" in url:
                current_price = get_price_flipkart(soup)
            else:
                print(f"⚠️ Unknown website for {name}")
                return

            # --- RESULT PROCESSING ---
            if current_price:
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"💰 {name}: Rs. {current_price}")
                
                # Save to CSV
                file_path = 'price_history.csv'
                is_new_file = not os.path.exists(file_path)
                with open(file_path, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    if is_new_file:
                            writer.writerow(['Timestamp', 'Product', 'Price', 'Website'])
                    # Infer website name for the CSV
                    site_name = "Amazon" if "amazon" in url else "Flipkart"
                    writer.writerow([current_time, name, current_price, site_name])
                    print(f"✅ Saved data for {name}")

                # Check Target
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

# --- MAIN LOOP ---
print("--- Starting Mall Check ---")
for item in products:
    check_price(item)
    print("-" * 30)
