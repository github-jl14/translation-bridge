import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# Hardcoded preferred languages
PREFERRED_LANGUAGES = {
    "EN", "DE", "ZH", "JA", "ES", "FR", "RU", "IT", "PT", "PL", "ID", "NL",
    "TR", "UK", "KO", "CS", "HU", "AR", "RO", "SV", "SK", "FI", "DA", "EL",
    "LT", "BG", "NB", "SL", "ET", "LV"
}

# Define target language (change as needed)
TARGET_LANGUAGE = "EN"  # English

# Setup Selenium with headless mode
options = Options()
options.add_argument("--headless")  # Runs without opening a browser window
driver = webdriver.Chrome(options=options)

# Open DeepL
driver.get("https://www.deepl.com/en/translate")

# Wait for DeepL to load
time.sleep(3)

# Modify local storage to set the target language
driver.execute_script(f'localStorage.setItem("LMT_selectedTargetLanguage", "{TARGET_LANGUAGE}");')
time.sleep(1)  # Ensure change takes effect

# Read LRC file from the same directory
lrc_filename = "sample.lrc"  # Modify this if needed
with open(lrc_filename, "r", encoding="utf-8") as file:
    input_text = file.read().strip()
    file.close()

# Find input box and paste text
input_box = driver.find_element(By.CSS_SELECTOR, 'div[contenteditable="true"]')
input_box.click()
input_box.send_keys(Keys.CONTROL + "a")  # Select all
input_box.send_keys(Keys.BACKSPACE)  # Clear
input_box.send_keys(input_text)  # Paste

# Wait for translation to process
time.sleep(5)

# Detect the source language from the DeepL UI
detected_lang = driver.execute_script("""
    let langTag = document.querySelector('[data-testid="translator-source-lang"]');
    return langTag ? langTag.innerText.trim() : "unknown";
""")

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
    # Extract translated text
    translated_text = driver.execute_script("""
        let outputDiv = document.querySelector('div[contenteditable="false"][role="textbox"]');
        if (!outputDiv) return 'Error: Output div not found.';
        return Array.from(outputDiv.querySelectorAll('p')).map(p => p.innerText).join('\\n');
    """)

    print("\nTranslated Text:\n", translated_text)

# Close browser
driver.quit()
