import requests

# Server URL (replace with the IP address of your Raspberry Pi)
SERVER_URL = "http://192.168.175.62:5000"

# Test connection to the server
response = requests.get(SERVER_URL)
print(f"Server says: {response.text}")

file_path = "Recording.mp3"  # Replace with the path to the file you want to send
with open(file_path, 'rb') as f:
    files = {'file': f}
    response = requests.post(f"{SERVER_URL}/upload", files=files)
    print(response.json())