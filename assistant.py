import parse
import requests
import os

# Replace this with the Raspberry Pi's IP
PI_IP = "192.168.175.62"
PI_PORT = 5000  
SAVE_PATH = "./uploads"  

text = """["Cook spaghetti according to package directions.", "Meanwhile, in a large skillet, heat oil over medium heat. Add garlic and cook 1 minute. Add tomatoes and parsley and cook 5 minutes or until tomatoes are softened.", "Drain spaghetti and transfer to a large serving bowl. Add tomato mixture and Parmesan cheese and toss to combine."]"""

def fetch_audio_from_pi():
    """Fetch audio file from the Pi."""
    url = f"http://{PI_IP}:{PI_PORT}/audio"
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(SAVE_PATH, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print(f"Audio file received and saved to {SAVE_PATH}")
        else:
            print(f"Failed to fetch audio: {response.status_code}, {response.json()}")
    except Exception as e:
        print(f"Error fetching audio: {e}")

def send_instruction_to_pi(instruction_data, audio_file=None):
    """Send instruction and optionally an audio file to the Pi."""
    url = f"http://{PI_IP}:{PI_PORT}/instruction"
    
    # Prepare the payload without the audio file first
    payload = {
        "send_audio": instruction_data.get("send_audio", False),
        "set_timer": instruction_data.get("set_timer", False),
        "timer_duration": instruction_data.get("timer_duration", 0),
        "set_temperature": instruction_data.get("set_temperature", False),
        "temperature_goal": instruction_data.get("temperature_goal", None),
        "set_scale": instruction_data.get("set_scale", False),
        "scale_goal": instruction_data.get("scale_goal", None),
    }
    
    # Handle the audio file if send_audio is True or if audio_file is explicitly passed
    files = None
    if instruction_data["send_audio"] or audio_file:
        # If the audio file is passed as an argument, use that
        if audio_file:
            try:
                files = {'audio_file': open(audio_file, 'rb')}
            except FileNotFoundError:
                print(f"Audio file not found: {audio_file}")
    
    try:
        if files:
            # Send a POST request with both payload and the audio file
            response = requests.post(url, data=payload, files=files)
        else:
            # Send a POST request without the audio file
            response = requests.post(url, json=payload)
        
        print(f"Instruction sent. Response: {response.json()}")
        
        # Close the file after sending
        if files:
            files['audio_file'].close()
            os.remove(audio_file)

    except Exception as e:
        print(f"Error sending instruction: {e}")

class assistant: 
    static_timer = False  # global static context variables
    static_scale = False
    static_scale_value = 0
    static_audio = False
    static_audio_file = None
    static_temp = False
    static_temp_value = 0
    static_on = True    

class instruction:
    static_recipe_query = False
    static_new_recipe = False
    static_recipe = False
    static_current_recipe = []
    static_current_instruction = ""
    static_recipe_index = 0
    static_interrupt = False
    audio_file = None
    instruction_data = {
    "instruction": None,
    "send_audio": False,  # Boolean flag to indicate if an audio file should be sent
    "set_timer": False,  # Boolean flag to indicate if a timer should be set
    "timer_duration": None,  # Duration of the timer (in seconds)
    "set_temperature": False,  # Boolean flag to set a specific temperature threshold
    "temperature_goal": None,  # Temperature goal value
    "set_scale": False,  # Boolean flag to set a specific scale level
    "scale_goal": None,  # Scale goal value
}
    
def reset_instruction_data():
    instruction.instruction_data.clear()
    instruction.instruction_data = {
    "instruction": None,
    "send_audio": False,  # Boolean flag to indicate if an audio file should be sent
    "set_timer": False,  # Boolean flag to indicate if a timer should be set
    "timer_duration": None,  # Duration of the timer (in seconds)
    "set_temperature": False,  # Boolean flag to set a specific temperature threshold
    "temperature_goal": None,  # Temperature goal value
    "set_scale": False,  # Boolean flag to set a specific scale level
    "scale_goal": None,  # Scale goal value
    }
    os.remove(instruction.audio_file) #delete instruction audio file
    
    
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
        
def stt() -> audio_file: #set instruction.static_current_instruction into audio file and set that as instruction.audio_file
    ...
def tts() -> string: #set audio file from string
    ...      
def send_LLM(string):
    ...
def send_LLM_instruction(string):
    ...
 
def parse_sensor():
    time = parse.checktime(instruction.static_current_instruction)
    temp = parse.checktemp(instruction.static_current_instruction)
    scale = parse.scale(instruction.static_current_instruction)
    
    if time:
        instruction.instruction_data["timer_duration"] = time
        instruction.instruction_data["set_timer"] = True
    if temp:
        instruction.instruction_data["temperature_goal"] = temp
        instruction.instruction_data["set_temperature"] = True
    if scale:
        instruction.instruction_data["scale_goal"] = scale
        instruction.instruction_data["set_scale"] = True
            
while assistant.static_on:
    instruction.static_current_instruction = ""
    instruction.static_recipe_query = False
    
    reset_instruction_data()
    
    # Placeholder for receiving and processing mic audio
    audio = fetch_audio_from_pi()
    input = sst()
    
    response = send_LLM(audio)  # Send user input to LLM and get response
    input_type = parse.parse_type(response)
    
    if input_type:
        instruction.static_recipe_query = True  # If "done" or "this is a recipe"
    
    if instruction.static_new_recipe: #do you want to start for new
        instruction.static_new_recipe = False
        response = send_LLM_instruction(input)
        start_recipe(response)
        tts()
        parse_sensor()
        send_instruction_to_pi(instruction.instruction_data, instruction.audio_file)

    elif instruction.static_recipe_query:
        if input_type == "recipe":
            if instruction.static_recipe:
                instruction.static_current_instruction = "Do you want to stop the current recipe?"
                instruction.static_new_recipe = True
                tts() 
                send_instruction_to_pi(instruction.instruction_data, instruction.audio_file)
            else:
                response = send_LLM_instruction(input)  # Send actual instruction to LLM and get response
                start_recipe(response)
                tts()
                parse_sensor()
                send_instruction_to_pi(instruction.instruction_data,instruction.audio_file)
        else:
            continue_recipe()
            tts()
            parse_sensor()
            send_instruction_to_pi(instruction.instruction_data,instruction.audio_file)
    else:
        response = send_LLM_instruction(input)  # Send actual instruction to LLM and get response
        instruction.static_current_instruction = response
        tts()
        send_instruction_to_pi(instruction.instruction_data,instruction.audio_file)
    #os.remove(assistant.static_audio_file)
    
