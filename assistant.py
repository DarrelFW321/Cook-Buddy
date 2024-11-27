import threading
import time
import parse
import requests  # For HTTP communication
import json

# Replace this with the Raspberry Pi's IP
PI_IP = "192.168.1.100"  # Change to your Pi's IP
PI_PORT = 5000

def fetch_audio_from_pi():
    """Fetch audio file from the Pi."""
    url = f"http://{PI_IP}:{PI_PORT}/audio"
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(SAVE_PATH, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            print(f"Audio file received and saved to {SAVE_PATH}")
        else:
            print(f"Failed to fetch audio: {response.status_code}, {response.json()}")
    except Exception as e:
        print(f"Error fetching audio: {e}")

def send_instruction_to_pi(instruction, audio_file=None):
    """Send instruction and audio file to the Pi."""
    url = f"http://{PI_IP}:{PI_PORT}/instruction"
    payload = {
        "instruction": instruction,
    }
    files = {'audio_file': audio_file} if audio_file else None
    try:
        if files:
            response = requests.post(url, data=payload, files=files)
        else:
            response = requests.post(url, json=payload)
        print(f"Instruction sent. Response: {response.json()}")
    except Exception as e:
        print(f"Error sending instruction: {e}")

def fetch_sensor_data_from_pi():
    """Fetch sensor data from the Pi."""
    url = f"http://{PI_IP}:{PI_PORT}/sensor"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"Sensor data received: {data}")
            return data
        else:
            print(f"Failed to fetch sensor data: {response.status_code}")
    except Exception as e:
        print(f"Error fetching sensor data: {e}")
    return {}


class assistant: 
    static_timer = False  # global static context variables
    static_scale = False
    static_scale_value = 0
    static_audio = False
    static_temp = False
    static_temp_value = 0
    static_on = True    

    @classmethod
    def start_timer(cls, seconds):
        cls.static_timer = True
        print(f"Timer started for {seconds} seconds.")
        time.sleep(seconds)  # Sleep for the given number of seconds

    @classmethod
    def run_timer(cls, seconds):
        timer_thread = threading.Thread(target=cls.start_timer, args=(seconds,))
        timer_thread.daemon = True  # Low-priority thread
        timer_thread.start()
        
class instruction:
    static_recipe_query = False
    static_new_recipe = False
    static_recipe = False
    static_current_recipe = []
    static_recipe_index = 0
    static_interrupt = False
    static_current_instruction = ""
    
def output_response(index=1):
    if index == 1:
        print(instruction.static_current_instruction)  # Currently printing but should be sent to Pi
    elif index == 2:
        print("Do you want to stop the current recipe?")  # Currently printing but should be sent to Pi

     
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
        instruction.static_current_instruction = send_LLM_instruction(audio)
        instruction.static_recipe = False
    else:
        instruction.static_recipe_index += 1
        instruction.static_current_instruction = instruction.static_current_recipe[instruction.static_recipe_index]
        
        
def send_LLM(audio):
    ...
def send_LLM_instruction(audio):
    ...

text1 = "This Is a recipe"
text2 = """Ingredients: ["1 large whole chicken", "2 (10 1/2 oz.) cans chicken gravy", "1 (10 1/2 oz.) can cream of mushroom soup", "1 (6 oz.) box Stove Top stuffing", "4 oz. shredded cheese"], Instructions: ["Boil and debone chicken.", "Put bite size pieces in average size square casserole dish.", "Pour gravy and cream of mushroom soup over chicken; level.", "Make stuffing according to instructions on box (do not make too moist).", "Put stuffing on top of chicken and gravy; level.", "Sprinkle shredded cheese on top and bake at 350\u00b0 for approximately 20 minutes or until golden and bubbly."], Course Type:  Main
"""

def main(sensor_data):
    while assistant.static_on:
        instruction.static_current_instruction = ""
        instruction.static_recipe_query = False
        
        # Placeholder for receiving and processing mic audio
        audio = ...  # Placeholder for STT (speech-to-text)
        
        response = send_LLM(audio)  # Send user input to LLM and get response
        input_type = parse.parse_type(response)
        
        if input_type:
            instruction.static_recipe_query = True  # If "done" or "this is a recipe"
        
        if instruction.static_new_recipe: #do you want to start for new
            instruction.static_new_recipe = False
            response = send_LLM_instruction(audio)
            start_recipe(response)
            output_response(1)

        elif instruction.static_recipe_query:
            if input_type == "recipe":
                if instruction.static_recipe:
                    instruction.static_current_instruction = "Do you want to stop the current recipe?"
                    instruction.static_new_recipe = True
                    output_response(2)
                else:
                    response = send_LLM_instruction(audio)  # Send actual instruction to LLM and get response
                    start_recipe(response)
                    output_response(1)
            else:
                continue_recipe()
                output_response(1)
        else:
            response = send_LLM_instruction(audio)  # Send actual instruction to LLM and get response
            instruction.static_current_instruction = response
            output_response(1)
    
