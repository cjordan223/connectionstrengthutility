import requests
import json
import time
import speedtest
import socket
from datetime import datetime
# tried calling speedtest server directly

# FIXED
# https://stackoverflow.com/questions/39970606/gaierror-errno-8-nodename-nor-servname-provided-or-not-known-with-macos-sie
# can directly use localhost if the script is intended to run on the same machine.

SERVER_URL = "http://192.168.0.19:5075/speedtest"
SERVER_ID = 17846

def get_ip_address():
    try:
        # Directly use 'localhost' for local IP
        return '127.0.0.1'
    except Exception as e:
        print(f"Error getting IP address: {e}")
    return "unknown"

def send_speedtest_data(download_speed, upload_speed, ping):
    try:
        # Get hostname and IP address
        hostname = socket.gethostname()
        ip_address = get_ip_address()
        timestamp = datetime.now().isoformat()

        data = {
            "hostname": hostname,
            "ip_address": ip_address,
            "timestamp": timestamp,
            "download_speed": download_speed,
            "upload_speed": upload_speed,
            "ping": ping
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(SERVER_URL, data=json.dumps(data), headers=headers)

        if response.status_code == 200:
            print("Speedtest data sent successfully")
        else:
            print(f"Failed to send data: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

def run_speedtest():
    try:
        st = speedtest.Speedtest()
        st.get_servers([SERVER_ID])
        st.get_best_server()
        st.download()
        st.upload()
        results = st.results.dict()
        return results['download'] / 1e6, results['upload'] / 1e6, results['ping']
    except Exception as e:
        print(f"An error occurred during the speed test: {e}")
        return None, None, None

if __name__ == "__main__":
    while True:
        download_speed, upload_speed, ping = run_speedtest()
        if download_speed and upload_speed and ping:
            send_speedtest_data(download_speed, upload_speed, ping)
        time.sleep(300)  # Send data every 5 minutes
