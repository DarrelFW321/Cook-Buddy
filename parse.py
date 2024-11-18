import re

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

