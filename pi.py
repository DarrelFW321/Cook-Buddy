import time
import threading
# import paramiko
import json
import wave
import pyaudio

class sensor:
    input 
    
    output = {
        'temperature' : None,
        'scale_level': None,
        'audio_out' : False,
        
    }
    temp_detect = True
    temp_goal = None
    temp_level = None
    scale_detect = True
    scale_goal = None
    scale_goal = None
    audio_out = False
    audio_in = None
    gas_detect = False
    co_level = None
    methane_level = None
    lpg_level = None
        
    class gas_type:
        CO_THRESHOLD = 50      # Carbon Monoxide threshold in ppm (OSHA 8-hour limit)
        METHANE_THRESHOLD = 10000  # Methane threshold in ppm (1% or 10,000 ppm)
        LPG_THRESHOLD = 18000    # LPG threshold in ppm (1.8% or 18,000 ppm)

        @staticmethod
        def check_gas_level(gas_value, gas_type):
            """Check the gas level against the threshold for the given gas type."""
            if gas_value >= gas_type:
                return f"Dangerous gas level detected! ({gas_value} ppm)"
            else:
                return f"Gas level is safe. ({gas_value} ppm)"
    
def monitorTemp(required_duration):
    sensor.temp_detect = True
    def temperature_check():
        # Wait until the correct temperature is reached before starting timer
        while True:
            sensor.temp_level = 1 # CHANGE!!! Connect to temperature sensor
            if sensor.temp_level >= sensor.temp_goal:
                break
            time.sleep(5)
        
        # Timer
        for remaining in range(required_duration, 0, -1):
            time.sleep(1)
        
    temp_thread = threading.Thread(target=temperature_check)
    temp_thread.daemon = True
    temp_thread.start()
    sensor.temp_detect = False

# target_weight and lbs are for displaying the weight real-time
def monitorScale(target_weight, lbs):
    sensor.scale_detect= True
    def scale_check():
      while sensor.scale_detect:
        current_weight = 3 # CHANGE!!
        if (abs(current_weight - target_weight)) < 1:
            sensor.scale_detect = False
            
        time.sleep(0.01)
    temp_thread = threading.Thread(target=scale_check)
    temp_thread.daemon = True
    temp_thread.start()

def monitorGas(threshold_voltage):
    def gas_check():
      while True:
        current_voltage = 3 # CHANGE!!!
        if (current_voltage >= threshold_voltage):
          # STOP PROGRAM, OR INFORM USER, WARNING
          break
        time.sleep(0.01)
    temp_thread = threading.Thread(target=gas_check)
    temp_thread.daemon = True
    temp_thread.start()



# Function to record audio for 10 seconds and save as .wav file
def record_audio(filename="audio.wav", duration=10, channels=1, rate=44100, chunk=1024):
    """
    Records audio from the microphone and saves it as a .wav file.
    """
    p = pyaudio.PyAudio()
    
    # Open the microphone stream
    stream = p.open(format=pyaudio.paInt16,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)

    print("Recording...")
    frames = []

    # Record for the specified duration
    start_time = time.time()
    while time.time() - start_time <= duration:
        data = stream.read(chunk)
        frames.append(data)

    print("Recording complete.")
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save the recorded audio as a .wav file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
    return filename

def microphone_in():
    # Thread function to handle recording and transcription
    def listen_and_transcribe(stt_function):
        """
        Listens to the microphone, records audio in 10-second batches,
        and processes it using the provided STT function.
        """
        output = ""
        while True:
            # Record audio and save as .wav
            wav_file = record_audio()

            # Pass the recorded audio file to the provided STT function
            transcription = stt_function(wav_file)
            if transcription == "":
                break
            output += transcription

            # Print the transcription result
            print(f"Transcription result: {transcription}")
        
        return output

    # Start the listener in a new thread
    listener_thread = threading.Thread(
        target=listen_and_transcribe, args=(custom_stt_function), daemon=True
    )
    listener_thread.start()


def AudioOut(wavFile):
    # Open the .wav file
    wf = wave.open(wavFile, 'rb')

    # Create an audio stream
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # Read data in chunks and play
    chunk = 1024
    data = wf.readframes(chunk)
    while data:
        stream.write(data)
        data = wf.readframes(chunk)

    # Stop and close the stream
    stream.stop_stream()
    stream.close()

    # Close PyAudio
    p.terminate()

