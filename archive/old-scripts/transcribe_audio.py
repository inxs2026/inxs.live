#!/usr/bin/env python3
import speech_recognition as sr
import sys

audio_file = sys.argv[1]

recognizer = sr.Recognizer()

with sr.AudioFile(audio_file) as source:
    audio = recognizer.record(source)
    
try:
    text = recognizer.recognize_google(audio)
    print(text)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
