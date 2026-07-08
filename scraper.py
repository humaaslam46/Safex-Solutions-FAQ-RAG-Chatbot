import os
import requests
from bs4 import BeautifulSoup

# List of URLs
urls = {
    "home": "https://safexsolutions.com/",
    "about": "https://safexsolutions.com/about",
    "services": "https://safexsolutions.com/services",
    "contact": "https://safexsolutions.com/contact",
    "trust_mission": "https://trust.safexsolutions.com/our-mission",
    "trust_programs": "https://trust.safexsolutions.com/programs---causes",
    "trust_events": "https://trust.safexsolutions.com/events",
    "trust_blog": "https://trust.safexsolutions.com/blog",
    "blog": "https://safexsolutions.com/blog"
}

# Create data folder if it doesn't exist
os.makedirs("data", exist_ok=True)

for filename, url in urls.items():
    print(f"Scraping: {url}")

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        text = soup.get_text(separator="\n")

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = "\n".join(lines)

        with open(f"data/{filename}.txt", "w", encoding="utf-8") as file:
            file.write(clean_text)

        print(f"✅ Saved: {filename}.txt")

    else:
        print(f"❌ Failed: {url}")