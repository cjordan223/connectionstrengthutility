#Run on the Ubuntu server XXX.XXX.XXX.19
#This is for the Speedtest Data set exclusively


from flask import Flask, request, jsonify
import psycopg2
import psycopg2.extras
from psycopg2 import OperationalError, DataError

app = Flask(__name__)

def connect_db():
    try:
        connection = psycopg2.connect(
            database="speedtest_data",
            user="postgres",
            password="TpmsirfA1!",
            host="localhost",
            port="5432"
        )
        return connection
    except OperationalError as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        return None

connection = connect_db()
if connection:
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS speedtest_data (
            id SERIAL PRIMARY KEY,
            hostname VARCHAR(255),
            ip_address VARCHAR(255),
            download_speed DECIMAL,
            upload_speed DECIMAL,
            ping INTEGER,
            timestamp TIMESTAMP
        )
    """)
    connection.commit()

@app.route('/speedtest', methods=['POST'])
def receive_speedtest_data():
    if not connection:
        return jsonify({"error": "Database connection is not established"}), 500
    try:
        data = request.get_json()
        print("Received data:", data)
        cursor.execute(
            """
            INSERT INTO speedtest_data 
            (hostname, ip_address, download_speed, upload_speed, ping, timestamp) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                data.get('hostname'),
                data.get('ip_address'),
                data.get('download_speed'),
                data.get('upload_speed'),
                data.get('ping'),
                data.get('timestamp')
            )
        )
        connection.commit()
        return jsonify({"status": "Speedtest data received"}), 200
    except (DataError, psycopg2.IntegrityError) as e:
        connection.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/api/speedtest_data', methods=['GET'])
def get_all_speedtest_data():
    try:
        cursor.execute("""
            SELECT id, hostname, ip_address, download_speed, upload_speed, ping, timestamp 
            FROM speedtest_data
        """)
        rows = cursor.fetchall()
        result = [{
            "id": row[0],
            "hostname": row[1],
            "ip_address": row[2],
            "download_speed": row[3],
            "upload_speed": row[4],
            "ping": row[5],
            "timestamp": row[6].isoformat(),
        } for row in rows]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5075)

