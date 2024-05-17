#Run this on client machine - testing: Mac, RBPi, PC Concurrently
#
#
import requests
import json
import time
import speedtest
import socket
from datetime import datetime

SERVER_URL = "http://192.168.0.19:5075/speedtest"
def send_speedtest_data(download_speed, upload_speed, ping):
    try:
        # Get hostname and IP address
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
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
