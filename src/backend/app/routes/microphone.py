import sounddevice as sd
import numpy as np
import time
from scipy.io.wavfile import write
from threading import Thread
import audio
import os
import wav_midi_converter

SAMPLE_RATE = 16000
CHANNEL = 1
DURATION = 10

INPUT_DIR = "recorded"
OUTPUT_DIR = "recorded_output"


if not os.path.exists(INPUT_DIR):
    os.makedirs(INPUT_DIR)

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    
def save_audio(audio, output_name):
    write(output_name, SAMPLE_RATE, audio)
    print(f"Audio saved to {output_name}")

def process_chunk(audio_chunk):
    avg_amplitude = np.mean(np.abs(audio_chunk))
    print(f"Average amplitude: {avg_amplitude}")
    
def record_audio():
    chunk_counter = 0
    while True:
        audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNEL, dtype='int16')
        sd.wait()
        
        process_chunk(audio)
        
        chunk_name = os.path.join(INPUT_DIR, f"chunk_{chunk_counter}.wav")
        save_audio(audio, chunk_name)
        
        wav_midi_converter.batch_wav_to_midi(INPUT_DIR, OUTPUT_DIR)
        
        chunk_counter += 1
        
        time.sleep(0.1)


def start_record():
    recording_thread = Thread(target=record_audio)
    recording_thread.daemon = True
    recording_thread.start()
    
    print("Recording started...")
    
start_record()






try:
    while True:
        time.sleep(1)  # Keep the main thread alive
except KeyboardInterrupt:
    print("Recording stopped.")

