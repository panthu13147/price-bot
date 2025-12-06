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
    """
    Robust logic: Tries multiple CSS selectors to find the price.
    """
    # LIST OF PLACES TO LOOK FOR PRICE
    selectors = [
        {"id": "corePriceDisplay_desktop_feature_div"}, # Standard Desktop
        {"id": "corePrice_feature_div"},                # Alternative Desktop
        {"id": "apex_desktop"},                         # Old Layout
        {"class_": "a-section a-spacing-none aok-align-center"}, # Generic container
        {"id": "price"}                                  # Mobile/Lite layout
    ]

    for sel in selectors:
        container = soup.find(**sel)
        if container:
            # Look for the whole number price class
            price_element = container.find(class_="a-price-whole")
            if price_element:
                text = price_element.get_text().strip().replace(",", "").replace(".", "")
                if text.isdigit():
                    return int(text)
    return None

def check_price(product):
    url = product["url"]
    print(f"🔎 Checking {product['name']}...")
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # --- DEBUG: CHECK WHAT PAGE WE ACTUALLY GOT ---
            page_title = soup.title.string.strip() if soup.title else "No Title"
            if "Robot Check" in page_title or "Captcha" in page_title:
                print(f"⚠️ AMAZON BLOCKED US (CAPTCHA PAGE) for {product['name']}")
                return
            # -----------------------------------------------

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
                print(f"⚠️ Could not find price. Page Title was: '{page_title}'")
        else:
            print(f"❌ Status Code {response.status_code} for {product['name']}")
            
    except Exception as e:
        print(f"🚫 Error checking {product['name']}: {e}")
