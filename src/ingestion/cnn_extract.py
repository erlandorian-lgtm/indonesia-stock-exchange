import requests
import xml.etree.ElementTree as ET
from pathlib import Path

# URL Response Check
def response_check(response):
    response.raise_for_status()
    try:
        return ET.fromstring(response.text)
    except ET.ParseError as xml_err:
        raise RuntimeError(
            "CNN Indonesia RSS feed returned invalid XML"
        ) from xml_err

def main():
    # Configuration for XML Type 
    url = "https://www.cnnindonesia.com/ekonomi/rss"

    headers = {
        "User-Agent": "indonesia-stock-exchange-student-project (contact: erlando.rian@gmail.com)",
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
    }
    response = requests.get(
        url, 
        timeout=30,
        headers=headers)
    
    response_check(response)

    # Exporting Data into XML File
    output_path = Path("data/raw/cnn/cnn_raw.xml")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(response.text, encoding="utf-8")

    print("CNN RSS extraction completed")

if __name__ == "__main__":
    main()