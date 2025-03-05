from urllib.parse import quote
from langdetect import detect
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import re

lrc_path = "sample.lrc"

with open(lrc_path, "r", encoding="utf-8") as lyrics:
    INPUT = lyrics.read()

SOURCE = detect(INPUT)
TARGET = "en-us"

BASE_URL = f"https://www.deepl.com/en/translator#{SOURCE}/{TARGET}/"
CLEAN_INPUT = quote(INPUT)
FINAL_URL = f"{BASE_URL}{CLEAN_INPUT}%0A"

session = HTMLSession()
response = session.get(FINAL_URL)
response.html.render(sleep=5)

soup = BeautifulSoup(response.html.html, 'html.parser')

target_textarea = soup.find("d-textarea", {"name": "target"})

if target_textarea:
    translated_text = target_textarea.text.strip()
    translated_lines = translated_text.split('\n')

    processed_lines = []
    for line in translated_lines:
        seen = set()
        result = []
        parts = re.split(r'(\[[^\]]+\])', line)
        for part in parts:
            if part.startswith('[') and part.endswith(']'):
                if part not in seen:
                    result.append(part)
                    seen.add(part)
            else:
                result.append(part)
        processed_lines.append(''.join(result))

    final_translated_text = '\n'.join(processed_lines)

    with open("result.lrc", "w", encoding="utf-8") as result_file:
        result_file.write(final_translated_text)
    print("Translation and duplicate removal complete. Results saved to result.lrc")
else:
    print("Translation not found.")
