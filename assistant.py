import threading
import time
import parse
import main

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = socketIO(app)

@app.route("/")
def UI():
    return render_template("interface.html")

@socketio.on("connect")
def on_connect():
    print("Client connected!")

@socketio.on("message")
def handle_message(data):
    print(f"Message from client: {data}")

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
    static_scale = False
    static_scale_value = 0
    static_audio = False
    static_temp = False
    static_temp_value = 0
    static_on = True

    @classmethod
    def interrupt_timer(cls):  # Need to change using queue
        while cls.static_audio:  # Prevents concurrent instructions
            time.sleep(5)  
        cls.static_timer = False

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
    
