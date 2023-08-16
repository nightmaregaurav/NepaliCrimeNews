#!/usr/bin/python

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime


def extract_data(selector):
    url = "https://www.nepalpolice.gov.np/news/latest-news/"
    response = requests.get(url)
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

if __name__ == "__main__":
    selector1 = ".row.mt-2 > div > div"
    selector2 = ".row.mt-5 > .col-lg-6.order-2.order-lg-1 > div"

    data_selector1 = extract_data(selector1)
    data_selector2 = extract_data(selector2)

    all_data = data_selector1 + data_selector2

    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"nepalpolice_gov_np_latest-news_{current_datetime}.json"

    with open(filename, "w", encoding="utf-8") as json_file:
        json.dump(all_data, json_file, ensure_ascii=False, indent=4)
