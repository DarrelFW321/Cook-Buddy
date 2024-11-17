import re
import threading
import time
import queue
from parse import *

class assistant: 
    static_timer = False  # global static context variables
    static_scale = False
    static_scale_value = 0
    static_audio = False
    static_temp = False
    static_temp_value = 0
    static_on = True
    
    @classmethod
    def interrupt_timer(cls):  #need to change using queue
        while assistant.static_audio:  # So two instructions are not at the same time
            time.sleep(5)  

        assistant.static_timer = False

    @classmethod
    def start_timer(cls, seconds):
        assistant.static_timer = True
        print(f"Timer started for {seconds} seconds.")
        time.sleep(seconds)  # Sleep for the given number of seconds

    @classmethod
    def run_timer(cls, seconds):
        timer_thread = threading.Thread(target=assistant.start_timer, args=(seconds,))
        timer_thread.daemon = True  # low priority thread
        timer_thread.start()
        
class instruction:
    static_recipe_query = False
    static_new_recipe = False
    static_recipe = False
    static_current_recipe=[]
    static_recipe_index = 0
    static_interrupt = False
    
def start_recipe():
    LLM_out = send_LLML(audio)
    static_current_recipe = LLM_out.split()
    output_response(instruction.static_recipe, instruction.static_)





#main loop
while(assistant.static_on):
    #receive mic audio
    
    #stt (receive instruction)
    
    #send to llm
    
    if(assistant.static_recipe_query): #if asks anything regarding recipe ( )
        if (assistant.recipe):
            new_recipe_query()
            if(next_step()):
                continue_recipe()
        else:
            start_recipe()
            
            
    elif(next_step()): #if there is next step
        continue_recipe()
    else:
        output_response()
        
    
    #audio out
    
    
