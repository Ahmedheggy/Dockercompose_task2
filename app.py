import time
import redis
import psycopg2
from flask import Flask

app = Flask(__name__)

# Connect to Redis
cache = redis.Redis(host='redis', port=6379)

# Connect to PostgreSQL
db_conn = psycopg2.connect(
    dbname="mydatabase",
    user="user",
    password="password",
    host="db",
    port="5432"
)
cursor = db_conn.cursor()

# Create table if not exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS visits (
        id SERIAL PRIMARY KEY,
        count INT NOT NULL
    );
""")
db_conn.commit()

def get_hit_count():
    retries = 5
    while True:
        try:
            count = cache.incr('hits')
            cursor.execute("INSERT INTO visits (count) VALUES (%s) RETURNING id;", (count,))
            db_conn.commit()
            return count
        except (redis.exceptions.ConnectionError, psycopg2.DatabaseError) as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/')
def hello():
    count = get_hit_count()
    return f'Hello Fixed intern team! This page has been seen {count} times.\n'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
