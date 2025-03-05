import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import sys

# ANSI Color Codes
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"

# Hardcoded preferred languages
PREFERRED_LANGUAGES = {
    "EN", "DE", "ZH", "JA", "ES", "FR", "RU", "IT", "PT", "PL", "ID", "NL",
    "TR", "UK", "KO", "CS", "HU", "AR", "RO", "SV", "SK", "FI", "DA", "EL",
    "LT", "BG", "NB", "SL", "ET", "LV"
}

# Define target language
TARGET_LANGUAGE = "EN"  # English

# Chrome options
chrome_options = Options()
chrome_options.binary_location = "/usr/bin/chromium-browser"
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service("/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

print(f"{BLUE}[INFO]{RESET} Opening DeepL website...")
driver.get("https://www.deepl.com/en/translate")
time.sleep(3)

# Modify local storage to set the target language
print(f"{BLUE}[INFO]{RESET} Setting target language to {TARGET_LANGUAGE}...")
driver.execute_script(f'localStorage.setItem("LMT_selectedTargetLanguage", "{TARGET_LANGUAGE}");')
time.sleep(1)

# Read LRC file
lrc_filename = "sample.lrc"
try:
    with open(lrc_filename, "r", encoding="utf-8") as file:
        input_text = file.read().strip()
        print(f"{GREEN}[SUCCESS]{RESET} Read input file '{lrc_filename}' successfully.")
except Exception as e:
    print(f"{RED}[ERROR]{RESET} Failed to read '{lrc_filename}': {e}")
    driver.quit()
    sys.exit(1)

# Find input box
try:
    input_box = driver.find_element(By.CSS_SELECTOR, 'div[contenteditable="true"]')
    print(f"{GREEN}[SUCCESS]{RESET} Found input box.")
except Exception as e:
    print(f"{RED}[ERROR]{RESET} Could not find input box: {e}")
    driver.quit()
    sys.exit(2)

# Paste text
print(f"{BLUE}[INFO]{RESET} Pasting text into DeepL...")
input_box.click()
input_box.send_keys(Keys.CONTROL + "a")
input_box.send_keys(Keys.BACKSPACE)
input_box.send_keys(input_text)
time.sleep(5)

# Get the page source and parse with BeautifulSoup
print(f"{BLUE}[INFO]{RESET} Parsing page source...")
soup = BeautifulSoup(driver.page_source, "html.parser")

# Detect source language
detected_lang_tag = soup.select_one('[data-testid="translator-source-lang"]')
detected_lang = detected_lang_tag.get_text(strip=True) if detected_lang_tag else "unknown"
print(f"{YELLOW}[DEBUG]{RESET} Detected source language: {detected_lang}")

# Map DeepL's displayed language names to standard codes
DEEPL_LANG_MAP = {
    "English": "EN", "Filipino": "TL", "Tagalog": "TL", "French": "FR",
    "Spanish": "ES", "German": "DE", "Japanese": "JA", "Chinese": "ZH",
}
detected_lang_code = DEEPL_LANG_MAP.get(detected_lang, detected_lang)

# Check if the detected language is supported
if detected_lang_code not in PREFERRED_LANGUAGES:
    print(f"{RED}[ERROR]{RESET} Language '{detected_lang_code}' is unsupported!")
    driver.quit()
    sys.exit(3)

# Extract translated text using BeautifulSoup
translated_div = soup.select_one('div[contenteditable="false"][role="textbox"]')
if translated_div:
    translated_text = "\n".join([p.get_text() for p in translated_div.find_all("p")])
    print(f"\n{GREEN}[SUCCESS]{RESET} Translated Text:\n{BOLD}{translated_text}{RESET}")
else:
    print(f"{RED}[ERROR]{RESET} Output div not found.")
    driver.quit()
    sys.exit(4)

# Save the raw page source for debugging
with open("debug_page.html", "w", encoding="utf-8") as debug_file:
    debug_file.write(driver.page_source)
    print(f"{YELLOW}[DEBUG]{RESET} Saved page source to 'debug_page.html' for inspection.")

# Close browser
print(f"{BLUE}[INFO]{RESET} Closing browser...")
driver.quit()
sys.exit(0)