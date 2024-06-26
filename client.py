#client.py
import requests
import json
import time
import speedtest
import socket
from datetime import datetime
import pytz

SERVER_URL = "http://192.168.0.19:5075/speedtest"

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        s.connect(('8.8.8.8', 1))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"An error occurred while getting the local IP address: {e}")
        return "127.0.0.1"

def format_timestamp():
    pst = pytz.timezone('America/Los_Angeles')
    now = datetime.now(pst)
    return now.strftime('%-m-%-d-%y at %-I:%M %p')

def send_speedtest_data(download_speed, upload_speed, ping):
    try:
        hostname = socket.gethostname()
        ip_address = get_local_ip()
        timestamp = format_timestamp()

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
        if download_speed is not None and upload_speed is not None and ping is not None:
            send_speedtest_data(download_speed, upload_speed, ping)
        time.sleep(60)
