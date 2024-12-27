#!/usr/bin/python

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import hashlib


NEWS_PATH = "./news/nepalpolice.gov.np/"
ALL_NEWS_FILE = NEWS_PATH + "all.json"

def retry_request_with_backoff(resource_url, max_retries=100, retry_delay=1):
    for attempt in range(1, max_retries + 1):
        try:
            url_response = requests.get(resource_url, timeout=120)
            url_response.raise_for_status()
            return url_response
        except requests.exceptions.RequestException as e:
            print(f"Request to {resource_url} failed x{attempt}. Error: {str(e)}")
            if attempt < max_retries:
                print("Retrying...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Request failed.")
                raise


def extract_data(selector):
    url = "https://www.nepalpolice.gov.np/news/latest-news/"
    response = retry_request_with_backoff(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        data = []

        news_elements = soup.select(selector)
        for element in news_elements:
            anchor = element.select_one("a")
            if(anchor == None):
                continue

            title = anchor.select_one("h6").text.strip()
            time = anchor.select_one("span").text.strip()
            content = anchor.select_one("p").text.strip()
            link = anchor['href']

            news_item = {
                "title": title,
                "time": time,
                "content": content,
                "link": "https://www.nepalpolice.gov.np/" + link.strip("/")
            }
            data.append(news_item)

        return data
    else:
        return []


selector1 = ".row.mt-2 > div > div"
selector2 = ".row.mt-5 > .col-lg-6.order-2.order-lg-1 > div"

latest_news = extract_data(selector1)
other_news = extract_data(selector2)
all_news = latest_news + other_news
for news in all_news:
    news_hash = hashlib.sha256(json.dumps(news, sort_keys=True).encode()).hexdigest()
    news["signature"] = news_hash

try:
    with open(ALL_NEWS_FILE, "r", encoding="utf-8") as json_file:
        existing_data = json.load(json_file)
except FileNotFoundError:
    existing_data = []

with open(ALL_NEWS_FILE, "w", encoding="utf-8") as json_file:
    json.dump(all_news, json_file, ensure_ascii=False, indent=4)

current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"{NEWS_PATH}{current_datetime}.json"

new_news = [news for news in all_news if news["signature"] not in [existing_news["signature"] for existing_news in existing_data]]
with open(filename, "w", encoding="utf-8") as json_file:
    json.dump(new_news, json_file, ensure_ascii=False, indent=4)