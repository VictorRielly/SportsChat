#!/usr/bin/env python
import os
import pyaudio
import asyncio
from deepgram import DeepgramClient, LiveTranscriptionEvents
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
if not DEEPGRAM_API_KEY:
    raise EnvironmentError("Please set the DEEPGRAM_API_KEY environment variable before running")

# Tip: Adjust audio and connection settings to trade off latency vs transcript length:
# - Lower CHUNK (frames per buffer; e.g., 4000) sends audio more frequently and reduces end-to-end latency (with higher CPU/network usage).
# - Enable "interim_results": True in dg_connection.start options to stream partial transcripts immediately (lower time-to-first-result).
# - Use "utterances": True and increase "utterance_silence" (ms) in the start options to group speech into longer segments and get longer transcripts.

# Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 8000
# NOTE: CHUNK controls audio frames per send. Lower values (e.g., 4000) send smaller audio packets more frequently, reducing end-to-end transcription latency (at the expense of higher CPU/network overhead). Higher values batch more audio, increasing latency but lowering overhead.

def listen():
    # Initialize PyAudio
    p = pyaudio.PyAudio()
    
    # Create Deepgram client
    deepgram = DeepgramClient(DEEPGRAM_API_KEY)
    
    # Create connection
    dg_connection = deepgram.listen.websocket.v("1")
    
    # Define handlers
    def on_open(*args, **kwargs):
        # Handle connection open event
        print("Connection opened!")
    
    def on_message(*args, **kwargs):
        # Don't know what args is for, but kwargs is the result
        # By default, only final transcripts are printed (result.is_final), which waits for end-of-utterance. To see interim (partial) transcripts sooner and reduce perceived latency, remove or adjust this check and enable "interim_results": True in the connection options.
        if len(args) >= 2:
            result = kwargs['result']
        elif len(args) == 1:
            result = kwargs['result']
        else:
            print("No arguments")
            result = kwargs.get("result") or kwargs.get("message")
        try:
            if result and result.is_final:
                transcript = result.channel.alternatives[0].transcript
                if transcript.strip():
                    print(f"Transcript: {transcript}")
        except Exception as e:
            #print(result.Transcript)
            print(f"Error processing transcript: {e}")
    
    def on_error(*args, **kwargs):
        # Determine the error from positional or keyword arguments
        if len(args) >= 2:
            error = args[1]
        elif len(args) == 1:
            error = args[0]
        else:
            error = kwargs.get("error")
        print(f"Error: {error}")
    
    # Register event handlers (no need for async here)
    dg_connection.on(LiveTranscriptionEvents.Open, on_open)
    dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
    dg_connection.on(LiveTranscriptionEvents.Error, on_error)
    
    # Start connection
    started = dg_connection.start({
        "model": "nova-2",
        "punctuate": True,
        "language": "en-US",
        "encoding": "linear16",
        "channels": CHANNELS,
        "sample_rate": RATE,
        # Uncomment the following to tweak latency and transcription length:
        # "interim_results": True,    # Stream partial transcripts in real time (lowers time to first result)
        # "utterances": True,         # Enable utterance detection for grouping speech into longer segments
        # "utterance_silence": 500,    # Silence threshold (ms) before ending an utterance; increase to get longer segments
    })
    
    if started is False:
        print("Failed to connect to Deepgram websocket. Exiting.")
        return
    print("Listening... (Press Ctrl+C to stop)")
    
    # Open audio stream
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    
    # Send audio to Deepgram
    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            dg_connection.send(data)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        # Clean up
        stream.stop_stream()
        stream.close()
        p.terminate()
        dg_connection.finish()
        print("Stopped.")

if __name__ == "__main__":
    print("Microphone Transcription with Deepgram")
    print("--------------------------------------")
    
    try:
        listen()
    except Exception as e:
        print(f"Error: {e}") 