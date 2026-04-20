from flask import Flask, request, jsonify
import json
import hashlib
import os

app = Flask(__name__)

def load_admins():
    with open("admins.json", "r") as f:
        return json.load(f)

def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

@app.route("/validate-pin", methods=["POST"])
def validate_pin():
    data = request.get_json()

    if not data or "pin" not in data:
        return jsonify({"valid": False, "message": "No PIN provided"}), 400

    pin = data["pin"].strip()

    if len(pin) != 6 or not pin.isdigit():
        return jsonify({"valid": False, "message": "PIN must be 6 digits"}), 400

    hashed = hash_pin(pin)
    admins = load_admins()

    for admin in admins:
        if admin["pin_hash"] == hashed:
            return jsonify({
                "valid": True,
                "admin_name": admin["name"],
                "facility": admin["facility"],
                "admin_id": admin["id"]
            })

    return jsonify({"valid": False, "message": "Invalid PIN"})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)