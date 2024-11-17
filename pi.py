from assistant import *

def monitorTemp(target_temp, required_duration):
    assistant.assistant.static_temp = True
    def temperature_check():
        # Wait until the correct temperature is reached before starting timer
        while True:
            current_temperature = 3 # CHANGE!!! Connect to temperature sensor
            if current_temperature >= target_temp:
                break
            time.sleep(5)
        
        # Timer
        for remaining in range(required_duration, 0, -1):
            time.sleep(1)
        
    temp_thread = threading.Thread(target=temperature_check)
    temp_thread.daemon = True
    temp_thread.start()
    assistant.assistant.static_temp = False

# target_weight and lbs are for displaying the weight real-time
def monitorScale(target_weight, lbs):
    assistant.assistant.static_scale = True
    def scale_check():
      while assistant.assistant.static_scale:
        current_weight = 3 # CHANGE!!
        if (abs(current_weight - target_weight)) < 1:
            assistant.assistant.static_scale = False
            
        time.sleep(0.01)
    temp_thread = threading.Thread(target=scale_check)
    temp_thread.daemon = True
    temp_thread.start()
    