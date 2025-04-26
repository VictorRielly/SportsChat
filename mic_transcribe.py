#!/usr/bin/env python
import os
import pyaudio
import asyncio
import json
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionOptions,
    LiveOptions,
)
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 8000  # Size of chunks to send to Deepgram

class MicrophoneTranscriber:
    def __init__(self):
        # Initialize PyAudio
        self.p = pyaudio.PyAudio()
        
        # Initialize Deepgram client
        options = DeepgramClientOptions(
            options={"keepalive": "true"}
        )
        self.deepgram = DeepgramClient(DEEPGRAM_API_KEY, options)
        
        # Stream setup flag
        self.setup_complete = False
        
    async def process_audio(self):
        try:
            # Configure audio stream
            stream = self.p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
            
            print("Listening... (Press Ctrl+C to stop)")
            
            # Configure live transcription
            options = LiveTranscriptionOptions(
                model="nova-2",
                punctuate=True,
                language="en-US",
                encoding="linear16",
                channels=CHANNELS,
                sample_rate=RATE,
            )
            
            # Create connection to Deepgram
            dg_connection = self.deepgram.listen.live.v("1")
            
            # Define event handlers
            async def on_message(result):
                try:
                    if result.is_final:
                        transcript = result.channel.alternatives[0].transcript
                        if transcript.strip():  # Only print non-empty transcripts
                            print(f"Transcript: {transcript}")
                except Exception as e:
                    print(f"Error processing transcript: {e}")
            
            async def on_error(error):
                print(f"Error from Deepgram: {error}")
            
            # Register event handlers
            dg_connection.on(dg_connection.Events.Transcript, on_message)
            dg_connection.on(dg_connection.Events.Error, on_error)
            
            # Start connection
            await dg_connection.start(options)
            self.setup_complete = True
            
            # Read audio from microphone and send to Deepgram
            while True:
                data = stream.read(CHUNK, exception_on_overflow=False)
                if self.setup_complete:
                    await dg_connection.send(data)
                await asyncio.sleep(0.01)
                
        except KeyboardInterrupt:
            print("\nStopping...")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            # Clean up
            if self.setup_complete:
                await dg_connection.finish()
            if 'stream' in locals():
                stream.stop_stream()
                stream.close()
            self.p.terminate()
            print("Stopped.")

    def start(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.process_audio())
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            loop.close()

if __name__ == "__main__":
    print("Microphone Transcription with Deepgram")
    print("--------------------------------------")
    
    if not DEEPGRAM_API_KEY:
        print("Get a transcription API key at https://console.deepgram.com/signup")
    else:
        transcriber = MicrophoneTranscriber()
        transcriber.start() 