import requests
from bs4 import BeautifulSoup
import smtplib 
import os 
import datetime 
import csv      

# --- CLOUD CONFIGURATION ---
MY_EMAIL = os.environ.get("MY_EMAIL") 
MY_PASSWORD = os.environ.get("MY_PASSWORD")
DESTINATION_EMAIL = os.environ.get("DESTINATION_EMAIL")

# --- THE TRACKING LIST (Top 2 Contenders) ---
products = [
    # 🥇 TARGET 1: Acer Predator Helios Neo 16 (i9 / RTX 4070)
    { 
        "name": "Acer Predator Helios Neo 16 (Amazon)", 
        "url": "https://www.amazon.in/dp/B0CX8WZYC3", 
        "target_price": 155000 
    },

    # 🥈 TARGET 2: Lenovo Legion Pro 5i (i7-14650HX / RTX 4070)
    # ✅ UPDATED WITH YOUR NEW LINK
    { 
        "name": "Lenovo Legion Pro 5i (Amazon)", 
        "url": "https://www.amazon.in/dp/B0CX8CYXZ2", 
        "target_price": 165000 
    }
]

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
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
    print(f"🔎 Checking {product['name']}...")
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
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
                            writer.writerow(['Timestamp', 'Product', 'Price', 'Website'])
                    writer.writerow([current_time, product['name'], current_price, "Amazon"])
                    print(f"✅ Saved data for {product['name']}")

                # Alert Logic
                if current_price < product['target_price']:
                    print("🚨 Target Met!")
                    if MY_EMAIL and MY_PASSWORD:
                        send_alert(product['name'], current_price, url)
                else:
                    print("Price is still high.")
            else:
                print(f"⚠️ Could not find price for {product['name']}")
        else:
            print(f"❌ Status Code {response.status_code} for {product['name']}")
            
    except Exception as e:
        print(f"🚫 Error checking {product['name']}: {e}")

print("--- Starting Stable Cloud Check ---")
for item in products:
    check_price(item)
    print("-" * 30)
