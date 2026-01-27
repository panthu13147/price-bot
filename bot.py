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

# --- THE TRACKING LIST ---
products = [
    # 🥇 TARGET 1: Acer Predator Helios Neo 16 (i9 / RTX 4070)
    { 
        "name": "Acer Predator Helios Neo 16 (Amazon)", 
        "url": "https://www.amazon.in/dp/B0CX8WZYC3", 
        "target_price": 155000 
    },
    # 🥈 TARGET 2: Lenovo Legion 5 (Updated Link)
    { 
        "name": "Lenovo Legion 5 (Amazon)", 
        "url": "https://www.amazon.in/dp/B0FY2ZXJBT", 
        "target_price": 165000 
    }
]

# --- STEALTH HEADERS ---
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
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
    # Strategy 1: Specific Container IDs (High Accuracy)
    selectors = [
        {"id": "corePriceDisplay_desktop_feature_div"},
        {"id": "corePrice_feature_div"},
        {"id": "apex_desktop"},
        {"id": "price_inside_buybox"},
        {"class_": "a-section a-spacing-none aok-align-center"}
    ]
    for sel in selectors:
        container = soup.find(**sel)
        if container:
            price_element = container.find(class_="a-price-whole")
            if price_element:
                text = price_element.get_text().strip().replace(",", "").replace(".", "")
                if text.isdigit():
                    return int(text)

    # Strategy 2: "Center Column" Fallback (Broad Search)
    # If specific IDs fail, look for ANY price in the main product area
    center_col = soup.find(id="centerCol")
    if center_col:
        price_element = center_col.find(class_="a-price-whole")
        if price_element:
            text = price_element.get_text().strip().replace(",", "").replace(".", "")
            if text.isdigit():
                return int(text)
                
    return None

def check_price(product):
    url = product["url"]
    print(f"🔎 Checking {product['name']}...")
    
    session = requests.Session()
    
    try:
        response = session.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Anti-Redirect Logic
            page_title = soup.title.string.strip() if soup.title else "No Title"
            if page_title == "Amazon.in":
                print("   ⚠️ Redirected to Homepage. Retrying...")
                time.sleep(2)
                response = session.get(url, headers=headers)
                soup = BeautifulSoup(response.content, 'html.parser')
                page_title = soup.title.string.strip() if soup.title else "No Title"

            current_price = get_price_amazon(soup) 

            if current_price:
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"💰 {product['name']}: Rs. {current_price}")
                
                # Save to CSV
                file_path = 'price_history.csv'
                is_new_file = not os.path.exists(file_path)
                with open(file_path, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    if is_new_file:
                            writer.writerow(['Timestamp', 'Product', 'Price', 'Website', 'URL'])
                    writer.writerow([current_time, product['name'], current_price, "Amazon", url])
                    print(f"✅ Saved data for {product['name']}")

                # Alert Logic
                if current_price < product['target_price']:
                    print("🚨 Target Met!")
                    if MY_EMAIL and MY_PASSWORD:
                        send_alert(product['name'], current_price, url)
                else:
                    print("Price is still high.")
            else:
                print(f"⚠️ Could not find price. Page Title was: '{page_title}'")
        else:
            print(f"❌ Status Code {response.status_code} for {product['name']}")
            
    except Exception as e:
        print(f"🚫 Error checking {product['name']}: {e}")

# --- MAIN EXECUTION ---
print("--- Starting Stable Cloud Check ---")
for item in products:
    check_price(item)
    print("-" * 30)
