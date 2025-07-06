import os
from flask import Flask, request, jsonify
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# This loads the database credentials from your .env file
load_dotenv()

app = Flask(__name__)

# --- NEW: Load database connection details separately ---
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")

# Check if all required variables are present
if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    raise RuntimeError("One or more database environment variables are not set in the .env file.")

# Safely construct the database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create a connection engine to your Supabase database
engine = create_engine(DATABASE_URL)

@app.route('/api/validate', methods=['POST'])
def validate_license():
    data = request.get_json()
    if not data or 'license_key' not in data:
        return jsonify({"status": "invalid", "reason": "No key provided"}), 400

    key_to_check = data['license_key']

    try:
        with engine.connect() as connection:
            query = text("SELECT is_active FROM licenses WHERE license_key = :key")
            result = connection.execute(query, {"key": key_to_check}).fetchone()

            if not result:
                return jsonify({"status": "invalid", "reason": "Key not found"}), 404

            if not result[0]: # is_active is the first column
                return jsonify({"status": "invalid", "reason": "Key has been disabled"}), 403
            
            return jsonify({"status": "valid"}), 200

    except Exception as e:
        print(f"Database error: {e}") 
        return jsonify({"status": "error", "reason": "Server error during validation"}), 500

if __name__ == "__main__":
    app.run(port=5002, debug=True)
