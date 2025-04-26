import sys

def main():
    print("Sports Chat Launcher")
    print("1. Terminal Version")
    print("2. GUI Version")
    choice = input("Choose option (1/2): ")
    
    if choice == "1":
        # Import and run terminal version
        from groq_bot import chat_with_groq
        chat_with_groq()
    elif choice == "2":
        # Import and run GUI version
        try:
            import tkinter as tk
            from groq_bot_gui import GroqChatGUI
            root = tk.Tk()
            app = GroqChatGUI(root)
            root.mainloop()
        except ImportError:
            print("Error: tkinter is not installed. Please install tkinter to use the GUI version.")
            sys.exit(1)
    else:
        print("Invalid option. Exiting.")

if __name__ == "__main__":
    main() 