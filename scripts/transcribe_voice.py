#!/usr/bin/env python3
"""
Transcribe voice messages using Google Speech Recognition
"""
import speech_recognition as sr
from pydub import AudioSegment
import sys
import os

def transcribe_audio(audio_path):
    """Transcribe audio file to text"""
    try:
        # Convert to WAV if needed
        if audio_path.endswith('.ogg'):
            print("Converting OGG to WAV...", file=sys.stderr)
            audio = AudioSegment.from_ogg(audio_path)
            wav_path = audio_path.replace('.ogg', '.wav')
            audio.export(wav_path, format='wav')
            audio_path = wav_path
        
        # Transcribe
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: transcribe_voice.py <audio_file>", file=sys.stderr)
        sys.exit(1)
    
    result = transcribe_audio(sys.argv[1])
    if result:
        print(result)
    else:
        sys.exit(1)
