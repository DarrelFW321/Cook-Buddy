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
        setence.lower()
        sentence.lower()
        match = re.search(r'(\d+)\s*minutes', sentence) # Checks if minutes is within the sentence   (is this reliable enough), (until instructions?)
        
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
        match = re.search(r'')
    return None

def scale(): # Puts scale on screen?
    return

def TTS(text): # Speaks text and character on screen
    return


for i in range(len(sentences)):
    ##API call for Character as well as speaking
    if checktime(sentences):
        


