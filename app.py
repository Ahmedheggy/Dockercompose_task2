import time
import redis
import psycopg2
import os
from flask import Flask, render_template, request, jsonify

# Initialize the Flask application
app = Flask(__name__, static_folder="static", static_url_path="/static")

# Load environment variables or set default values
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')  # Redis host (default: 'redis' for Docker networking)
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))  # Redis port (default: 6379)
POSTGRES_DB = os.getenv('POSTGRES_DB', 'mydatabase')  # PostgreSQL database name
POSTGRES_USER = os.getenv('POSTGRES_USER', 'user')  # PostgreSQL username
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'password')  # PostgreSQL password

# Connect to Redis
cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=POSTGRES_DB,      # Database name
    user=POSTGRES_USER,      # Username
    password=POSTGRES_PASSWORD,  # Password
    host='db',               # Database hostname (assumed to be 'db' in a Docker environment)
    port=5432                # PostgreSQL default port
)

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

# Ensure the visits table exists (stores visitor name and timestamp)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS visits (
        id SERIAL PRIMARY KEY,               -- Unique ID for each visit
        visitor_name TEXT NOT NULL,          -- Visitor's name
        visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Auto-generated timestamp
    );
""")
conn.commit()  # Commit changes to the database

# Function to get and increment the wave count
def get_wave_count(visitor_name):
    try:
        # Retrieve the current wave count from Redis
        count = cache.get("waves")

        if count is None:  
            count = 0  # Initialize count if it doesn't exist
        else:
            count = int(count)  # Convert bytes to integer

        # Increment count in Redis when a visitor waves
        count = cache.incr("waves")

        # Insert visitor's name and timestamp into the database
        cursor.execute("INSERT INTO visits (visitor_name) VALUES (%s) RETURNING visit_time;", (visitor_name,))
        visit_time = cursor.fetchone()[0]  # Fetch the generated timestamp
        conn.commit()

        return count, visit_time  # Return updated wave count and timestamp
    except (redis.exceptions.ConnectionError, psycopg2.DatabaseError) as exc:
        print(f"⚠️ Error: {exc}")  # Print error message if Redis or PostgreSQL fails
        return None, None  # Return None values on failure

# API route to handle visitor waves
@app.route('/wave', methods=['POST'])
def wave():
    if not conn:
        return jsonify({"message": "⚠️ Database is not connected"}), 500  # Error if DB connection fails

    data = request.json  # Get JSON data from the request
    visitor_name = data.get("name", "Guest").strip()  # Extract visitor's name, default to "Guest"

    if not visitor_name:
        return jsonify({"message": "👋 Please enter your name!"}), 400  # Return error if name is empty

    try:
        # Increment wave count in Redis
        count = cache.incr("waves") if cache else 0  

        # Insert visitor name into PostgreSQL and fetch visit timestamp
        cursor.execute("INSERT INTO visits (visitor_name) VALUES (%s) RETURNING visit_time;", (visitor_name,))
        visit_time = cursor.fetchone()[0]
        conn.commit()

        # Return JSON response with greeting, timestamp, and wave count
        return jsonify({
            "message": f"👋 Hello, {visitor_name}!",
            "visit_time": visit_time.strftime("%Y-%m-%d %H:%M:%S"),
            "count": count
        })
    except Exception as e:
        print(f"⚠️ Error in /wave: {e}")  # Print error message
        return jsonify({"message": "⚠️ Internal server error"}), 500  # Return error response

# API route to retrieve the current wave count
@app.route('/get_count')
def get_count():
    try:
        count = cache.get("waves")  # Get the wave count from Redis

        if count is None:
            count = 0  # Default to 0 if not found

        return jsonify({"count": int(count)})  # Return count as integer
    except Exception as e:
        print(f"⚠️ Error in /get_count: {e}")  # Print error message
        return jsonify({"error": "Failed to get count"}), 500  # Return error response

# Home page route
@app.route('/')
def home():
    return render_template('index.html')  # Render index.html template

# Run the Flask application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Start server on port 5000 (accessible from any IP)
