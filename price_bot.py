import requests
from bs4 import BeautifulSoup
import smtplib 
import os 

# --- CLOUD CONFIGURATION ---
# The bot gets these from the Github Vault (Secrets)
MY_EMAIL = os.environ.get("MY_EMAIL") 
MY_PASSWORD = os.environ.get("MY_PASSWORD")
DESTINATION_EMAIL = os.environ.get("DESTINATION_EMAIL")

# 1. The Target
url = 'https://www.amazon.in/Apple-MacBook-13-inch-10-core-Unified/dp/B0DZDDKTQZ'

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

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

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    price_element = soup.find(class_="a-price-whole")
    
    if price_element:
        clean_price = int(price_element.get_text().strip().replace(",", "").replace(".", ""))
        print(f"Current Price: {clean_price}")
        
        # Trigger Logic (Set high for testing)
        target_price = 115000 
        
        if clean_price < target_price:
            print("Target Met! Triggering Alert...")
            if MY_EMAIL and MY_PASSWORD:
                send_alert(clean_price)
            else:
                print("⚠️ Alert triggered, but no credentials found in secrets.")
        else:
            print("Price is still high.")
              
