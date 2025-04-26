from groq import Groq

client = Groq(api_key="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")

def chat_with_groq():
    messages = [
        {
            "role": "system",
            "content": "You are a Sports Expert. You are talking to a user interested in sports. Feel free to converse freely with the user but the conversation must remain related to sports. If the user starts to steer the conversation to a topic not related to sports, YOU MUST REPLY WITH \"I'm sorry I am only able to discuss sports topics\"."
        },
        {
            "role": "assistant",
            "content": "Let's talk sports!"
        }
    ]

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit", "bye"]:
            break

        messages.append({"role": "user", "content": user_input})

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )

        assistant_response = ""
        for chunk in completion:
            delta_content = chunk.choices[0].delta.content
            if delta_content:
                print(delta_content, end="", flush=True)  # Flush to ensure immediate output
                assistant_response += delta_content

        print()  # Add a newline after the full response

        messages.append({"role": "assistant", "content": assistant_response})

if __name__ == "__main__":
    chat_with_groq()


