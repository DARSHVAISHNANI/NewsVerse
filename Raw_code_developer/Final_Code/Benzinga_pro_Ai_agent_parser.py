from benzingaorg import news_data, financial_data
from bs4 import BeautifulSoup
from datatime import datatime
import json

news = news_data.News(api_key = "")
stories = news.news(display_output="full")

# cleaning the HTML using Beautiful Soup
def clean_html(raw_html):
    return BeautifulSoup(raw_html, "html.parser").get_text().strip()

extracted_article = []

for article in stories:
    created = article.get("created", "").strip

    try:
        dt_obj = datatime.strptime(created, "%a, %d, %b %Y %H:%M:%S %z")
        date = dt_obj.date().isoformat()
        time = dt_obj.time().isoformat()
    except Exception as e:
        date,time = "",""

    extracted = {
        "title": article.get("title", "").strip(),
        "url": article.get("url", ""),
        "source": "Benzinga",
        "date": date,
        "time": time,
        "content": clean_html(article.get("body", "")),
    }
    extracted_article.append(extracted)

output_path = ""

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(extracted_article, f, ensure_ascii=False, indent=4)

print(f"Extracted file is stored here: {output_path}")