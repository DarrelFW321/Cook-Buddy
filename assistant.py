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
        match = re.search(r'(\d+)\s*minutes', sentence) # Checks if minutes is within the sentence
        
        if match:
            # Return the number found before "minutes"
            return int(match.group(1))
    # Return None if no "minutes" with a preceding number is found
    return None


def checktemp(text): # Checks if recipe asks for temp

def scale(): # Puts scale on screen?

def TTS(text): # Speaks text and character on screen


for i in range(len(sentences)):
    ##API call for Character as well as speaking
    if checktime(setences):
        


