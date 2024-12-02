from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
import threading
import json
import queue
import time
import os
import wave
import pyaudio
import requests
from playsound import playsound

app = Flask(__name__)
socketio = SocketIO(app)   # what to put here

@app.route("/")
def UI():
    return render_template("interface.html")

@socketio.on("connect")
def on_connect():
    print("Client connected!")

@socketio.on("message")
def handle_message(data):
    print(f"Message from client: {data}")

@socketio.on("cur_temp")
def sendTempToJS(curTemp):
    socketio.emit("tempData", {"curTemp": curTemp})
    
    
#@socketio.on("timer_update")
#def handle_timer_update(data):
    #print(f"TImer update received: {data}")


LAPTOP_IP = "192.168.1.x" 
LAPTOP_PORT = 5000

# Define the instruction queue globally
instruction_queue = queue.Queue()
audioOutQueue = queue.Queue()
instruction_data = None
transcription_queue = queue.Queue()  # Queue for managing transcriptions (instructions)

# Paths and thresholds
OUTPUT_AUDIO_FILE_PATH = "outputAudio.mp3"
CO_THRESHOLD = 50      # Carbon Monoxide threshold in ppm
METHANE_THRESHOLD = 10000  # Methane threshold in ppm (1% or 10,000 ppm)
LPG_THRESHOLD = 18000  # LPG threshold in ppm

# Sound files for each type of alert
ALERT_SOUNDS = {
    "activate" : "/AlertSounds/Activate.wav",
    "deactivate" : "/AlertSounds/Deactivate.wav",
    "temperature": "/AlertSounds/temperature.wav",  # File path to temperature alert sound
    "gas": "/AlertSounds/gas.mp3",               
    "timer":"/AlertSounds/timer.wav",                    # File path to timer alert sound
}

# State variables for sensors
sensor_data = {
    "temperature": None,  # Mock temperature, replace with actual sensor data
    "co_level": None,      # Mock CO level
    "methane_level": None, # Mock methane level
    "lpg_level": None,     # Mock LPG level
}

# Threshold goals for sensors
threshold_goals = {
    "temperature_goal": None,
}

# Lock for sensor data and instruction queue
sensor_lock = threading.Lock()
instruction_queue_lock = threading.Lock()

sensor_flags = {
    "temperature" : False,
}


alert_flags = {
    "temperature_alert": False,
    "timer_alert": False
}

# Event to stop threads if a gas alert occurs
stop_threads_event = threading.Event()

@app.route('/instruction', methods=['POST'])
def receive_instruction():
    """Receive instruction from the assistant."""
    # Get incoming data: form or json
    data = request.form if request.form else request.json
    
    # Extract instruction data
    instruction_data = {    
        "set_timer": data.get("set_timer", False),
        "timer_duration": data.get("timer_duration", 0),
        "set_temperature": data.get("set_temperature", False),
        "temperature_goal": data.get("temperature_goal", None),
    }

    # Handle setting temperature goal if requested
    if instruction_data["set_temperature"] and instruction_data["temperature_goal"] is not None:
        set_temperature_goal(instruction_data["temperature_goal"])

    # Handle setting a timer if requested
    if instruction_data["set_timer"]:
        instruction_queue.put({"type": "timer", "data": instruction_data["timer_duration"]})

    # Initialize a dictionary to store paths for all received audio files

    # Handle receiving and saving the instruction audio file
    instruction_audio_file = request.files.get("instruction_audio")
    if instruction_audio_file:
        instruction_audio_file.save("/AlertSounds/instruction.mp3")
        instruction_queue.put({"type": "instruction", "path":OUTPUT_AUDIO_FILE_PATH})

    # Handle receiving and saving the timer alert audio file if set
    if instruction_data["set_timer"]:
        timer_audio_file = request.files.get("timer_audio")
        if timer_audio_file:
            timer_audio_file.save("/AlertSounds/timer.mp3")


    # Handle receiving and saving the temperature alert audio file if set
    if instruction_data["set_temperature"]:
        temperature_audio_file = request.files.get("temperature_audio")
        if temperature_audio_file:
            temperature_audio_file.save("/AlertSounds/temperature.mp3")

def monitorTemp(required_duration):
    sensor_flags["temperature"] = True
    def temperature_check():
        # Wait until the correct temperature is reached before starting timer
        while True:
            curTemp = sensor_data["temperature"] # CHANGE!!! Connect to temperature sensor
            if curTemp >= threshold_goals["temperature_goal"]:
                break
            sendTempToJS()
            time.sleep(5)
        
        # Timer
        for remaining in range(required_duration, 0, -1):
            # socketio.emit("timer", {"data": remaining, "bool": True})
            time.sleep(1)
        
        socketio.emit("timer", {"data": 0, "bool": False})
        
    temp_thread = threading.Thread(target=temperature_check)
    temp_thread.daemon = True
    temp_thread.start()
    sensor_flags["temperature"] = False


def send_audio_file(filePath):
    """Send audio file to the assistant."""
    if os.path.exists(filePath):
        # Prepare the file for sending
        with open(filePath, 'rb') as audio_file:
            files = {'audio_chunk': (filePath, audio_file, 'audio/wav')}
            try:
                # Send the POST request to the Flask server
                response = requests.post(f'http://{LAPTOP_IP}:{LAPTOP_PORT}/audio_chunk', files=files)

                if response.status_code == 200:
                    # Successfully received transcription
                    transcription = response.json().get("transcription")
                    print(f"Transcription: {transcription}")
                    return jsonify({"transcription": transcription}), 200
                else:
                    # Handle errors from the Flask server
                    print(f"Error: {response.json().get('error')}")
                    return jsonify({"error": "Failed to get transcription from server"}), 500
            except Exception as e:
                print(f"Error sending audio file: {e}")
                return jsonify({"error": "Failed to send audio file"}), 500
    else:
        return jsonify({"error": "Audio file not found"}), 404


def beep(alert_type):
    """Play a unique sound based on the alert type."""
    if alert_type in ALERT_SOUNDS:
        sound_file = ALERT_SOUNDS[alert_type]
        playsound(sound_file)


def monitor_sensors():
    """Monitor sensors and trigger appropriate alerts."""
    while True:
        if stop_threads_event.is_set():
            break  # Stop monitoring if gas alert has been triggered

        with sensor_lock:
            if (sensor_flags["temperature"]):
                temp = sensor_data["temperature"]
            co = sensor_data["co_level"]
            methane = sensor_data["methane_level"]
            lpg = sensor_data["lpg_level"]

        # Immediate alerts for gas levels
        if co >= CO_THRESHOLD:  # CO Threshold
            beep("gas")
            stop_threads_event.set()  # Stop all threads
            break
        if methane >= METHANE_THRESHOLD:  # Methane Threshold
            beep("gas")
            stop_threads_event.set()  # Stop all threads
            break
        if lpg >= LPG_THRESHOLD:  # LPG Threshold
            beep("gas")
            stop_threads_event.set()  # Stop all threads
            break
        
        if temp >= threshold_goals["temperature_goal"] and not alert_flags["temperature_alert"]:  # Temperature Threshold
            alert_flags["temperature_alert"] = True
            instruction_queue.put({"type": "alert", "data": "Temperature alert!"})
            threading.Thread(target =beep("temperature"), daemon=True).start()
            reset_temperature_goal()
        time.sleep(0.1)  # Adjust the frequency of monitoring as needed


def process_queue():
    """Process instructions and alerts in the queue."""
    while True:
        if stop_threads_event.is_set():
            break  # Stop processing the queue if gas alert has been triggered

        task = instruction_queue.get()
        
        if task["type"] == "instruction":
            AudioOut(task["path"])
            if (task["path"] == ALERT_SOUNDS["timer"]):
                alert_flags["timer_alert"] = False
        elif task["type"] == "alert":
            alert_message = task["data"]
            print(f"ALERT: {alert_message}")
            
            if alert_message == "Temperature alert!" and not alert_flags["temperature_alert"]:
                AudioOut(ALERT_SOUNDS["temperature"])
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
        instruction_queue.put({"type": "instruction", "path": ALERT_SOUNDS["timer"]})
        beep("timer") 
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
    """
    Listens to the microphone, records audio in 10-second batches,
    and processes it using the provided STT function.
    """
    
    transcription_buffer = ""
    initial_flag = False
    
    while True:
        if stop_threads_event.is_set():
            break  # Stop processing the queue if gas alert has been triggered

        try:
            # Record audio and save as .wav
            wav_file = record_audio()
            transcription = send_audio_file(wav_file)

            # Check for valid transcription
            if transcription and transcription.strip():
                if initial_flag:
                    beep("activate")
                    initial_flag = False
                # Append transcription to the buffer if there's no ongoing instruction being processed
                transcription_buffer += transcription.strip() + " "  # Append with a space
                print(f"Updated instruction buffer: {transcription_buffer}")
            else:
                # Handle empty transcription
                if transcription_buffer.strip():
                    beep ("deactivate")
                    initial_flag = True
                    print(f"Complete instruction received: {transcription_buffer}")
                    transcription_queue.put(transcription_buffer.strip())  # Add instruction to the queue
                else:
                    print("Empty transcription received, no data to send.")
                    
                transcription_buffer = ""  # Clear the buffer after adding to the queue

        except Exception as e:
            print(f"Error in listen_and_transcribe: {e}")
            
def is_assistant_ready():
    """Check if the assistant is ready to receive a new instruction."""
    try:
        response = requests.get(f"http://{LAPTOP_IP}:{LAPTOP_PORT}/check_instruction_status")
        if response.status_code == 200:
            status = response.json().get("status")
            return status == "ready"
        else:
            print(f"Failed to check assistant status. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error checking assistant status: {e}")
        return False

def send_to_assistant(instruction):
    """
    Sends the accumulated instruction to the assistant via HTTP POST.
    """
    try:
        payload = {"instruction": instruction}
        response = requests.post(f"http://{LAPTOP_IP}:{LAPTOP_PORT}/instruction", json=payload)

        if response.status_code == 200:
            print(f"Instruction successfully sent to assistant: {instruction}")
        else:
            print(f"Failed to send instruction to assistant. Status code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error sending instruction to assistant: {e}")
            
            
def process_transcription_queue():
    """Process the transcription queue and send instructions when the assistant is ready."""
    while True:
        if stop_threads_event.is_set():
            break  # Stop processing the queue if gas alert has been triggered

        # Wait for an instruction to be available in the queue
        instruction = transcription_queue.get()

        if instruction:
            print(f"Processing instruction: {instruction}")
            
            # Check if the assistant is ready for a new instruction
            if is_assistant_ready():
                send_to_assistant(instruction)  # Send instruction to the assistant
                transcription_queue.task_done()  # Indicate that the task is finished
            else:
                # If the assistant is busy, add the instruction back to the queue
                print("Assistant is busy, retrying later.")
                transcription_queue.put(instruction)  # Re-add to the queue for later processing
        
        time.sleep(0.25)
        
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

    alert_flags["temperature_alert"] = False
    # Close PyAudio
    p.terminate()


# -------- Application Initialization -------- #


if __name__ == "__main__":
    threading.Thread(target=process_transcription_queue, daemon=True).start()
    threading.Thread(target=process_queue, daemon=True).start()
    threading.Thread(target=monitor_sensors, daemon=True).start()
    threading.Thread(target=microphone_in, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
