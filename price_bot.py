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

# --- THE SHOPPING MALL (Product List) ---
# Add as many items as you want here!
products = [
    {
        "name": "MacBook Air M4",
        "url":"https://www.amazon.in/dp/B0DZDDK21R",
        "target_price": 100000
    },
    {
        "name": "Lenovo Legion Pro 5i (Core i7 / RTX 4070)", 
        # SEARCH LINK: https://www.amazon.in/s?k=Lenovo+Legion+Pro+5i
        "url": "https://www.amazon.in/dp/B0CX8WZYC3", 
        "target_price": 140000 # Good deal price for RTX 4070 models
    },
    {
        "name": "ASUS ROG Zephyrus G14 (Ryzen 9 / RTX 4060)", 
        # SEARCH LINK: https://www.amazon.in/s?k=ASUS+ROG+Zephyrus+G14
        "url": "https://www.amazon.in/dp/B09T9CQ5DR", 
        "target_price": 150000 # Rare, but a great target
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

def check_price(product):
    url = product["url"]
    target_price = product["target_price"]
    name = product["name"]

    if "PASTE" in url:
        print(f"⚠️ Skipping {name}: No URL provided yet.")
        return

    print(f"🔎 Checking {name}...")
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Scoped Search
            price_container = soup.find(id="corePriceDisplay_desktop_feature_div")
            
            if price_container:
                all_prices = price_container.find_all(class_="a-price-whole")
                extracted_prices = []
                
                for p in all_prices:
                    text = p.get_text().strip().replace(",", "").replace(".", "")
                    if text.isdigit():
                        price_val = int(text)
                        if price_val > 1000: # Filter small junk values
                            extracted_prices.append(price_val)
                
                if extracted_prices:
                    current_price = min(extracted_prices) 
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"💰 {name}: Rs. {current_price}")
                    
                    # Save to CSV
                    file_path = 'price_history.csv'
                    is_new_file = not os.path.exists(file_path)
                    
                    with open(file_path, mode='a', newline='') as file:
                        writer = csv.writer(file)
                        if is_new_file:
                             writer.writerow(['Timestamp', 'Product', 'Price'])
                        writer.writerow([current_time, name, current_price])
                        print(f"✅ Saved data for {name}")

                    # Check Target
                    if current_price < target_price:
                        print("🚨 Target Met!")
                        if MY_EMAIL and MY_PASSWORD:
                            send_alert(name, current_price, url)
                    else:
                        print("Price is still high.")
                else:
                    print(f"⚠️ Could not find valid price for {name}")
            else:
                print(f"⚠️ Price container not found for {name}")
        else:
            print(f"❌ Status Code {response.status_code} for {name}")
            
    except Exception as e:
        print(f"🚫 Error checking {name}: {e}")

# --- MAIN LOOP ---
print("--- Starting Mall Check ---")
for item in products:
    check_price(item)
    print("-" * 30) # Separator line
