import re
import time
import threading
import queue

class assistant: 
    static_timer = False  # global static context variables
    static_scale = False
    static_audio = False

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
        time

# Sample text
text = """
Preheat the oven to 180°C for 5 seconds.
"""

# Parses LLM Instructions for recipe
def parser(text):
    sentences = re.split(r'[.\n]', text)
    sentences = [sentence.strip() for sentence in sentences if sentence]
    return sentences

# Handles fractional values
def convert_to_decimal(value):
    if value is None: return 0.0
    if '/' in value:
        numerator, denominator = value.split('/')
        return float(numerator) / float(denominator)
    return float(value)

def parse_time(sentence):
    match = re.search(r'(\d+/\d+|\d+\.\d+|\d+)\s*(hour|hours?)', sentence)
    match2 = re.search(r'(\d+/\d+|\d+\.\d+|\d+)\s*(minute|minutes?)', sentence)
    match3 = re.search(r'(\d+/\d+|\d+\.\d+|\d+)\s*(second|seconds?)', sentence)
    
    if match or match2 or match3:
        if match: hours = match.group(1)
        else: hours = '0'
        if match2: minutes = match2.group(1)
        else: minutes = '0'
        if match3: seconds = int(match3.group(1))
        else: seconds = 0

        hours = convert_to_decimal(hours)
        minutes = convert_to_decimal(minutes)

        total_time = 360 * hours + 60 * minutes + seconds
        return total_time
    return None

def checktime(sentences):
    for sentence in sentences:
        sentence = sentence.lower()
        time = parse_time(sentence)
        if time:
            print(f"Checking sentence:{sentence}")
            return time
    return None

def checktemp(text):
    for sentence in text:
        sentence.lower()
        print(f"Checking sentence:{sentence}")
        match = re.search(r'(\d+\.\d+)°C', sentence) or re.search(r'(\d+)°C', sentence) or re.search(r'(\d+\.\d+)F', sentence) or re.search(r'(\d+)F', sentence)

        if match:
            temperature = match.group(1)
            print(f"Temperature detected: {temperature}°")
            seconds = parse_time(sentence)
            # TODO: Need to differentiate between Fahrenheit and Celsius
            if seconds and seconds > 0:
                monitorTemp(temperature, seconds)
            else:
                return temperature    
    return None

def monitorTemp(target_temp, required_duration):
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



def scale(text):
    for sentence in text:
        sentence.lower()
        match_grams = re.search(r'(\d+/\d+|\d+\.\d+|\d+)\s*(gram|grams)', sentence)
        match_kgs = re.search(r'(\d+/\d+|\d+\.\d+|\d+)\s*(kg|kgs)', sentence)
        match_lb = re.search(r'(\d+/\d+|\d+\.\d+|\d+)\s*(lb|lbs)', sentence)
        amount_in_grams = 0

        if match_grams:
            amount = match_grams.group(1)
            amount_in_grams = convert_to_decimal(amount)
        
        elif match_kgs:
            amount = match_kgs.group(1)
            amount_in_kgs = convert_to_decimal(amount)
            amount_in_grams = amount_in_kgs * 1000
        
        elif match_lb:
            amount = match_lb.group(1)
            amount_in_lb = convert_to_decimal(amount)
            amount_in_grams = amount_in_lb * 453.592

        

    return None

# Sample usage
sentences = parser(text)
for i in range(len(sentences)):
    if checktime(sentences):
        checktemp(sentences)
    scale(sentences)
    time.sleep(10)
