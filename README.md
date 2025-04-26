# Sports Chat with Groq

A chat application for discussing sports topics using the Groq API with the llama3-70b-8192 model.

## Features

- Terminal-based chat interface
- GUI interface built with tkinter
- Streaming responses for a more natural conversation
- Sports-focused conversation guardrails

## Requirements

- Python 3.6+
- groq Python package
- tkinter (for GUI version)

## Installation

1. Ensure you have Python installed
2. Install the required packages:
   ```
   pip install groq
   ```
3. tkinter is included with most Python installations. If not, install according to your OS:
   - Windows: Usually included with Python
   - macOS: `brew install python-tk`
   - Linux: `sudo apt-get install python3-tk`

## Usage

### Option 1: Use the launcher

Run the launcher script to choose between GUI and terminal versions:

```
python sports_chat_launcher.py
```

### Option 2: Run specific version directly

For terminal version:
```
python groq_bot.py
```

For GUI version:
```
python groq_bot_gui.py
```

## How to Use

- Type your sports-related questions or comments
- The AI will respond with sports information
- If you try to discuss non-sports topics, the AI will politely redirect the conversation
- Type "quit", "exit", or "bye" to end the conversation (in terminal mode)

## Note

This application requires a valid Groq API key which is already configured in the code. 