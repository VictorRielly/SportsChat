import tkinter as tk
from tkinter import scrolledtext, StringVar, Entry, Button, END, messagebox
import threading
import os
import pygame
from dotenv import load_dotenv
from groq import Groq
from io import BytesIO
from pydub import AudioSegment

# Load environment variables from .env file
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Initialize pygame mixer for audio playback
pygame.mixer.init()

class SpeakingChatGUI:
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
        self.chat_display.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.chat_display.config(state="disabled")
        
        # Create entry field for user input
        self.user_input = Entry(root, width=60)
        self.user_input.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.user_input.bind("<Return>", self.send_message)
        
        # Create send button
        self.send_button = Button(root, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=1, padx=10, pady=10, sticky="e")
        
        # TTS settings
        self.tts_model = "playai-tts"
        self.tts_voice = "Fritz-PlayAI"
        self.tts_response_format = "wav"
        # Speech playback speed (1.0 = normal)
        self.tts_speed = 1.0
        
        # Speed control buttons
        self.slow_button = Button(root, text="Slow Down", command=self.slow_down)
        self.slow_button.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.fast_button = Button(root, text="Speed Up", command=self.speed_up)
        self.fast_button.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        
        # Initial welcome message
        self.add_message("Assistant: Let's talk sports!")
        self.text_to_speech("Let's talk sports!")
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Set focus to input field
        self.user_input.focus()
    
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
        except Exception as e:
            print(f"TTS Error: {str(e)}")
    
    def send_message(self, event=None):
        user_message = self.user_input.get().strip()
        if not user_message:
            return
        
        self.user_input.delete(0, END)
        self.add_message(f"You: {user_message}")
        
        # Check if user wants to exit
        if user_message.lower() == "exit":
            self.add_message("Assistant: Goodbye! Closing the application...")
            self.text_to_speech("Goodbye! Closing the application...")
            self.root.after(1500, self.root.destroy)
            return
        
        # Add message to history
        self.messages.append({"role": "user", "content": user_message})
        
        # Disable input while processing
        self.user_input.config(state="disabled")
        self.send_button.config(state="disabled")
        
        # Process message in separate thread to keep UI responsive
        threading.Thread(target=self.get_assistant_response).start()
    
    def show_error(self, message):
        """Display an error message and close the application"""
        messagebox.showerror("Configuration Error", message)
        self.root.after(1000, self.root.destroy)
    
    def get_assistant_response(self):
        try:
            # Ensure client is initialized
            if client is None:
                raise ValueError("Groq client is not initialized")
                
            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=self.messages,
                temperature=1,
                max_completion_tokens=1024,
                top_p=1,
                stream=True,
                stop=None,
            )
            
            self.chat_display.config(state="normal")
            self.chat_display.insert(END, "Assistant: ")
            self.chat_display.config(state="disabled")
            
            assistant_response = ""
            for chunk in completion:
                delta_content = chunk.choices[0].delta.content
                if delta_content:
                    self.chat_display.config(state="normal")
                    self.chat_display.insert(END, delta_content)
                    self.chat_display.see(END)
                    self.chat_display.config(state="disabled")
                    assistant_response += delta_content
            
            self.chat_display.config(state="normal")
            self.chat_display.insert(END, "\n\n")
            self.chat_display.config(state="disabled")
            
            # Add assistant response to messages
            self.messages.append({"role": "assistant", "content": assistant_response})
            
            # Convert assistant response to speech
            self.text_to_speech(assistant_response)
            
        except Exception as e:
            error_message = f"Error: {str(e)}"
            self.add_message(error_message)
            self.text_to_speech("Sorry, there was an error generating a response.")
        
        finally:
            # Re-enable input
            self.root.after(0, lambda: self.user_input.config(state="normal"))
            self.root.after(0, lambda: self.send_button.config(state="normal"))
            self.root.after(0, lambda: self.user_input.focus())

    def speed_up(self):
        """Increase playback speed by 0.1x up to 2.0x."""
        self.tts_speed = min(self.tts_speed + 0.1, 2.0)
        self.add_message(f"Playback speed: {self.tts_speed:.1f}x")

    def slow_down(self):
        """Decrease playback speed by 0.1x down to 0.5x."""
        self.tts_speed = max(self.tts_speed - 0.1, 0.5)
        self.add_message(f"Playback speed: {self.tts_speed:.1f}x")

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeakingChatGUI(root)
    root.mainloop() 