from groq import Groq
import tkinter as tk
from tkinter import scrolledtext
import threading

client = Groq(api_key="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")

class ChatGUI:
    def __init__(self, master):
        self.master = master
        master.title("Sports Chat with Groq")
        master.geometry("600x800")
        master.configure(bg="#f0f0f0")
        
        # Chat history display
        self.chat_frame = tk.Frame(master, bg="#f0f0f0")
        self.chat_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        self.chat_display = scrolledtext.ScrolledText(self.chat_frame, wrap=tk.WORD, 
                                                     bg="white", height=30, 
                                                     font=("Arial", 11))
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)
        
        # Input area
        self.input_frame = tk.Frame(master, bg="#f0f0f0")
        self.input_frame.pack(padx=10, pady=(0, 10), fill=tk.X)
        
        self.user_input = tk.Entry(self.input_frame, font=("Arial", 11))
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.user_input.bind("<Return>", self.send_message)
        
        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message,
                                     bg="#4a7abc", fg="white", font=("Arial", 11, "bold"))
        self.send_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Initialize Groq chat
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
        
        # Add initial assistant message to chat display
        self.update_chat_display("Assistant: Let's talk sports!", "assistant")
        
        # Set focus to input field
        self.user_input.focus()
    
    def update_chat_display(self, message, role):
        self.chat_display.config(state=tk.NORMAL)
        
        # Add some visual styling based on the role
        if role == "user":
            self.chat_display.insert(tk.END, message + "\n\n", "user")
        else:
            self.chat_display.insert(tk.END, message + "\n\n", "assistant")
            
        # Auto-scroll to the bottom
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def send_message(self, event=None):
        user_input = self.user_input.get().strip()
        if not user_input:
            return
        
        # Clear the input field
        self.user_input.delete(0, tk.END)
        
        # Update chat display with user message
        self.update_chat_display(f"You: {user_input}", "user")
        
        # Add user message to Groq messages
        self.messages.append({"role": "user", "content": user_input})
        
        # Disable input while processing
        self.user_input.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED)
        
        # Process the message in a separate thread
        threading.Thread(target=self.get_groq_response).start()
    
    def get_groq_response(self):
        try:
            # Call Groq API
            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=self.messages,
                temperature=1,
                max_completion_tokens=1024,
                top_p=1,
                stream=True,
                stop=None,
            )
            
            assistant_response = ""
            # Start with just "Assistant: " to show typing is happening
            self.master.after(0, lambda: self.start_assistant_response())
            
            # Process the streaming response
            for chunk in completion:
                delta_content = chunk.choices[0].delta.content
                if delta_content:
                    assistant_response += delta_content
                    # Update UI with each chunk
                    self.master.after(0, lambda content=assistant_response: 
                                     self.update_assistant_response(content))
            
            # Add assistant message to messages
            self.messages.append({"role": "assistant", "content": assistant_response})
            
        except Exception as e:
            # Show error in chat
            self.master.after(0, lambda: self.update_chat_display(
                f"Assistant: Sorry, there was an error: {str(e)}", "assistant"))
        
        # Re-enable input after response
        self.master.after(0, self.enable_input)
    
    def start_assistant_response(self):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "Assistant: ", "assistant")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def update_assistant_response(self, content):
        self.chat_display.config(state=tk.NORMAL)
        # Delete the previous placeholder and add the updated response
        last_line_index = self.chat_display.index(tk.END + "-2 lines")
        self.chat_display.delete(last_line_index, tk.END)
        self.chat_display.insert(tk.END, f"Assistant: {content}\n\n", "assistant")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def enable_input(self):
        self.user_input.config(state=tk.NORMAL)
        self.send_button.config(state=tk.NORMAL)
        self.user_input.focus()


def main():
    root = tk.Tk()
    app = ChatGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()


