import pyaudio
import wave

# Function to play an audio file
def play_audio(file_path):
    # Open the audio file
    wf = wave.open(file_path, 'rb')

    # Initialize PyAudio
    p = pyaudio.PyAudio()

    # Open a stream to play the audio file
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # Read data from the file and play it
    chunk = 1024  # Size of each chunk
    data = wf.readframes(chunk)
    
    while data:
        stream.write(data)
        data = wf.readframes(chunk)

    # Close the stream and PyAudio
    stream.stop_stream()
    stream.close()
    p.terminate()

# Example usage: replace 'yourfile.wav' with your audio file path
play_audio(r'AlertSounds/timer.wav')