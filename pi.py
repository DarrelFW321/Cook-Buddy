from flask import Flask, request, jsonify, send_file
import threading
import json
import queue
import time
import os
import wave
import pyaudio
from playsound import playsound
import speechToText

app = Flask(__name__)

# Define the instruction queue globally
instruction_queue = queue.Queue()
audioOutQueue = queue.Queue()
instruction_data = None

# Paths and thresholds
OUTPUT_AUDIO_FILE_PATH = "outputAudio.wav"
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
            audio_file.save(OUTPUT_AUDIO_FILE_PATH)
            instruction_data["audio_file"] = OUTPUT_AUDIO_FILE_PATH
            print(f"Audio file saved to {OUTPUT_AUDIO_FILE_PATH}")
            instruction_queue.put({"type": "instruction"})

    except Exception as e:
        print(f"Error receiving instruction: {e}")

@app.route('/audio', methods=['GET'])
def send_audio_file(filepath):
    """Send audio file to the assistant."""
    if audioOutQueue:
        filePath = audioOutQueue.pop
        if os.path.exists(filePath):
            return filePath
        else:
            jsonify({"error": "Audio file not found"}), 404
    else:
        return jsonify({"error": "No Audio File in Queue"}), 404

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
            AudioOut(OUTPUT_AUDIO_FILE_PATH)
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


# Function to record audio for 10 seconds and save as .wav file
def record_audio(filename="inputAudio.wav", duration=10, channels=1, rate=44100, chunk=1024):
    """
    Records audio from the microphone and saves it as a .wav file.
    """
    p = pyaudio.PyAudio()
    
    # Open the microphone stream
    stream = p.open(format=pyaudio.paInt16,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)

    print("Recording...")
    frames = []

    # Record for the specified duration
    start_time = time.time()
    while time.time() - start_time <= duration:
        data = stream.read(chunk)
        frames.append(data)

    print("Recording complete.")
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save the recorded audio as a .wav file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
    return filename

def microphone_in():
    # Thread function to handle recording and transcription
    configAndClient = speechToText.configure()
    client = configAndClient[0]
    config = configAndClient[1]
    audioFilePath = "outputAudio.wav"
    
    def listen_and_transcribe(stt_function):
        """
        Listens to the microphone, records audio in 10-second batches,
        and processes it using the provided STT function.
        """
        output = ""
        while True:
            # Record audio and save as .wav
            wav_file = record_audio()

            # stt_function(wav_file)
            
            audioOutQueue.put(audioFilePath)
            # Pass the recorded audio file to the provided STT function
            # send via flask to stt on laptop
            transcription = # retrieve and write      
            if transcription == "":
                break
            output += transcription

            # Print the transcription result
            print(f"Transcription result: {transcription}")
        
        return output

    # Start the listener in a new thread
    listener_thread = threading.Thread(
        target=listen_and_transcribe, args=(speechToText.speech_to_text(audioFilePath, client, config)), daemon=True
    )
    listener_thread.start()


def AudioOut(wavFile):
    # Open the .wav file
    wf = wave.open(wavFile, 'rb')

    # Create an audio stream
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # Read data in chunks and play
    chunk = 1024
    data = wf.readframes(chunk)
    while data:
        stream.write(data)
        data = wf.readframes(chunk)

    # Stop and close the stream
    stream.stop_stream()
    stream.close()

    # Close PyAudio
    p.terminate()


# -------- Application Initialization -------- #

if __name__ == '__main__':
    # Start the sensor monitoring thread
    threading.Thread(target=monitor_sensors, daemon=True).start()
    
    threading.Thread(target=microphone_in, daemon=True).start()
    
    # Start the queue processor thread
    threading.Thread(target=process_queue, daemon=True).start()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
