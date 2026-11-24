import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import date, timedelta

# URL Response Check
def response_check(response):
    response.raise_for_status()
    try:
        return ET.fromstring(response.text)
    except ET.ParseError as xml_err:
        raise RuntimeError(
            "Bank Indonesia API returned an invalid XML response"
        ) from xml_err

def main():
    # Configuration for XML Type
    url = "https://www.bi.go.id/biwebservice/wskursbi.asmx/getSubKursJisdor3"
    
    params = {
        "mts":"USD",
        "startDate" : "2024-10-20",
        "endDate" : (date.today() + timedelta(days=1)).isoformat()
    }

    headers = {
        "User-Agent": "indonesia-stock-exchange-student-project (contact: erlando.rian@gmail.com)",
        "Referer": "https://www.bi.go.id/",
        "Accept": "application/rss+xml, application/xml, text/xml, */*"
    }

    # Processing and Checking the URL 
    response = requests.get(
        url, 
        params=params, 
        timeout=30,
        headers=headers)
    
    response_check(response)

    # Exporting Data into XML File
    output_path = Path("data/raw/bi/bi_raw.xml")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(response.text, encoding="utf-8")

    print("BI XML extraction completed")

if __name__ == "__main__":
    main()