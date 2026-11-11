import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from scripts.saveandload import load_json_list, save_json

rejected_output_path = Path("data/processed/cnn_rejected.json")
output_path = Path("data/processed/cnn_articles.json")
load_articles_path = Path("data/processed/cnn_articles.json")
raw_data = Path("data/raw/cnn/cnn_raw.xml") 

# Preparing Which Elements in XML to save into Json
def parse_items(channel, existing_guids):
    new_articles = []
    skipped_count = 0
    for item in channel.findall("item"):
        article = {
            "title" : item.findtext("title", default="").strip(),
            "link" : item.findtext("link", default="").strip(),
            "pubDate" : item.findtext("pubDate", default="").strip(),
            "guid" : item.findtext("guid", default="").strip()
        }
        if article["guid"] not in existing_guids:
            new_articles.append(article)
            existing_guids.add(article["guid"])
        else:
            skipped_count += 1
    if skipped_count > 0:
        print(f"Skipped {skipped_count} existing Guid's")

    print("Total articles:", len(new_articles))
    if len(new_articles) > 0:
        print("First article:", new_articles[0])
    else:
        print("No new articles were found.")
    return new_articles

# Checking NULL Data
def cleaning_articles(new_articles):
    cleaned_articles = []
    rejected_articles = []
    ingested_at = datetime.now(timezone.utc).isoformat()
    for article in new_articles:
        if not article["title"] or not article["link"] or not article["pubDate"] or not article["guid"]:
            rejected_articles.append(article)
        else:
            try:
                date_string = article["pubDate"]
                parsed_date = datetime.strptime(
                date_string,"%a, %d %b %Y %H:%M:%S %z")
                utc = parsed_date.astimezone(timezone.utc)
                article["published_utc"] = utc.isoformat()
                article["ingested_at_utc"] = ingested_at
                cleaned_articles.append(article)
            except ValueError:
                rejected_articles.append(article)

    return cleaned_articles, rejected_articles

def main():
    tree = ET.parse(raw_data)
    channel = tree.getroot().find("channel")
    existing = load_json_list(load_articles_path)
    guids = set(article["guid"] for article in existing)
    new = parse_items(channel, guids)
    cleaned, rejected = cleaning_articles(new)
    save_json(existing + cleaned, output_path)
    save_json(rejected, rejected_output_path)

if __name__ == "__main__":
    main()