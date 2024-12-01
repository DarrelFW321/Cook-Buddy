import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd
from pydub import AudioSegment
from pydub.playback import play
import threading

# Load your audio file (MP3)
audio_path = r'C:\Users\archi\Downloads\file_example_MP3_700KB.mp3'  # Replace with your audio file path
audio = AudioSegment.from_mp3(audio_path)

def play_audio():
    play(audio)

def animate_waveform():
    BUFFER = 1024
    RATE = audio.frame_rate

    fig, ax = plt.subplots(figsize=(15, 5))
    # Initialize x with an arbitrary size; we'll update it dynamically
    x = np.arange(0, BUFFER)
    line, = ax.plot(x, np.random.rand(BUFFER), lw=2, color='turquoise')
    ax.set_ylim(-30000, 30000)
    ax.set_xlim(0, BUFFER)
    ax.axis('off')
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')

    def smooth(data, window_len=11):
        if window_len < 3:
            return data
        # Create a Hann window
        w = np.hanning(window_len)
        # Perform convolution with 'same' mode
        y = np.convolve(data, w / w.sum(), mode='same')
        return y

    def audio_callback(indata, frames, time, status):
        if status:
            print(status)
        data = indata[:, 0]
        data = smooth(data, window_len=10)
        # Update x to match the length of data
        x = np.arange(len(data))
        line.set_data(x, data)
        ax.set_xlim(0, len(data))
        fig.canvas.draw()
        fig.canvas.flush_events()

    stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=RATE, blocksize=BUFFER)

    with stream:
        plt.show()

# Create threads
thread_play = threading.Thread(target=play_audio)
thread_visualize = threading.Thread(target=animate_waveform)

# Start threads
thread_play.start()
thread_visualize.start()

# Wait for threads to finish
thread_play.join()
thread_visualize.join()
