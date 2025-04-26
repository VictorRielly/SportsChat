import tkinter as tk
from tkinter import scrolledtext, Button, END, messagebox
import threading
import os
import pygame
import pyaudio
import time
from dotenv import load_dotenv
from groq import Groq
from deepgram import DeepgramClient, LiveTranscriptionEvents
from io import BytesIO
from pydub import AudioSegment

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Initialize pygame mixer for audio playback
pygame.mixer.init()

# Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 8000

class SpeechToSpeechGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sports Chat with Voice")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Initialize messages list
        self.messages = [
            {
                "role": "system",
                "content": "You are a Sports Expert. You are talking to a user interested in sports. Feel free to converse freely with the user but the conversation must remain related to sports. If the user starts to steer the conversation to a topic not related to sports, YOU MUST REPLY WITH \"I'm sorry I am only able to discuss sports topics\"."
            },
            {
                "role": "assistant",
                "content": "Let's talk sports!"
            }
        ]
        
        # Create chat display area
        self.chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=20)
        self.chat_display.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        self.chat_display.config(state="disabled")
        
        # Create mic control button
        self.listening = False
        self.mic_button = Button(root, text="Start Listening", bg="green", command=self.toggle_listening)
        self.mic_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        # TTS settings
        self.tts_model = "playai-tts"
        self.tts_voice = "Fritz-PlayAI"
        self.tts_response_format = "wav"
        # Speech playback speed (1.0 = normal)
        self.tts_speed = 1.0
        
        # Speed control buttons
        self.slow_button = Button(root, text="Slow Down", command=self.slow_down)
        self.slow_button.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.fast_button = Button(root, text="Speed Up", command=self.speed_up)
        self.fast_button.grid(row=1, column=2, padx=10, pady=10, sticky="ew")
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        
        # Speech recognition variables
        self.last_speech_time = time.time()
        self.silence_threshold = 2.0  # 2 seconds of silence
        self.current_transcript = ""
        self.is_speaking = False
        self.speech_thread = None
        self.silence_thread = None
        self.dg_connection = None
        self.p = None
        self.stream = None
        
        # Initialize deepgram
        self.deepgram = DeepgramClient(DEEPGRAM_API_KEY)
        
        # Initial welcome message
        self.add_message("Assistant: Let's talk sports!")
        self.text_to_speech("Let's talk sports!")
    
    def add_message(self, message):
        self.chat_display.config(state="normal")
        self.chat_display.insert(END, message + "\n\n")
        self.chat_display.see(END)
        self.chat_display.config(state="disabled")
    
    def text_to_speech(self, text):
        """Convert text to speech and play it directly from memory"""
        try:
            response = client.audio.speech.create(
                model=self.tts_model,
                voice=self.tts_voice,
                input=text,
                response_format=self.tts_response_format
            )
            
            # Determine audio bytes from response, handling BinaryAPIResponse
            if hasattr(response, 'content'):
                audio_bytes = response.content
            elif isinstance(response, (bytes, bytearray)):
                audio_bytes = response
            elif hasattr(response, 'read'):
                audio_bytes = response.read()
            else:
                audio_bytes = bytes(response)
            audio_data = BytesIO(audio_bytes)
            audio_data.seek(0)
            
            # Apply speed change using pydub
            audio_segment = AudioSegment.from_file(audio_data, format=self.tts_response_format)
            if self.tts_speed != 1.0:
                audio_segment = audio_segment.speedup(playback_speed=self.tts_speed)
            buf = BytesIO()
            audio_segment.export(buf, format=self.tts_response_format)
            buf.seek(0)
            
            # Play the generated speech from memory
            pygame.mixer.music.load(buf)
            pygame.mixer.music.play()
            
            # Pause listening while TTS audio is playing
            if hasattr(self, 'listening') and self.listening:
                self.stop_listening()
            # Monitor audio playback and resume listening when finished
            threading.Thread(target=self._wait_for_audio_end, daemon=True).start()
        except Exception as e:
            print(f"TTS Error: {str(e)}")
    
    def toggle_listening(self):
        # If TTS audio is playing, interrupt it and resume listening
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            self.add_message("System: Audio interrupted by user.")
            # After interrupt, ensure listening is on
            if not self.listening:
                self.start_listening()
            return
        # Otherwise toggle listening state normally
        if self.listening:
            self.stop_listening()
        else:
            self.start_listening()
    
    def start_listening(self):
        self.listening = True
        self.mic_button.config(text="Stop Listening", bg="red")
        #self.add_message("System: Listening for speech...")
        
        # Start speech recognition in a separate thread
        self.speech_thread = threading.Thread(target=self.listen_for_speech)
        self.speech_thread.daemon = True
        self.speech_thread.start()
    
    def stop_listening(self):
        self.listening = False
        self.mic_button.config(text="Start Listening", bg="green")
        #self.add_message("System: Stopped listening.")
        
        # Clean up audio resources
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.p:
            self.p.terminate()
        if self.dg_connection:
            self.dg_connection.finish()
    
    def listen_for_speech(self):
        # Initialize PyAudio
        self.p = pyaudio.PyAudio()
        
        # Create Deepgram connection
        self.dg_connection = self.deepgram.listen.websocket.v("1")
        
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
            self.root.after(0, lambda: self.add_message("System: Failed to connect to speech recognition service."))
            self.root.after(0, self.stop_listening)
            return
        
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
            while self.listening:
                data = self.stream.read(CHUNK, exception_on_overflow=False)
                self.dg_connection.send(data)
        except Exception as e:
            self.root.after(0, lambda: self.add_message(f"System: Error during speech recognition: {str(e)}"))
        finally:
            # The stop_listening method will clean up resources
            pass
    
    def on_open(self, *args, **kwargs):
        print("Speech recognition connection opened!")
    
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
        print(f"Speech recognition error: {error}")
    
    def check_silence(self):
        """Check for silence and submit transcript to chat"""
        while self.listening:
            time.sleep(0.1)  # Check every 100ms
            
            current_time = time.time()
            time_since_speech = current_time - self.last_speech_time
            
            # If we have a transcript, there was speech, and now silence for threshold time
            if (self.current_transcript and 
                self.is_speaking and 
                time_since_speech >= self.silence_threshold):
                
                transcript_to_send = self.current_transcript
                print(f"Submitting to chat: {transcript_to_send}")
                
                # Schedule GUI update on main thread
                if self.root.winfo_exists():
                    self.root.after(0, lambda: self.process_speech(transcript_to_send))
                
                # Reset for next utterance
                self.current_transcript = ""
                self.is_speaking = False
    
    def process_speech(self, text):
        """Process the speech transcript and get a response"""
        if not text.strip():
            return
            
        # Check if user wants to exit
        if text.strip().lower() == "exit":
            self.add_message("System: Exit command detected. Closing application.")
            self.root.after(1500, self.root.destroy)
            return
        
        # Add message to chat display
        self.add_message(f"You: {text}")
        
        # Add message to history
        self.messages.append({"role": "user", "content": text})
        
        # Process message in separate thread to keep UI responsive
        threading.Thread(target=self.get_assistant_response).start()
    
    def get_assistant_response(self):
        try:
            # Generate response from Groq
            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=self.messages,
                temperature=1,
                max_completion_tokens=1024,
                top_p=1,
                stream=True,
                stop=None,
            )
            
            self.root.after(0, lambda: self.chat_display.config(state="normal"))
            self.root.after(0, lambda: self.chat_display.insert(END, "Assistant: "))
            self.root.after(0, lambda: self.chat_display.config(state="disabled"))
            
            assistant_response = ""
            for chunk in completion:
                delta_content = chunk.choices[0].delta.content
                if delta_content:
                    self.root.after(0, lambda content=delta_content: self.append_to_chat(content))
                    assistant_response += delta_content
            
            self.root.after(0, lambda: self.chat_display.config(state="normal"))
            self.root.after(0, lambda: self.chat_display.insert(END, "\n\n"))
            self.root.after(0, lambda: self.chat_display.config(state="disabled"))
            
            # Add assistant response to messages
            self.messages.append({"role": "assistant", "content": assistant_response})
            
            # Convert assistant response to speech
            self.text_to_speech(assistant_response)
            
        except Exception as e:
            error_message = f"Error: {str(e)}"
            self.root.after(0, lambda: self.add_message(error_message))
            self.text_to_speech("Sorry, there was an error generating a response.")
    
    def append_to_chat(self, content):
        """Append content to chat display"""
        self.chat_display.config(state="normal")
        self.chat_display.insert(END, content)
        self.chat_display.see(END)
        self.chat_display.config(state="disabled")
    
    def speed_up(self):
        """Increase playback speed by 0.1x up to 2.0x."""
        self.tts_speed = min(self.tts_speed + 0.1, 2.0)
        self.add_message(f"System: Playback speed: {self.tts_speed:.1f}x")

    def slow_down(self):
        """Decrease playback speed by 0.1x down to 0.5x."""
        self.tts_speed = max(self.tts_speed - 0.1, 0.5)
        self.add_message(f"System: Playback speed: {self.tts_speed:.1f}x")

    def show_error(self, message):
        """Display an error message and close the application"""
        messagebox.showerror("Configuration Error", message)
        self.root.after(1000, self.root.destroy)

    def _wait_for_audio_end(self):
        """Wait until TTS audio finishes and resume listening."""
        # Poll until audio playback completes
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        # Once done, resume listening if GUI still exists and not already listening
        if hasattr(self, 'root') and self.root.winfo_exists():
            if not self.listening:
                self.root.after(0, self.start_listening)

def main():
    # Check for API keys
    if not DEEPGRAM_API_KEY:
        print("Error: DEEPGRAM_API_KEY not found in environment variables.")
        return
    
    if not GROQ_API_KEY:
        print("Error: GROQ_API_KEY not found in environment variables.")
        return
        
    # Create and start the GUI
    root = tk.Tk()
    app = SpeechToSpeechGUI(root)
    
    # Start the GUI main loop
    root.mainloop()

if __name__ == "__main__":
    print("Speech-to-Speech Sports Chat")
    print("---------------------------")
    try:
        main()
    except Exception as e:
        print(f"Error: {e}") 