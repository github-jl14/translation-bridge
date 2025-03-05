import time
import json
import os
import sys
from langdetect import detect
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# DeepL URL
DEEPL_URL = "https://www.deepl.com/en/translate"

# ANSI Color Dictionary
COLOR = {
    "RESET": "\033[0m",
    "BOLD": "\033[1m",
    "INFO": "\033[34m",    # Blue
    "SUCCESS": "\033[32m", # Green
    "WARNING": "\033[33m", # Yellow
    "ERROR": "\033[31m",   # Red
}

# Supported languages
PREFERRED_LANGUAGES = {
    "EN", "DE", "ZH", "JA", "ES", "FR", "RU", "IT", "PT", "PL", "ID", "NL",
    "TR", "UK", "KO", "CS", "HU", "AR", "RO", "SV", "SK", "FI", "DA", "EL",
    "LT", "BG", "NB", "SL", "ET", "LV"
}

# Read LRC file
LRC_FILE = "sample.lrc"
if not os.path.exists(LRC_FILE):
    print(f"{COLOR['ERROR']}[ERROR]{COLOR['RESET']} LRC file not found!")
    sys.exit(1)

with open(LRC_FILE, "r", encoding="utf-8") as file:
    source_text = file.read().strip()

print(f"{COLOR['INFO']}[INFO]{COLOR['RESET']} Loaded LRC file with {len(source_text.splitlines())} lines.")

# Detect language
detected_source = detect(source_text).upper()
TARGET_LANGUAGE = "EN"

print(f"{COLOR['INFO']}[INFO]{COLOR['RESET']} Detected Language: {detected_source}")

if detected_source not in PREFERRED_LANGUAGES:
    print(f"{COLOR['ERROR']}[ERROR]{COLOR['RESET']} Unsupported language detected!")
    sys.exit(1)

# Selenium Setup
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

service = Service("/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

print(f"{COLOR['INFO']}[INFO]{COLOR['RESET']} Opening DeepL website...")
driver.get(DEEPL_URL)
time.sleep(3)

# Enable DevTools Network Monitoring
driver.execute_cdp_cmd("Network.enable", {})

# Modify local storage
print(f"{COLOR['INFO']}[INFO]{COLOR['RESET']} Setting target language to {TARGET_LANGUAGE}...")
driver.execute_script(f'localStorage.setItem("LMT_selectedTargetLanguage", "{TARGET_LANGUAGE}");')
time.sleep(1)

# Find input box
try:
    input_box = driver.find_element(By.CSS_SELECTOR, 'div[contenteditable="true"]')
    print(f"{COLOR['SUCCESS']}[SUCCESS]{COLOR['RESET']} Found input box.")
except Exception as e:
    print(f"{COLOR['ERROR']}[ERROR]{COLOR['RESET']} Could not find input box: {e}")
    driver.quit()
    sys.exit(2)

# Paste text
print(f"{COLOR['INFO']}[INFO]{COLOR['RESET']} Pasting text into DeepL...")
input_box.click()
input_box.send_keys(Keys.CONTROL + "a")
input_box.send_keys(Keys.BACKSPACE)
input_box.send_keys(source_text)
time.sleep(10)  # Wait for translation to process

# Capture network logs
print(f"{COLOR['INFO']}[INFO]{COLOR['RESET']} Capturing network logs for translation requests...")

logs = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": "1"})
last_handle_jobs_request = None

for log in logs:
    if "jsonrpc?method=LMT_handle_jobs" in log["url"]:
        last_handle_jobs_request = json.loads(log["body"])
        break

if not last_handle_jobs_request:
    print(f"{COLOR['ERROR']}[ERROR]{COLOR['RESET']} Could not find 'LMT_handle_jobs' request.")
    driver.quit()
    sys.exit(3)

# Extract translated text
print(f"{COLOR['INFO']}[INFO]{COLOR['RESET']} Parsing translation response...")

if "params" in last_handle_jobs_request and "jobs" in last_handle_jobs_request["params"]:
    translated_texts = [
        job["sentences"][0]["text"]
        for job in last_handle_jobs_request["params"]["jobs"]
        if "sentences" in job and len(job["sentences"]) > 0
    ]

    if translated_texts:
        print(f"\n{COLOR['SUCCESS']}[SUCCESS]{COLOR['RESET']} Final Translated Text:\n")
        for line in translated_texts:
            print(line)
    else:
        print(f"{COLOR['WARNING']}[WARNING]{COLOR['RESET']} No translated text found!")

else:
    print(f"{COLOR['ERROR']}[ERROR]{COLOR['RESET']} Invalid response format!")

# Cleanup
driver.quit()
sys.exit(0)
