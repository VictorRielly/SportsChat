import tkinter as tk
from tkinter import scrolledtext, StringVar, Entry, Button, END
import threading
from groq import Groq
from groq_bot import client

class GroqChatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sports Chat with Groq")
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
        
        # Initial welcome message
        self.add_message("Assistant: Let's talk sports!")
        
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
    
    def send_message(self, event=None):
        user_message = self.user_input.get().strip()
        if not user_message:
            return
        
        self.user_input.delete(0, END)
        self.add_message(f"You: {user_message}")
        
        # Check if user wants to exit
        if user_message.lower() == "exit":
            self.add_message("Assistant: Goodbye! Closing the application...")
            self.root.after(1500, self.root.destroy)
            return
        
        # Add message to history
        self.messages.append({"role": "user", "content": user_message})
        
        # Disable input while processing
        self.user_input.config(state="disabled")
        self.send_button.config(state="disabled")
        
        # Process message in separate thread to keep UI responsive
        threading.Thread(target=self.get_assistant_response).start()
    
    def get_assistant_response(self):
        try:
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
            
        except Exception as e:
            self.add_message(f"Error: {str(e)}")
        
        finally:
            # Re-enable input
            self.root.after(0, lambda: self.user_input.config(state="normal"))
            self.root.after(0, lambda: self.send_button.config(state="normal"))
            self.root.after(0, lambda: self.user_input.focus())

if __name__ == "__main__":
    root = tk.Tk()
    app = GroqChatGUI(root)
    root.mainloop() 