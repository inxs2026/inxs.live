#!/usr/bin/env python3
"""
Voice Chat with Charlie
- Listen via Google Speech Recognition (free)
- Respond via Edge TTS (already set up)
"""
import speech_recognition as sr
import subprocess
import sys
import os

def listen():
    """Listen for voice input and convert to text"""
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("\n🎤 Listening... (speak now)")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
            print("🔄 Processing...")
            
            # Use Google Speech Recognition (free tier)
            text = recognizer.recognize_google(audio)
            print(f"📝 You said: {text}")
            return text
            
        except sr.WaitTimeoutError:
            print("⏱️  No speech detected")
            return None
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            return None

def send_to_charlie(text):
    """Send text to OpenClaw and get response"""
    try:
        # Use openclaw CLI to send message to main session
        result = subprocess.run(
            ['openclaw', 'chat', text],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Error: {result.stderr}"
            
    except Exception as e:
        return f"Error communicating with Charlie: {e}"

def speak(text):
    """Convert text to speech using Edge TTS"""
    try:
        # Use existing sag TTS script if available
        subprocess.run(
            ['sag', text],
            check=True,
            timeout=30
        )
    except FileNotFoundError:
        # Fallback: just print the response
        print(f"\n💬 Charlie: {text}\n")
    except Exception as e:
        print(f"TTS Error: {e}")
        print(f"\n💬 Charlie: {text}\n")

def main():
    """Main voice chat loop"""
    print("=" * 60)
    print("🎙️  VOICE CHAT WITH CHARLIE")
    print("=" * 60)
    print("\nPress Ctrl+C to exit\n")
    
    try:
        while True:
            # Listen for input
            user_input = listen()
            
            if user_input:
                # Check for exit commands
                if user_input.lower() in ['exit', 'quit', 'goodbye', 'stop']:
                    print("\n👋 Goodbye!")
                    speak("Goodbye!")
                    break
                
                # Send to Charlie and get response
                print("💭 Charlie is thinking...")
                response = send_to_charlie(user_input)
                
                # Speak the response
                speak(response)
            
            print("\n" + "-" * 60)
            
    except KeyboardInterrupt:
        print("\n\n👋 Voice chat ended")
        sys.exit(0)

if __name__ == "__main__":
    main()
