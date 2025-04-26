#!/usr/bin/env python
import os
import pyaudio
import time
import threading
import tkinter as tk
from deepgram import DeepgramClient, LiveTranscriptionEvents
from dotenv import load_dotenv
from groq_bot_gui import GroqChatGUI
import groq_bot

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
if not DEEPGRAM_API_KEY:
    raise EnvironmentError("Please set the DEEPGRAM_API_KEY environment variable before running")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise EnvironmentError("Please set the GROQ_API_KEY environment variable before running")


# Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 8000

class SpeechToChatIntegration:
    def __init__(self):
        self.last_speech_time = time.time()
        self.silence_threshold = 2.0  # 1 second of silence
        self.current_transcript = ""
        self.is_speaking = False
        self.app = None
        
    def set_gui(self, app):
        self.app = app
        
    def start_listening(self):
        # Initialize PyAudio
        self.p = pyaudio.PyAudio()
        
        # Create Deepgram client
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)
        
        # Create connection
        self.dg_connection = deepgram.listen.websocket.v("1")
        
        # Register event handlers
        self.dg_connection.on(LiveTranscriptionEvents.Open, self.on_open)
        self.dg_connection.on(LiveTranscriptionEvents.Transcript, self.on_message)
        self.dg_connection.on(LiveTranscriptionEvents.Error, self.on_error)
        
        # Start connection
        started = self.dg_connection.start({
            "model": "nova-2",
            "punctuate": True,
            "language": "en-US",
            "encoding": "linear16",
            "channels": CHANNELS,
            "sample_rate": RATE,
            "interim_results": True,
            "utterances": True,
            "utterance_silence": 1000,  # 1 second silence detection
        })
        
        if started is False:
            print("Failed to connect to Deepgram websocket. Exiting.")
            return
        
        print("Listening for speech... (Press Ctrl+C to stop)")
        
        # Start silence detection thread
        self.silence_thread = threading.Thread(target=self.check_silence)
        self.silence_thread.daemon = True
        self.silence_thread.start()
        
        # Open audio stream
        self.stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        # Send audio to Deepgram
        try:
            while True:
                data = self.stream.read(CHUNK, exception_on_overflow=False)
                self.dg_connection.send(data)
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            # Clean up
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
            self.dg_connection.finish()
            print("Stopped.")
    
    def on_open(self, *args, **kwargs):
        print("Connection opened!")
    
    def on_message(self, *args, **kwargs):
        try:
            if len(args) >= 2:
                result = kwargs['result']
            elif len(args) == 1:
                result = kwargs['result']
            else:
                result = kwargs.get("result") or kwargs.get("message")
            
            if result:
                transcript = result.channel.alternatives[0].transcript
                if transcript.strip():
                    # Update the last speech time
                    self.last_speech_time = time.time()
                    self.is_speaking = True
                    
                    # Update current transcript (only use final for clarity)
                    if result.is_final:
                        self.current_transcript += transcript
                        print(f"Transcript: {transcript}")
        except Exception as e:
            print(f"Error processing transcript: {e}")
    
    def on_error(self, *args, **kwargs):
        if len(args) >= 2:
            error = args[1]
        elif len(args) == 1:
            error = args[0]
        else:
            error = kwargs.get("error")
        print(f"Error: {error}")
    
    def check_silence(self):
        """Check for 1 second of silence and submit transcript to chat"""
        while True:
            time.sleep(0.1)  # Check every 100ms
            
            current_time = time.time()
            time_since_speech = current_time - self.last_speech_time
            
            # If we have a transcript, there was speech, and now silence for threshold time
            if (self.current_transcript and 
                self.is_speaking and 
                time_since_speech >= self.silence_threshold):
                
                # Submit transcript to GUI
                if self.app:
                    transcript_to_send = self.current_transcript
                    print(f"Submitting to chat: {transcript_to_send}")
                    
                    # Schedule GUI update on main thread
                    if self.app.root.winfo_exists():
                        self.app.root.after(0, lambda: self.submit_to_gui(transcript_to_send))
                
                # Reset for next utterance
                self.current_transcript = ""
                self.is_speaking = False
    
    def submit_to_gui(self, text):
        """Submit text to GUI chat"""
        if self.app and text.strip():
            # Check if user wants to exit
            if text.strip().lower() == "exit":
                print("Exit command detected. Closing application.")
                self.app.root.quit()
                return
                
            # Set the text in the entry field
            self.app.user_input.delete(0, tk.END)
            self.app.user_input.insert(0, text)
            
            # Trigger send
            self.app.send_message()

def main():
    # Create and start the GUI
    root = tk.Tk()
    app = GroqChatGUI(root)
    
    # Create and setup the speech integration
    speech_integration = SpeechToChatIntegration()
    speech_integration.set_gui(app)
    
    # Start speech recognition in a separate thread
    speech_thread = threading.Thread(target=speech_integration.start_listening)
    speech_thread.daemon = True
    speech_thread.start()
    
    # Start the GUI main loop
    root.mainloop()

if __name__ == "__main__":
    print("Speech-to-Chat Integration")
    print("-------------------------")
    try:
        main()
    except Exception as e:
        print(f"Error: {e}") 