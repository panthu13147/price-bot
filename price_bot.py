import requests
from bs4 import BeautifulSoup
import smtplib 
import os 
import datetime # For timestamp
import csv      # For file saving

# --- CLOUD CONFIGURATION ---
MY_EMAIL = os.environ.get("MY_EMAIL") 
MY_PASSWORD = os.environ.get("MY_PASSWORD")
DESTINATION_EMAIL = os.environ.get("DESTINATION_EMAIL")

# 1. The Target
url = 'https://www.amazon.in/Apple-MacBook-13-inch-10-core-Unified/dp/B0DZDDKTQZ'

# UPDATED HEADERS (The "Heavy Duty" Disguise)
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "https://www.google.com/"
}

# --- ALERT FUNCTION (Restored and Complete) ---
def send_alert(price):
    print(f"📧 Sending email to {DESTINATION_EMAIL}...")
    subject = "PRICE DROP ALERT: MacBook Air M4!"
    body = f"The price dropped to Rs. {price}. Buy it here: {url}"
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

# --- MAIN LOGIC ---
print("Checking price...")
response = requests.get(url, headers=headers)
print(f"Status Code: {response.status_code}") 

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # DEBUG: Print the Page Title 
    page_title = soup.title.string.strip() if soup.title else "No Title Found"
    print(f"Page Title: {page_title}")

    # Find the main price container first (scoping the search)
    price_container = soup.find(id="corePriceDisplay_desktop_feature_div")
    
    if price_container:
        all_prices = price_container.find_all(class_="a-price-whole")
        extracted_prices = []
        
        for p in all_prices:
            text = p.get_text().strip().replace(",", "").replace(".", "")
            if text.isdigit():
                price_val = int(text)
                if price_val > 10000: 
                    extracted_prices.append(price_val)
        
        if extracted_prices:
            current_price = min(extracted_prices) 
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"📉 Lowest Price Found: {current_price}")
            print(f"⏰ Timestamp: {current_time}") 

            # --- DATA SAVING LOGIC (CLOUD FIX) ---
            file_path = 'price_history.csv'
            is_new_file = not os.path.exists(file_path) # Check if file exists
            
            with open(file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                
                # Write a header row only if the file did not exist before
                if is_new_file:
                     writer.writerow(['Timestamp', 'Price'])
                
                # Write the new data point
                writer.writerow([current_time, current_price])
                print(f"✅ Data saved to {file_path}")

            # --- TRIGGER LOGIC ---
            target_price = 110000 
            
            if current_price < target_price:
                print("Target Met! Triggering Alert...")
                if MY_EMAIL and MY_PASSWORD:
                    send_alert(current_price)
                else:
                    print("⚠️ Alert triggered, but no credentials found in secrets.")
            else:
                print(f"Price ({current_price}) is still high.")

        else:
            print("⚠️ ERROR: No valid main price found in the Buy Box.")

else:
    print("Failed to connect to Amazon.")
