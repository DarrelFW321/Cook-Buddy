from flask import Flask, request, jsonify, send_file
import threading
import queue
import time
import os
from playsound import playsound

app = Flask(__name__)

# Define the instruction queue globally
instruction_queue = queue.Queue()
instruction_data = None

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
    "lpg": "lpg_alert.mp3" ,                  # File path to LPG alert sound
    "timer":"timer.mp3",                    # File path to timer aler sound
    "scale" :"scale_alert.mp3"
}

# State variables for sensors
sensor_data = {
    "temperature": None,  # Mock temperature, replace with actual sensor data
    "scale_level": None,   # Mock scale level
    "co_level": None,      # Mock CO level
    "methane_level": None, # Mock methane level
    "lpg_level": None,     # Mock LPG level
}

# Threshold goals for sensors
threshold_goals = {
    "temperature_goal": None,
    "scale_goal": None
}

# Lock for sensor data and instruction queue
sensor_lock = threading.Lock()
instruction_queue_lock = threading.Lock()

sensor_flags = {
    "temperature" : False,
    "scale" : False
}


# Boolean flags to control output of temperature, scale, and timer alerts
alert_flags = {
    "temperature_alert": False,
    "scale_alert": False,
    "timer_alert": False
}

# Event to stop threads if a gas alert occurs
stop_threads_event = threading.Event()

# -------- Flask Endpoints -------- #

@app.route('/instruction', methods=['POST'])
def receive_instruction():
    """Receive instruction from the assistant."""
    try:
        data = request.form if request.form else request.json
        
        instruction_data = {
            "send_audio": data.get("send_audio", False),
            "set_timer": data.get("set_timer", False),
            "timer_duration": data.get("timer_duration", 0),
            "set_temperature": data.get("set_temperature", False),
            "temperature_goal": data.get("temperature_goal", None),
            "set_scale": data.get("set_scale", False),
            "scale_goal": data.get("scale_goal", None),
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
            instruction_queue.put({"type": "instruction"})

    except Exception as e:
        print(f"Error receiving instruction: {e}")

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
        if stop_threads_event.is_set():
            break  # Stop monitoring if gas alert has been triggered

        with sensor_lock:
            if (sensor_flags["temperature"]):
                temp = sensor_data["temperature"]
            if (sensor_flags["scale"]):
                scale = sensor_data["scale_level"]
            co = sensor_data["co_level"]
            methane = sensor_data["methane_level"]
            lpg = sensor_data["lpg_level"]

        # Immediate alerts for gas levels
        if co >= CO_THRESHOLD:  # CO Threshold
            beep("co")
            stop_threads_event.set()  # Stop all threads
            break
        if methane >= METHANE_THRESHOLD:  # Methane Threshold
            beep("methane")
            stop_threads_event.set()  # Stop all threads
            break
        if lpg >= LPG_THRESHOLD:  # LPG Threshold
            beep("lpg")
            stop_threads_event.set()  # Stop all threads
            break
        
        # Lower priority alerts, added to the queue for handling
        if temp >= TEMP_THRESHOLD and not alert_flags["temperature_alert"]:  # Temperature Threshold
            alert_flags["temperature_alert"] = True
            instruction_queue.put({"type": "alert", "data": "Temperature alert!"})
            reset_temperature_goal()

        if scale >= SCALE_THRESHOLD and not alert_flags["scale_alert"]:  # Scale Threshold
            alert_flags["scale_alert"] = True
            instruction_queue.put({"type": "alert", "data": "Scale alert!"})
            reset_scale_goal()
        
        time.sleep(0.1)  # Adjust the frequency of monitoring as needed

# -------- Queue Processor -------- #

def process_queue():
    """Process instructions and alerts in the queue."""
    while True:
        if stop_threads_event.is_set():
            break  # Stop processing the queue if gas alert has been triggered

        task = instruction_queue.get()
        
        if task["type"] == "instruction":
            # Process the saved audio file and play sound
            pass
        elif task["type"] == "alert":
            alert_message = task["data"]
            print(f"ALERT: {alert_message}")
            
            if alert_message == "Temperature alert!" and not alert_flags["temperature_alert"]:
                beep("temperature")
                alert_flags["temperature_alert"] = True
            elif alert_message == "Scale alert!" and not alert_flags["scale_alert"]:
                beep("scale")
                alert_flags["scale_alert"] = True
        elif task["type"] == "timer":
            duration = task["data"]
            print(f"Processing timer for {duration} seconds.")
            start_timer(duration)
        
        instruction_queue.task_done()

def start_timer(duration):
    """Start a timer for a given duration and notify when it finishes."""
    # Set the timer as active
    print(f"Timer started for {duration} seconds.")
    # Countdown loop
    time.sleep(duration)
    print(f"Timer finished after {duration} seconds.")
    
    # Play an alert sound when the timer finishes
    if not alert_flags["timer_alert"]:
        beep("timer")  # You can change this to a specific alert if you want
        alert_flags["timer_alert"] = True

def set_temperature_goal(goal):
    """Set the temperature threshold goal."""
    sensor_flags["temperature"] = True
    threshold_goals["temperature_goal"] = goal
    print(f"Temperature goal set to {goal}°C")

def reset_temperature_goal():
    """Reset the temperature goal after it's reached."""
    threshold_goals["temperature_goal"] = None
    sensor_data["temperature"] = None
    sensor_flags["temperature"] = False
    print("Temperature goal reset.")

def set_scale_goal(goal):
    """Set the scale threshold goal."""
    sensor_flags["scale"] = True
    threshold_goals["scale_goal"] = goal
    print(f"Scale goal set to {goal}")

def reset_scale_goal():
    """Reset the scale goal after it's reached."""
    threshold_goals["scale_goal"] = None
    sensor_data["scale_level"] = None
    sensor_flags["scale"] = False
    print("Scale goal reset.")


# -------- Application Initialization -------- #

if __name__ == '__main__':
    # Start the sensor monitoring thread
    threading.Thread(target=monitor_sensors, daemon=True).start()
    
    # Start the queue processor thread
    threading.Thread(target=process_queue, daemon=True).start()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
