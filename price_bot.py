import requests
from bs4 import BeautifulSoup
import smtplib
import os

# --- CLOUD CONFIGURATION ---
MY_EMAIL = os.environ.get("MY_EMAIL")
MY_PASSWORD = os.environ.get("MY_PASSWORD")
DESTINATION_EMAIL = os.environ.get("DESTINATION_EMAIL")

# 1. The Target
url = 'https://www.amazon.in/Apple-MacBook-13-inch-10-core-Unified/dp/B0DZDDKTQZ'

# UPDATED HEADERS (Newer "Disguise" to trick Amazon)
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "https://www.google.com/"
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
print(f"Status Code: {response.status_code}") # <--- DEBUG 1

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # DEBUG 2: Print the Page Title (This tells us if it's a Captcha!)
    page_title = soup.title.string.strip() if soup.title else "No Title Found"
    print(f"Page Title: {page_title}")
    
    price_element = soup.find(class_="a-price-whole")
    
    if price_element:
        clean_price = int(price_element.get_text().strip().replace(",", "").replace(".", ""))
        print(f"Current Price: {clean_price}")
        
        target_price = 115000 
        
        if clean_price < target_price:
            print("Target Met! Triggering Alert...")
            if MY_EMAIL and MY_PASSWORD:
                send_alert(clean_price)
            else:
                print("⚠️ Alert triggered, but no credentials found in secrets.")
        else:
            print("Price is still high.")
    else:
        # <--- THIS IS THE MISSING PIECE
        print("⚠️ Price tag not found! Amazon might have given us a CAPTCHA page.")
        # Optional: Print a bit of the HTML to see what's wrong
        print("First 500 chars of page:", soup.prettify()[:500])
else:
    print("Failed to connect to Amazon.")
