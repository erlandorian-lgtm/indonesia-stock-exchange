import requests
import xml.etree.ElementTree as ET
from pathlib import Path

# Configuration for XML Type 
url = "https://www.cnnindonesia.com/ekonomi/rss"
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

# URL Response Check
def response_check(response):
    response.raise_for_status()
    try:
        root = ET.fromstring(response.text)
        return root
    except ET.ParseError as xml_err:
        print(f"Failed to decode XML response: {xml_err}")
        raise RuntimeError("CNN Indonesia RSS feed returned invalid XML") from xml_err
    
response = requests.get(url, 
                        timeout=30,
                        headers=headers)
print("Status code:", response.status_code)
print("Content-Type:", response.headers.get("Content-Type"))
print("Response preview:", response.text[:500])
data = response_check(response)

# Exporting Data into XML File
output_path = Path("data/raw/cnn/cnn_raw.xml")
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    f.write(response.text)