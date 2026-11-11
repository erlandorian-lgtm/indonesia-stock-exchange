import requests
import xml.etree.ElementTree as ET
from pathlib import Path

# Configuration for XML Type
url = "https://www.bi.go.id/biwebservice/wskursbi.asmx/getSubKursJisdor3"
params = {"mts":"USD",
          "startDate" : "2024-10-20",
          "endDate" : "2026-10-22"
}
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/149.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.bi.go.id/",
    "Accept": "application/xml, text/xml, */*",
}

# URL Response Check
def response_check(response):
    response.raise_for_status()
    try:
        root = ET.fromstring(response.text)
        return root
    except ET.ParseError as xml_err:
        print(f"Failed to decode XML response: {xml_err}")
        raise RuntimeError("Bank Indonesia API returned an invalid XML response") from xml_err

# Processing and Checking the URL 
response = requests.get(url, 
                        params=params, 
                        timeout=30,
                        headers=headers)
print("Request URL:", response.url)
data = response_check(response)

# Exporting Data into XML File
output_path = Path("data/raw/bi/bi_raw.xml")
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    f.write(response.text)