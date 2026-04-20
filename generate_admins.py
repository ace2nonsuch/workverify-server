
import pandas as pd
import hashlib
import json
import random
import string
import os

# ─────────────────────────────────────────
# CONFIGURATION — change these as needed
# ─────────────────────────────────────────
INPUT_FILE = "facilities.csv"   # or "facilities.xlsx"
OUTPUT_JSON = "admins.json"
OUTPUT_CSV = "admin_pins_KEEP_SAFE.csv"  # plain text PINs — store securely
FACILITY_COLUMN = "facility_name"  # name of the column in your file
# ─────────────────────────────────────────

def generate_pin():
    """Generate a random 6-digit PIN"""
    return str(random.randint(100000, 999999))

def generate_admin_id(index):
    """Generate a unique admin ID like ADM001, ADM002..."""
    return f"ADM{str(index + 1).zfill(3)}"

def generate_admin_name(facility):
    """Derive admin name from facility name"""
    return f"Admin, {facility}"

def hash_pin(pin):
    """SHA256 hash of a PIN"""
    return hashlib.sha256(pin.encode()).hexdigest()

def load_facilities(filepath):
    """Load facilities from CSV or Excel"""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".csv":
        df = pd.read_csv(filepath)
    elif ext in [".xlsx", ".xls"]:
        df = pd.read_excel(filepath)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    return df

def main():
    # ── Step 1: Load facilities ──────────────────
    print(f"Loading facilities from {INPUT_FILE}...")
    df = load_facilities(INPUT_FILE)

    if FACILITY_COLUMN not in df.columns:
        print(f"\nERROR: Column '{FACILITY_COLUMN}' not found.")
        print(f"Available columns: {list(df.columns)}")
        return

    facilities = df[FACILITY_COLUMN].dropna().unique().tolist()
    print(f"Found {len(facilities)} facilities.")

    # ── Step 2: Generate PINs and IDs ────────────
    records = []
    plain_records = []  # for the safe-keep CSV

    used_pins = set()  # ensure no duplicate PINs

    for index, facility in enumerate(facilities):
        # Generate unique PIN
        pin = generate_pin()
        while pin in used_pins:
            pin = generate_pin()
        used_pins.add(pin)

        admin_id = generate_admin_id(index)
        pin_hash = hash_pin(pin)

        # For admins.json — no plain PIN
        admin_name = generate_admin_name(facility)
        records.append({
            "id": admin_id,
            "name": admin_name,
            "facility": facility,
            "pin_hash": pin_hash
        })

        # For the safe-keep CSV — includes plain PIN
        plain_records.append({
            "admin_id": admin_id,
            "name": admin_name,
            "facility": facility,
            "pin": pin
        })

        print(f"  {admin_id} | {facility} | PIN: {pin}")

    # ── Step 3: Save admins.json ─────────────────
    with open(OUTPUT_JSON, "w") as f:
        json.dump(records, f, indent=4)
    print(f"\n✅ Saved {OUTPUT_JSON} — upload this to your server")

    # ── Step 4: Save plain PIN CSV ───────────────
    plain_df = pd.DataFrame(plain_records)
    plain_df.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Saved {OUTPUT_CSV} — keep this file PRIVATE, share PINs with admins")

    print("\nDone!")

if __name__ == "__main__":
    main()