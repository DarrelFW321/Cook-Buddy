import time
import threading
import paramiko
import json

class sensor:
    input 
    
    output = {
        'temperature' : None,
        'scale_level': None,
        'audio_out' : False,
        
    }
    temp_detect = True
    temp_goal = None
    temp_level = None
    scale_detect = True
    scale_goal = None
    scale_goal = None
    audio_out = False
    audio_in = None
    gas_detect = False
    co_level = None
    methane_level = None
    lpg_level = None
        
    class gas_type:
        CO_THRESHOLD = 50      # Carbon Monoxide threshold in ppm (OSHA 8-hour limit)
        METHANE_THRESHOLD = 10000  # Methane threshold in ppm (1% or 10,000 ppm)
        LPG_THRESHOLD = 18000    # LPG threshold in ppm (1.8% or 18,000 ppm)

        @staticmethod
        def check_gas_level(gas_value, gas_type):
            """Check the gas level against the threshold for the given gas type."""
            if gas_value >= gas_type:
                return f"Dangerous gas level detected! ({gas_value} ppm)"
            else:
                return f"Gas level is safe. ({gas_value} ppm)"
    


def monitorTemp(required_duration):
    sensor.temp_detect = True
    def temperature_check():
        # Wait until the correct temperature is reached before starting timer
        while True:
            sensor.temp_level =  # CHANGE!!! Connect to temperature sensor
            if sensor.temp_level >= sensor.temp_goal:
                break
            time.sleep(5)
        
        # Timer
        for remaining in range(required_duration, 0, -1):
            time.sleep(1)
        
    temp_thread = threading.Thread(target=temperature_check)
    temp_thread.daemon = True
    temp_thread.start()
    sensor.temp_detect = False

# target_weight and lbs are for displaying the weight real-time
def monitorScale(target_weight, lbs):
    sensor.scale_detect= True
    def scale_check():
      while sensor.scale_detect:
        current_weight = 3 # CHANGE!!
        if (abs(current_weight - target_weight)) < 1:
            sensor.scale_detect = False
            
        time.sleep(0.01)
    temp_thread = threading.Thread(target=scale_check)
    temp_thread.daemon = True
    temp_thread.start()

def monitorGas(threshold_voltage):
    def gas_check():
      while True:
        current_voltage = 3 # CHANGE!!!
        if (current_voltage >= threshold_voltage):
          # STOP PROGRAM, OR INFORM USER, WARNING
          break
        time.sleep(0.01)
    temp_thread = threading.Thread(target=gas_check)
    temp_thread.daemon = True
    temp_thread.start()
          
def send_sensor_data():
    while True:
        # Get sensor data (replace this with actual sensor code in a real scenario)
        data = get_sensor_data()
        
        # Convert the data to JSON format for easy transmission
        json_data = json.dumps(data)
        
        # Output the sensor data (for streaming via SSH)
        print(json_data)
        
        time.sleep(5) 