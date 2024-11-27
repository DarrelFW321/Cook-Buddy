from flask import Flask, request, jsonify, send_file
import threading
import queue
import time
import os
from playsound import playsound

app = Flask(__name__)

# Define the instruction queue globally
instruction_queue = queue.Queue()

# Paths and thresholds
AUDIO_FILE_PATH = "test_audio.mp3"  # Set the path for the audio file
TIMER_DURATION = 0  # Timer duration in seconds (can be set dynamically)
CO_THRESHOLD = 50      # Carbon Monoxide threshold in ppm
METHANE_THRESHOLD = 10000  # Methane threshold in ppm (1% or 10,000 ppm)
LPG_THRESHOLD = 18000  # LPG threshold in ppm
TEMP_THRESHOLD = None    # Example: Temperature threshold in Celsius
SCALE_THRESHOLD = None   # Example: Scale threshold

# Sound files for each type of alert
ALERT_SOUNDS = {
    "temperature": "temperature_alert.mp3",  # File path to temperature alert sound
    "co": "co_alert.mp3",                    # File path to CO alert sound
    "methane": "methane_alert.mp3",          # File path to methane alert sound
    "lpg": "lpg_alert.mp3"                   # File path to LPG alert sound
}

# State variables for sensors
sensor_data = {
    "temperature": 0,  # Mock temperature, replace with actual sensor data
    "scale_level": 0,   # Mock scale level
    "co_level": 0,      # Mock CO level
    "methane_level": 0, # Mock methane level
    "lpg_level": 0,     # Mock LPG level
}

# Threshold goals for sensors
threshold_goals = {
    "temperature_goal": None,
    "scale_goal": None
}

# Thread-safe flags for status
flags = {
    "timer_active": False,
    "alert_active": False,
}

# Lock for sensor data and instruction queue
sensor_lock = threading.Lock()
instruction_queue_lock = threading.Lock()


# -------- Flask Endpoints -------- #

@app.route('/instruction', methods=['POST'])
def receive_instruction():
    """Receive instruction from the assistant."""
    try:
        data = request.form if request.form else request.json
        
        # Create the instruction_data dictionary (without unnecessary fields like alert_message)
        instruction_data = {
            "instruction": data.get("instruction", ""),
            "send_audio": data.get("send_audio", False),
            "set_timer": data.get("set_timer", False),
            "timer_duration": data.get("timer_duration", 0),
            "set_temperature": data.get("set_temperature", False),
            "temperature_goal": data.get("temperature_goal", None),
            "set_scale": data.get("set_scale", False),
            "scale_goal": data.get("scale_goal", None),
            "alert": data.get("alert", False),  # You may keep this if you want to handle alerts
        }

        # Handle setting temperature goal if requested
        if instruction_data["set_temperature"] and instruction_data["temperature_goal"] is not None:
            set_temperature_goal(instruction_data["temperature_goal"])

        # Handle setting scale goal if requested
        if instruction_data["set_scale"] and instruction_data["scale_goal"] is not None:
            set_scale_goal(instruction_data["scale_goal"])

        # Handle setting a timer if requested
        if instruction_data["set_timer"]:
            instruction_queue.put({"type": "timer", "data": instruction_data["timer_duration"]})

        # Handle receiving and saving an audio file if provided
        audio_file = request.files.get("audio_file")
        if audio_file:
            audio_file.save(AUDIO_FILE_PATH)
            instruction_data["audio_file"] = AUDIO_FILE_PATH
            print(f"Audio file saved to {AUDIO_FILE_PATH}")

        return jsonify({"status": "Instruction received", "data": instruction_data}), 200

    except Exception as e:
        print(f"Error receiving instruction: {e}")
        return jsonify({"error": "Failed to receive instruction"}), 500



@app.route('/audio', methods=['GET'])
def send_audio_file():
    """Send audio file to the assistant."""
    if os.path.exists(AUDIO_FILE_PATH):
        return send_file(AUDIO_FILE_PATH, as_attachment=True)
    else:
        return jsonify({"error": "Audio file not found"}), 404


# -------- Beep Function -------- #

def beep(alert_type):
    """Play a unique sound based on the alert type."""
    if alert_type in ALERT_SOUNDS:
        sound_file = ALERT_SOUNDS[alert_type]
        playsound(sound_file)


# -------- Monitor Sensors -------- #

def monitor_sensors():
    """Monitor sensors and trigger appropriate alerts."""
    while True:
        with sensor_lock:
            temp = sensor_data["temperature"]
            scale = sensor_data["scale_level"]
            co = sensor_data["co_level"]
            methane = sensor_data["methane_level"]
            lpg = sensor_data["lpg_level"]

        # Immediate alerts for gas levels
        if co >= 50:  # CO Threshold
            beep("gas_co")
        if methane >= 10000:  # Methane Threshold
            beep("gas_methane")
        if lpg >= 18000:  # LPG Threshold
            beep("gas_lpg")
        
        # Lower priority alerts, added to the queue for handling
        if temp >= TEMP_THRESHOLD:  # Temperature Threshold
            instruction_queue.put({"type": "alert", "data": "Temperature alert!"})
            reset_temperature_goal
        if scale >= SCALE_THRESHOLD:  # Scale Threshold
            instruction_queue.put({"type": "alert", "data": "Scale alert!"})
            reset_scale_goal
        
        time.sleep(0.1)  # Adjust the frequency of monitoring as needed


# -------- Queue Processor -------- #

def process_queue():
    """Process instructions and alerts in the queue."""
    while True:
        task = instruction_queue.get()
        
        if task["type"] == "instruction":
            instruction = task["data"]
            print(f"Processing instruction: {instruction}")
            # Handle specific instructions here
        
        elif task["type"] == "alert":
            alert_message = task["data"]
            print(f"ALERT: {alert_message}")
            
            if alert_message == "Temperature alert!":
                beep("temperature")
            elif alert_message == "Scale alert!":
                beep("scale")   
        elif task["type"] == "timer":
            duration = task["data"]
            print(f"Processing timer for {duration} seconds.")
            start_timer(duration)
        
        instruction_queue.task_done()
        
def start_timer(duration):
    """Start a timer for a given duration and notify when it finishes."""
    # Set the timer as active
    flags["timer_active"] = True
    print(f"Timer started for {duration} seconds.")

    # Countdown loop
    time.sleep(duration)

    # Timer is finished
    flags["timer_active"] = False
    print(f"Timer finished after {duration} seconds.")
    
    # Play an alert sound when the timer finishes
    beep("temperature")  # You can change this to a specific alert if you want

def set_temperature_goal(goal):
    """Set the temperature threshold goal."""
    threshold_goals["temperature_goal"] = goal
    print(f"Temperature goal set to {goal}°C")

def reset_temperature_goal():
    """Reset the temperature goal after it's reached."""
    threshold_goals["temperature_goal"] = None
    print("Temperature goal reset.")

def set_scale_goal(goal):
    """Set the scale threshold goal."""
    threshold_goals["scale_goal"] = goal
    print(f"Scale goal set to {goal}")

def reset_scale_goal():
    """Reset the scale goal after it's reached."""
    threshold_goals["scale_goal"] = None
    print("Scale goal reset.")


# -------- Application Initialization -------- #

if __name__ == '__main__':
    # Start the sensor monitoring thread
    threading.Thread(target=monitor_sensors, daemon=True).start()
    
    # Start the queue processor thread
    threading.Thread(target=process_queue, daemon=True).start()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
