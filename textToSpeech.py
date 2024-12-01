from flask import Flask, request, jsonify
import io
from google.oauth2 import service_account
from google.cloud import texttospeech
import os


app = Flask(__name__)

@app.route('text-to-speech/instruction', method=['POST'])
def text_to_speech():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    textBlock = file.read()
    
    synthesisInput = texttospeech.SynthesisInput(text=textBlock)
    
    audioOut = client.synthesize_speech(input=synthesisInput, voice=voice, audio_config=audio_config)
    
    os.makedirs(r"speechOuts", exist_ok=True)
    with open(r"speechOuts/speechOutput.mp3", "wb") as outFile:
        outFile.write(audioOut.audio_content)
    
    return jsonify({'message': 'instruction audio generated'}), 200

@app.route('text-to-speech/timer', method=['POST'])
def text_to_speech():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    textBlock = file.read()
    
    synthesisInput = texttospeech.SynthesisInput(text=textBlock)
    
    audioOut = client.synthesize_speech(input=synthesisInput, voice=voice, audio_config=audio_config)
    
    os.makedirs(r"speechOuts", exist_ok=True)
    with open(r"speechOuts/timer.mp3", "wb") as outFile:
        outFile.write(audioOut.audio_content)
    
    return jsonify({'message': 'Timer alert audio generated'}), 200 

@app.route('text-to-speech/temperature', method=['POST'])
def text_to_speech():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    textBlock = file.read()
    
    synthesisInput = texttospeech.SynthesisInput(text=textBlock)
    
    audioOut = client.synthesize_speech(input=synthesisInput, voice=voice, audio_config=audio_config)
    
    os.makedirs(r"speechOuts", exist_ok=True)
    with open(r"speechOuts/temperature.mp3", "wb") as outFile:
        outFile.write(audioOut.audio_content)
    
    return jsonify({'message': 'Temperature alert audio generated'}), 200


client_file = "serviceAccKey.json"
credentials = service_account.Credentials.from_service_account_file(client_file)
client = texttospeech.TextToSpeechClient(credentials=credentials)

voice = texttospeech.VoiceSelectionParams(
    language_code='en-US',
    name='en-US-Journey-F'  # studio al: 'en-US-Studio-O'
)

audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3,
    effects_profile_id=['small-bluetooth-speaker-class-device'],      #medium-bluetooth-speaker-class-device if we use a bigger speaker
    # not supported for journey:
    #speaking_rate=1,
    #pitch=1
)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)  # changes values
