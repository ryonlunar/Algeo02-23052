import sounddevice as sd
import numpy as np
import time
from scipy.io.wavfile import write
from threading import Thread
import os
from .wav_midi_converter import batch_wav_to_midi

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SAMPLE_RATE = 16000 # Menggunakan sample rate sebesar 16 Hz
CHANNEL = 1 # Menggunakan channel 1 sebagai melodi utama
DURATION = 20 # Durasi/interval rekaman dalam detik

INPUT_DIR = os.path.join(BASE_DIR, "recorded_input") # Folder untuk menyimpan rekaman audio dalam bentuk .wav
OUTPUT_DIR = os.path.join(BASE_DIR, "recorded_output") # Folder untuk menyimpan hasil convert menjadi .mid

# Memastikan folder ada
if not os.path.exists(INPUT_DIR):
    os.makedirs(INPUT_DIR)
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    
# Fungsi menyimpan audio ke folder input
def save_audio(audio, output_name):
    write(output_name, SAMPLE_RATE, audio)
    print(f"Audio saved to {output_name}")

# Fungsi merekam audio
def record_audio():
    chunk_counter = 0
    audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNEL, dtype='int16')
    sd.wait()
    
    chunk_name = os.path.join(INPUT_DIR, f"chunk_{chunk_counter}.wav")
    save_audio(audio, chunk_name)
    
    chunk_counter += 1
    
    batch_wav_to_midi(INPUT_DIR, OUTPUT_DIR)
    print("Mic audio conversion completed!")