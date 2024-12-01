import parse
import requests
import os
from flask import Flask, request, jsonify
import requests
import speechToText
import threading
import llm 

# Replace this with the Raspberry Pi's IP
PI_IP = "192.168.175.62"
PI_PORT = 5000  
SAVE_PATH = "./uploads"  

app = Flask(__name__)


@app.route('/audio_chunk', methods=['POST'])
def receive_audio_chunk():
    try:
        audio_file = request.files.get('audio_chunk')
        if not audio_file:
            return jsonify({"error": "No audio file received"}),400
        
        audio_path = './audio_chunk.wav'
        audio_file.save(audio_path)
        print(f"Received audio chunk and saved to {audio_path}")
        
        client, config = speechToText.configure()  # Configure the speech-to-text client and config
        transcription = speechToText.speech_to_text(audio_path, client, config)  # Get transcription
        
        print(f"Transcription: {transcription}")

        # Return the transcription result
        response_data = {
            "transcription": transcription
        }

        return jsonify(response_data)
    
    except Exception as e:
        print(f"Error receiving audio chunk: {e}")
        return jsonify({"error": "Failed to process audio"}), 500

@app.route('/check_instruction_status', methods=['GET'])
def check_instruction_status():
    """Check if the assistant is ready for a new instruction."""
    if instruction.transcription == "":
        return jsonify({"status": "ready"}), 200  # Assistant is ready for a new instruction
    else:
        return jsonify({"status": "busy"}), 200  # Assistant is processing an instruction
    
@app.route('/instruction', methods=['POST'])
def receive_instruction():
    """Receive instruction from the Pi side."""
    data = request.json
    input = data.get('instruction', "")
    
    if input:
        # Simulate processing the instruction
        instruction.transcription = input
        print(f"Assistant received instruction: {input}")
        return jsonify({"status": "success", "instruction": input}), 200
    else:
        return jsonify({"error": "No instruction received"}), 400

def send_instruction_to_pi(instruction_data, audio_files=None):
    """
    Sends an instruction and optional audio files to the Raspberry Pi server.
    
    """
    url = f"http://{PI_IP}:{PI_PORT}/instruction"
    
    # Prepare the payload
    payload = {
        "set_timer": instruction_data.get("set_timer", False),
        "timer_duration": instruction_data.get("timer_duration", 0),
        "set_temperature": instruction_data.get("set_temperature", False),
        "temperature_goal": instruction_data.get("temperature_goal", None),
    }

    # Prepare the files dictionary for audio files
    files = {}
    if audio_files:
        for key, file_path in audio_files.items():
            try:
                files[key] = open(file_path, 'rb')
            except FileNotFoundError:
                print(f"Audio file not found: {file_path}")
    
    try:
        # Send a POST request with the payload and any audio files
        if files:
            response = requests.post(url, data=payload, files=files)
        else:
            response = requests.post(url, json=payload)
        
        print(f"Instruction sent. Response: {response.json()}")

    except Exception as e:
        print(f"Error sending instruction: {e}")

    finally:
        # Close all files and remove them if necessary
        for file in files.values():
            file.close()
        for file_path in audio_files.values():
            if os.path.exists(file_path):
                os.remove(file_path)

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

@app.route("/")
def UI():
    return render_template("interface.html")

@socketio.on("connect")
def on_connect():
    print("Client connected!")

@socketio.on("message")
def handle_message(data):
    print(f"Message from client: {data}")
    
def send_timer_update(timer_active, time):
    socketio.emit("timer_update", {"timer_active": timer_active, "time": time})

def send_temp_update(temp_active, target_temp):
    socketio.emit("temp_update", {"temp_active": temp_active, "target_temp": target_temp})

# def send_real_time_updates():
#     import time
#     while True:
#         socketio.emit("update", {"data": "Hello, this is a real-time update!"})
#         time.sleep(1)

if __name__ == "__main__":
    import threading
    # Start a thread to handle real-time updates
    threading.Thread(target=send_real_time_updates).start()
    socketio.run(app, debug=True)


class assistant: 
    static_timer = False  # global static context variables
    static_audio_file = None
    static_temp = False
    static_temp_value = 0
    static_on = True    

class instruction:
    transcription = ""
    static_recipe = False
    static_current_recipe = []
    static_current_instruction = ""
    static_recipe_index = 0
    instruction_data = {
    "instruction": None,
    "set_timer": False,  # Boolean flag to indicate if a timer should be set
    "timer_duration": None,  # Duration of the timer (in seconds)
    "set_temperature": False,  # Boolean flag to set a specific temperature threshold
    "temperature_goal": None,  # Temperature goal value
}
    
def reset_instruction_data():
    instruction.instruction_data.clear()
    instruction.instruction_data = {
    "instruction": None,
    "set_timer": False,  # Boolean flag to indicate if a timer should be set
    "timer_duration": None,  # Duration of the timer (in seconds)
    "set_temperature": False,  # Boolean flag to set a specific temperature threshold
    "temperature_goal": None,  # Temperature goal value
    }
    
    
def start_recipe(response):
    instruction.static_recipe_index = 0
    instruction.static_recipe = True
    instruction.static_current_recipe = parse.parse_instruction(response)
    if instruction.static_current_recipe:  # Ensure there's at least one instruction
        instruction.static_current_instruction = instruction.static_current_recipe[0]
    else:
        print("No valid recipe instructions found.")  # Debug

def continue_recipe():
    if instruction.static_recipe_index + 1 >= len(instruction.static_current_recipe):
        instruction.static_current_recipe = []
        instruction.static_recipe_index = 0
        instruction.static_current_instruction = llm.generate_response("I have finished the all steps in the recipe")
        instruction.static_recipe = False
    else:
        instruction.static_recipe_index += 1
        instruction.static_current_instruction = instruction.static_current_recipe[instruction.static_recipe_index]
    
 
def parse_sensor():
    time = parse.checktime(instruction.static_current_instruction)
    temp = parse.checktemp(instruction.static_current_instruction)
    if time:
        instruction.instruction_data["timer_duration"] = time
        instruction.instruction_data["set_timer"] = True
    if temp:
        instruction.instruction_data["temperature_goal"] = temp
        instruction.instruction_data["set_temperature"] = True

def tts():
    # Prepare text files
    files_to_send = {}

    # Write the instruction to a file
    instruction_text_file = "/textFiles/instruction.txt"
    with open(instruction_text_file, 'w') as file:
        file.write(instruction.static_current_instruction)
    files_to_send["instruction_audio"] = instruction_text_file  # Audio file for instruction

    # Check if timer is set and write timer file
    if instruction.instruction_data["set_timer"]:
        timer_text_file = "/textFiles/timer.txt"
        with open(timer_text_file, 'w') as file:
            file.write(f"Timer for {instruction.instruction_data['timer_duration']} seconds has completed!")
        files_to_send["timer_audio"] = timer_text_file  # Audio file for timer alert

    # Check if temperature goal is set and write temperature file
    if instruction.instruction_data["set_temperature"]:
        temperature_text_file = "/textFiles/temperature.txt"
        with open(temperature_text_file, 'w') as file:
            file.write(f"Temperature has reached {instruction.instruction_data['temperature_goal']} degrees!")
        files_to_send["temperature_audio"] = temperature_text_file  # Audio file for temperature alert

    with open(files_to_send["instruction_audio"], 'rb') as f:
        response = requests.post("http://localhost:5001/text-to-speech/instruction", files={'file': f})
        print(response.json())


    if "timer_audio" in files_to_send:
        with open(files_to_send["timer_audio"], 'rb') as f:
            response = requests.post("http://localhost:5001/text-to-speech/timer", files={'file': f})
            print(response.json())

    if "temperature_audio" in files_to_send:
        with open(files_to_send["temperature_audio"], 'rb') as f:
            response = requests.post("http://localhost:5001/text-to-speech/temperature", files={'file': f})
            print(response.json())
            
    send_instruction_to_pi(instruction.instruction_data, audio_files=files_to_send)
    
 
def assistant_logic():
    while assistant.static_on:
        instruction.static_current_instruction = ""
        instruction.transcription= ""
        
        reset_instruction_data()
        
        # Placeholder for receiving and processing mic audio
        
        response = llm.generate_response(instruction.transcription)  # Send user input to LLM and get response
        input_type = parse.parse_type(response)
              
        if input_type:
            if input_type == "recipe":
                    response = parse.parse_instruction(response)
                    start_recipe(response)
                    parse_sensor()
                    tts()
            else:
                continue_recipe()
                parse_sensor()
                tts()
        else:
            response = parse.parse_conversation(response)
            instruction.static_current_instruction = response
            tts()

if __name__ == '__main__':
    # Start the background thread for assistant logic
    threading.thread(target=assistant_logic, daemon=True).start()
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)