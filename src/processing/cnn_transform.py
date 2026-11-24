import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from scripts.saveandload import load_json_list, save_json
from email.utils import parsedate_to_datetime

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
        required_fields = ["title", "link", "pubDate", "guid"]
        
        if not all(article[field] for field in required_fields):
            article["rejected_at_utc"] = datetime.now(timezone.utc).isoformat()
            article["reason"] = "missing required field"
            rejected_articles.append(article)
            continue
        try:
            parsed_date = parsedate_to_datetime(article["pubDate"])

            if parsed_date is None:
                raise ValueError("invalid publication date")

            utc = parsed_date.astimezone(timezone.utc)

            article["published_utc"] = utc.isoformat()
            article["ingested_at_utc"] = ingested_at
            cleaned_articles.append(article)

        except (ValueError, TypeError, OverflowError) as e:
            article["rejected_at_utc"] = datetime.now(timezone.utc).isoformat()
            article["reason"] = f"invalid publication date: {e}"
            rejected_articles.append(article)

    return cleaned_articles, rejected_articles


def main(source):
    raw_data = Path(f"data/raw/{source}/{source}_raw.xml")
    output_path = Path(f"data/processed/{source}_articles.json")
    rejected_path = Path(f"data/processed/{source}_rejected.json")
    tree = ET.parse(raw_data)
    channel = tree.getroot().find("channel")
    if channel is None:
        raise ValueError("RSS channel not found")
    existing = load_json_list(output_path)
    existing_rejected = load_json_list(rejected_path)
    guids = set(article["guid"] for article in existing)
    new = parse_items(channel, guids)
    cleaned, rejected = cleaning_articles(new)
    save_json(existing + cleaned, output_path)
    save_json(existing_rejected + rejected, rejected_path)

if __name__ == "__main__":
    main("cnn")