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
    "Refer
