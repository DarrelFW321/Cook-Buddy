from flask import Flask, request, jsonify
from google.cloud import speech
import io

app = Flask(__name__)

@app.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    audio_content = file.read()

    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=16000,        # set sample rate
        language_code='en-US'
    )

    response = client.recognize(config=config, audio=audio)

    transcript = ''
    for result in response.results:
        transcript += result.alternatives[0].transcript

    return jsonify({'transcript': transcript})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)