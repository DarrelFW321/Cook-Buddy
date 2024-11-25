import threading
import time
import assistant
import paramiko
import queue
import json

class context:
    sensor_data = None #dictionary from json
    temp_detect = False
    temp_goal = None
    temp_interrupt = False
    scale_detect = False
    scale_goal = None
    scale_interrupt = False
    audio_out = False
    timer = False
    timer_interrupt = False
    
def initialize_ssh_client(host, username, password):
    """Initialize and return the SSH client to be used throughout the program."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Automatically add unknown host keys
    ssh.connect(host, username=username, password=password)   # Connect to the Raspberry Pi
    return ssh

# Function to send a command to the Raspberry Pi and get the response
def send_command_to_pi(ssh, command):
    """Send a command to the Raspberry Pi over an existing SSH connection and return the response."""
    try:
        # Send the command to the Raspberry Pi (e.g., GET_SENSOR_DATA)
        stdin, stdout, stderr = ssh.exec_command(command)
        
        # Read the response
        response = stdout.read().decode('utf-8')  # Read the response from stdout
        
        try:
            sensor_data = json.loads(response)
            return sensor_data  # Return the parsed data (e.g., temperature, humidity, gas level)
        except json.JSONDecodeError:
            print("Failed to decode response as JSON.")
            return None
        
    except Exception as e:
        print(f"Error while communicating with Raspberry Pi: {e}")
        return None

# Function to start the assistant (which will manage the recipe and sensor data)
def start_assistant():
    """Start the assistant and process sensor data as needed."""
    assistant.main()  # Call the assistant's main method to start the assistant process

# Main loop to handle commands and interact with the assistant
def main():
    # Set Raspberry Pi SSH credentials
    host = "192.168.1.100"  # Replace with your Pi's IP address
    username = "pi"  # Pi username
    password = "raspberry"  # Pi password
    
    # Initialize the SSH client once (persistent connection)
    ssh = initialize_ssh_client(host, username, password)
    
    try:
        while assistant.static_on:
            # For the sake of this example, let's just send a command to get sensor data
            command = "GET_SENSOR_DATA"
            
            # Send the command to Raspberry Pi and get the response
            sensor_data = send_command_to_pi(ssh, command)
            
            if sensor_data:
                print("Sensor Data from Pi:", sensor_data)
            
            # You can process the data further as needed
            
            # Check if the assistant should continue running
            time.sleep(5)
    
    finally:
        # Close the SSH connection when the loop ends
        ssh.close()
        print("SSH connection closed.")

if __name__ == "__main__":
    main()