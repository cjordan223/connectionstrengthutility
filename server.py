from flask import Flask, request, jsonify
import psycopg2
import psycopg2.extras
from psycopg2 import OperationalError, DataError
import os
from datetime import datetime

app = Flask(__name__)

def connect_db():
    try:
        connection = psycopg2.connect(
            database=os.getenv("DB_NAME", "speedtest_data"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "TpmsirfA1!"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432")
        )
        return connection
    except OperationalError as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        return None

def create_table():
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
                timestamp VARCHAR(255)  -- Changed to VARCHAR to store the custom format
            )
        """)
        connection.commit()
        cursor.close()
        connection.close()

create_table()

def is_valid_ip(ip_address):
    # old script did not catch IP's, this ensures only hosts running new script will hit the db
    unwanted_ips = {'unknown', '127.0.0.1', '127.0.1.1'}
    return ip_address not in unwanted_ips

@app.route('/speedtest', methods=['POST'])
def receive_speedtest_data():
    connection = connect_db()
    if not connection:
        return jsonify({"error": "Database connection is not established"}), 500
    try:
        data = request.get_json()
        print("Received data:", data)

        ip_address = data.get('ip_address')

        if not data.get('hostname') or not ip_address or not data.get('download_speed') or not data.get('upload_speed') or not data.get('ping'):
            return jsonify({"error": "Invalid data"}), 400

        if not is_valid_ip(ip_address):
            return jsonify({"error": "Invalid IP address"}), 400

        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO speedtest_data 
            (hostname, ip_address, download_speed, upload_speed, ping, timestamp) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                data.get('hostname'),
                ip_address,
                data.get('download_speed'),
                data.get('upload_speed'),
                data.get('ping'),
                data.get('timestamp')
            )
        )
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({"status": "Speedtest data received"}), 200
    except (DataError, psycopg2.IntegrityError) as e:
        connection.rollback()
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            connection.close()

@app.route('/api/speedtest_data', methods=['GET'])
def get_all_speedtest_data():
    connection = connect_db()
    if not connection:
        return jsonify({"error": "Database connection is not established"}), 500
    try:
        cursor = connection.cursor()
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
            "timestamp": row[6],
        } for row in rows]
        cursor.close()
        connection.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection:
            connection.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5075)
