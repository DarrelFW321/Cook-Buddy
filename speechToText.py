from flask import Flask, request, jsonify
from google.oauth2 import service_account
from google.cloud import speech
import io

app = Flask(__name__)

@app.route('/speech-to-text', methods=['POST'])
# when a window is detected to have words (non-empty string), start input again
# call on small windows, when one or two windows return empty string, then stop appending user input and submit input, restarting
def speech_to_text():       
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    audioContent = file.read()
    
    audio = speech.RecognitionAudio(content=audioContent)

    response = client.recognize(config=config, audio=audio)

    transcript = ''
    for result in response.results:
        transcript += result.alternatives[0].transcript

    return jsonify({'transcript': transcript})

client_file = "serviceAccKey.json"
credentials = service_account.Credentials.from_service_account_file(client_file)
client = speech.SpeechClient(credentials=credentials)

config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=44100,  #whatever sample rate is used
    language_code='en-US',
    model='default',
)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)