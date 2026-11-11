import json
import requests
from pathlib import Path

# Configuration
url = "https://api.gdeltproject.org/api/v2/doc/doc"
params = {"query":"Indonesia",
          "mode" : "ArtList",
          "format" : "json",
          "maxrecords" : 10,
          "timespan" : "7d"}
headers = {
    "User-Agent": "IHSGMarketEventStudy/1.0 (educational project)"
}

# URL Response Check
def response_check(response):
    response.raise_for_status()
    try:
        data = response.json()
        if isinstance(data, dict):
            return data
        else:
            raise ValueError("GDELT returned an invalid JSON response") 
    except requests.exceptions.JSONDecodeError as json_err:
        print(f"Failed to decode Json response {json_err}")
        raise ValueError("GDELT returned an invalid JSON response") from json_err

# Processing and Checking the URL 
response = requests.get(url, params=params, headers=headers, timeout=(10,60))
data = response_check(response)

print("Status code:", response.status_code)
print("Response preview:", response.text[:500])

# Exporting Data into Json File
output_path = Path("data/raw/gdelt/gdelt_raw.json")
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
