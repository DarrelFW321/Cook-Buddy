import threading
import time
import assistant
import paramiko
import json
import parse

def get_sensor_data(host, username, password):
    try:
        # Initialize SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to the Raspberry Pi
        ssh.connect(host, username=username, password=password)
        
        # Command to execute the sensor script
        command = "python3 /home/pi/pi.py"
        stdin, stdout, stderr = ssh.exec_command(command)

        # Read real-time sensor data (streaming)
        for line in stdout:
            try:
                sensor_data = json.loads(line.strip())  # Parse JSON output
                print(f"Sensor Data: {sensor_data}")
                # Process or store the data as needed
            except json.JSONDecodeError:
                print(f"Received non-JSON data: {line.strip()}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

# Replace with your Raspberry Pi's credentials

def get_sensor_data_thread():
    host = "192.168.1.100"  # Replace with your Raspberry Pi's IP address
    username = "pi"         # Raspberry Pi username
    password = "raspberry"  # Raspberry Pi password
    while assistant.static_on:
        get_sensor_data(host, username, password)
        time.sleep(5)  # Fetch data every 10 seconds, adjust as needed

# Start the assistant's main loop in a separate thread
def assistant_thread():
    assistant.main()

# Main function to run both the assistant and sensor data fetching concurrently
def main():
    # Start the assistant in its own thread
    assistant_thread = threading.Thread(target=assistant_thread)
    assistant_thread.daemon = True 
    assistant_thread.start()

    # Start the sensor data thread
    sensor_thread = threading.Thread(target=get_sensor_data_thread)
    sensor_thread.daemon = True  
    sensor_thread.start()

    # Keep the main program running while threads do their work
    try:
        while True:
            time.sleep(1)  # Main loop does nothing, just waits for the threads
    except KeyboardInterrupt:
        print("Main program interrupted. Stopping threads...")
        assistant.static_on = False  # Stop the assistant loop
        time.sleep(1)  # Give threads a moment to clean up before exiting
        print("Program exited.")

if __name__ == "__main__":
    main()




