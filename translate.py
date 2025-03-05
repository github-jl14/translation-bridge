import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup  # Import BeautifulSoup

# Hardcoded preferred languages
PREFERRED_LANGUAGES = {
    "EN", "DE", "ZH", "JA", "ES", "FR", "RU", "IT", "PT", "PL", "ID", "NL",
    "TR", "UK", "KO", "CS", "HU", "AR", "RO", "SV", "SK", "FI", "DA", "EL",
    "LT", "BG", "NB", "SL", "ET", "LV"
}

# Define target language (change as needed)
TARGET_LANGUAGE = "EN"  # English

chrome_options = Options()
chrome_options.binary_location = "/usr/bin/chromium-browser"  # Use Chromium instead of Chrome
chrome_options.add_argument("--headless")  # Run without UI
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service("/usr/bin/chromedriver")  # Point to the correct ChromeDriver
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open DeepL
driver.get("https://www.deepl.com/en/translate")
time.sleep(3)  # Wait for page to load

# Modify local storage to set the target language
driver.execute_script(f'localStorage.setItem("LMT_selectedTargetLanguage", "{TARGET_LANGUAGE}");')
time.sleep(1)  # Ensure change takes effect

# Read LRC file from the same directory
lrc_filename = "sample.lrc"  # Modify this if needed
with open(lrc_filename, "r", encoding="utf-8") as file:
    input_text = file.read().strip()

# Find input box and paste text
input_box = driver.find_element(By.CSS_SELECTOR, 'div[contenteditable="true"]')
input_box.click()
input_box.send_keys(Keys.CONTROL + "a")  # Select all
input_box.send_keys(Keys.BACKSPACE)  # Clear
input_box.send_keys(input_text)  # Paste

# Wait for translation to process
time.sleep(5)

# Get the page source and parse with BeautifulSoup
soup = BeautifulSoup(driver.page_source, "html.parser")

# Detect source language
detected_lang_tag = soup.select_one('[data-testid="translator-source-lang"]')
detected_lang = detected_lang_tag.get_text(strip=True) if detected_lang_tag else "unknown"

# Map DeepL's displayed language names to standard codes
DEEPL_LANG_MAP = {
    "English": "EN", "Filipino": "TL", "Tagalog": "TL", "French": "FR",
    "Spanish": "ES", "German": "DE", "Japanese": "JA", "Chinese": "ZH",
}
detected_lang_code = DEEPL_LANG_MAP.get(detected_lang, detected_lang)

# Check if the detected language is supported
if detected_lang_code not in PREFERRED_LANGUAGES:
    print(f"Error: Language '{detected_lang_code}' is unsupported!")
else:
    # Extract translated text using BeautifulSoup
    translated_div = soup.select_one('div[contenteditable="false"][role="textbox"]')
    if translated_div:
        translated_text = "\n".join([p.get_text() for p in translated_div.find_all("p")])
        print("\nTranslated Text:\n", translated_text)
    else:
        print("Error: Output div not found.")

# Close browser
driver.quit()