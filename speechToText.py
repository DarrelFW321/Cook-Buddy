import pyaudio
import grpc
from google.cloud import speech_v1 as speech
from google.cloud.speech_v1 import types

import google.auth

piDeviceIndex = 1   # add actual device index

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

def get_audio_stream():
    audio_interface = pyaudio.PyAudio()
    audio_stream = audio_interface.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        input_device_index = piDeviceIndex
    )
    return audio_stream

def generate_audio_chunks(audio_stream):
    while True:
        yield types.StreamingRecognizeRequest(audio_content=audio_stream.read(CHUNK))

def main():
    credentials, project_id = google.auth.default()
    client = speech.SpeechClient(credentials=credentials)

    config = types.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code="en-US",
    )
    streaming_config = types.StreamingRecognitionConfig(config=config)

    audio_stream = get_audio_stream(piDeviceIndex)
    requests = generate_audio_chunks(audio_stream)

    responses = client.streaming_recognize(config=streaming_config, requests=requests)

    for response in responses:
        for result in response.results:
            print("Transcript: {}".format(result.alternatives[0].transcript))

if __name__ == "__main__":
    main()