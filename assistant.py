import re
# Parses LLM Instructions for recipe
def parser(text): 
    # Split by periods and newlines
    sentences = re.split(r'[.\n]', text)
    
    # Remove any empty strings and strip whitespace
    sentences = [sentence.strip() for sentence in sentences if sentence]
    return sentences

def checktime(sentences):
    for sentence in sentences:
        sentence.lower()
        # Should also check for hours, and hours and minutes combined
        match = re.search(r'(\d+)\s*minutes', sentence) # Checks if minutes is within the sentence
        
        if match:
            # Return the number found before "minutes"
            return int(match.group(1))
    # Return None if no "minutes" with a preceding number is found
    return None


def checktemp(text): # Checks if recipe asks for temp
    # Find instances of temperature, Celsius symbol, farenheit 
    # The check if there is a time given
        # make a timer function
        # "Boil the water for 10 minutes" -> start timer after temperature is 100
    for sentence in text:
        sentence.lower()
        match = re.search(r'(\d+\.\d+)°C', sentence) or re.search(r'(\d+)°C', sentence) or re.search(r'(\d+\.\d+)F', sentence) or re.search(r'(\d+)F', sentence) or re.search(r'(\d+\.\d+)\s(degrees Celsius)', sentence) or re.search(r'(\d+)\s(degrees Celsius)', sentence) or re.search(r'(\d+\.\d+)\s Fahrenheit') or re.search(r'(\d+)\s Fahrenheit') or re.search(r'temperature')

        if match:
            # modify this search for hours and hours and minutes combined
            # Allow assistant to now anticipate "I'm done"
            time_match = re.search(r'(\d+)\s*minutes', sentence)
            # Define timer function

    return None

def scale(text): # Puts scale on screen?
    for sentence in text:
        sentence.lower()
        match = re.search(r'(\d+)\s*grams') or re.search(r'(\d+\.\d+)\s*grams')

        if match:
            # Define function to check scale immediately
    return None
=======
        match = re.search(r'')
    return None

def scale(): # Puts scale on screen?
    return
>>>>>>> 672ec49f3a23ed22fbe6424f7bdfc8db0f0e3fc7

def TTS(text): # Speaks text and character on screen
    return


for i in range(len(sentences)):
    ##API call for Character as well as speaking
    if checktime(sentences):
        



