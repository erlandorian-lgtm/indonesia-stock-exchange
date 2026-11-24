import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from scripts.saveandload import load_json_list, save_json

# Preparing Which Elements in XML to save into Json
def parse_items(root, existing_list):
    new_bi = []
    skipped_count = 0
    for item in root.findall(".//Table"):
        bi_list = {
            "Tanggal" : item.findtext("tgl_subkursasing", default="").strip(),
            "Mata Uang" : item.findtext("mts_subkursasing", default="").strip(),
            "Nilai Beli" : item.findtext("beli_subkursasing", default="").strip(),
            "Nilai Jual" : item.findtext("jual_subkursasing", default="").strip()
        }
        bi_key = (bi_list["Tanggal"], bi_list["Mata Uang"])
        if bi_key not in existing_list:
            new_bi.append(bi_list)
            existing_list.add(bi_key)
        else:
            skipped_count += 1
    print(f"Skipped {skipped_count} existing BI Record's")
    return new_bi

# Checking NULL Data
def cleaning_bi_records(bi_records):
    cleaned, rejected = [], []
    ingested_at = datetime.now(timezone.utc).isoformat()
    for record in bi_records:
        required_fields = ["Tanggal", "Mata Uang", "Nilai Beli", "Nilai Jual"]
        if not all(record[field] for field in required_fields):
            record["rejected_at_utc"] = datetime.now(timezone.utc).isoformat()
            record["reason"] = "missing required field"
            rejected.append(record)
            continue
        try:
            parsed = datetime.strptime(record["Tanggal"],"%Y-%m-%dT%H:%M:%S%z")
            record["rate_date"] = parsed.strftime("%Y-%m-%d")                    # hint 1
            record["Nilai Beli"] = float(record["Nilai Beli"])
            record["Nilai Jual"] = float(record["Nilai Jual"])
            if record["Nilai Beli"] <= 0 or record["Nilai Jual"] <= 0:                                       # hint 2
                raise ValueError("non-positive rate")
            record["ingested_at_utc"] = ingested_at
            cleaned.append(record)
        except ValueError as e:
            record["rejected_at_utc"] = datetime.now(timezone.utc).isoformat()
            record["reason"] = f"invalid BI record: {e}"
            rejected.append(record)
    return cleaned, rejected

def main(source):
    raw_data = Path(f"data/raw/{source}/{source}_raw.xml")
    output_path = Path(f"data/processed/{source}_processed.json")
    rejected_path = Path(f"data/processed/{source}_rejected.json")
    root = ET.parse(raw_data).getroot()
    print(sorted({i.findtext("mts_subkursasing") for i in root.findall(".//Table")}))  

    existing = load_json_list(output_path)
    existing_rejected = load_json_list(rejected_path)
    existing_keys = { (record["Tanggal"], record["Mata Uang"]) for record in existing}
    new = parse_items(root, existing_keys)
    cleaned, rejected = cleaning_bi_records(new)
    save_json(existing + cleaned, output_path)
    save_json(existing_rejected + rejected, rejected_path)

if __name__ == "__main__":
    main("bi")