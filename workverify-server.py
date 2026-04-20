from flask import Flask, request, jsonify
import json
import os
import hashlib

app = Flask(__name__)

def load_admins():
    if os.path.exists('admins.json'):
        with open('admins.json', 'r') as f:
            return json.load(f)
    return []

@app.route('/')
def home():
    return "WorkVerify Plus Server is Running"

@app.route('/validate-pin', methods=['POST'])
def validate_pin():
    data = request.json
    entered_pin = data.get('pin', '')
    entered_name = data.get('admin_name', '').strip().lower()
    
    # Hash the PIN sent by the Android app so we can compare it to the stored hash
    entered_pin_hash = hashlib.sha256(entered_pin.encode()).hexdigest()
    
    admins = load_admins()
    
    # Your script generates a LIST of dictionaries, so we iterate through it
    for admin in admins:
        record_name = admin.get('name', '').strip().lower()
        
        # Match Name and the Hashed PIN
        if record_name == entered_name and admin.get('pin_hash') == entered_pin_hash:
            return jsonify({
                "valid": True,
                "facility": admin.get('facility'),
                "admin_id": admin.get('id')
            }), 200
            
    return jsonify({
        "valid": False, 
        "message": "Incorrect Admin Name or PIN"
    }), 401

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)