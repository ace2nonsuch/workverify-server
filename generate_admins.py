import pandas as pd
import hashlib
import json
import random
import os

# ─────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────
INPUT_FILE = "facilities.csv"
OUTPUT_JSON = "admins.json"
OUTPUT_CSV = "admin_pins_KEEP_SAFE.csv"

LGA_COL = "lga_name"
WARD_COL = "ward_name"
FACILITY_COL = "facility_name"
# ─────────────────────────────────────────

def generate_pin():
    return str(random.randint(100000, 999999))

def generate_admin_id(index):
    return f"ADM{str(index + 1).zfill(3)}"

def generate_short_code(lga, ward, facility):
    """
    Creates a code: LGA-WAR-FAC (First 3 letters, Uppercase)
    Example: Abeokuta North, Ward 1, PHC Sabo -> ABE-WAR-PHC
    """
    lga_part = str(lga)[:3].upper()
    ward_part = str(ward)[:3].upper()
    fac_part = str(facility)[:3].upper()
    
    return f"{lga_part}-{ward_part}-{fac_part}"

def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

def load_facilities(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".csv":
        return pd.read_csv(filepath)
    elif ext in [".xlsx", ".xls"]:
        return pd.read_excel(filepath)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def main():
    print(f"Loading facilities from {INPUT_FILE}...")
    df = load_facilities(INPUT_FILE)

    required_cols = [LGA_COL, WARD_COL, FACILITY_COL]
    df = df.dropna(subset=required_cols)

    records = []
    plain_records = []
    used_pins = set()

    for index, row in df.iterrows():
        lga = str(row[LGA_COL]).strip()
        ward = str(row[WARD_COL]).strip()
        fac = str(row[FACILITY_COL]).strip()

        # 1. Generate the 3-3-3 Short Code
        admin_name = generate_short_code(lga, ward, fac)
        
        # 2. Handle unique PINs
        pin = generate_pin()
        while pin in used_pins:
            pin = generate_pin()
        used_pins.add(pin)

        admin_id = generate_admin_id(index)
        pin_hash = hash_pin(pin)

        # 3. JSON format for Server
        records.append({
            "id": admin_id,
            "name": admin_name, # The short code (e.g. ABE-WAR-PHC)
            "full_facility": fac,
            "pin_hash": pin_hash
        })

        # 4. CSV format for your records
        plain_records.append({
            "admin_id": admin_id,
            "short_code": admin_name,
            "lga": lga,
            "ward": ward,
            "facility": fac,
            "pin": pin
        })

        print(f" {admin_id} | {admin_name} | PIN: {pin}")

    with open(OUTPUT_JSON, "w") as f:
        json.dump(records, f, indent=4)
    
    pd.DataFrame(plain_records).to_csv(OUTPUT_CSV, index=False)
    print(f"\n✅ Created {len(records)} admin records.")
    print(f"✅ Upload {OUTPUT_JSON} to GitHub.")

if __name__ == "__main__":
    main()