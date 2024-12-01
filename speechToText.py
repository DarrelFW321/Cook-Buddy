from google.oauth2 import service_account
from google.cloud import speech
import io

def configure():
    client_file = "serviceAccKey.json"
    credentials = service_account.Credentials.from_service_account_file(client_file)
    client = speech.SpeechClient(credentials=credentials)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=44100,  #whatever sample rate is used
        language_code='en-US',
        model='default',
    )
    
    return (client, config)

def speech_to_text(filePath, client, config):       
    with open(filePath, "rb") as file:
        audioContent = file.read()
        
        audio = speech.RecognitionAudio(content=audioContent)

        response = client.recognize(config=config, audio=audio)

        transcript = ''
        for result in response.results:
            transcript += result.alternatives[0].transcript

        return transcript
