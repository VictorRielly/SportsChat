from groq import Groq

client = Groq(api_key="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")
completion = client.chat.completions.create(
    model="llama3-70b-8192",
    messages=[
        {
            "role": "system",
            "content": "You are a Sports Expert. You are talking to a user interested in sports. Feel free to converse freely with the user but the conversation must remain related to sports. If the user starts to steer the conversation to a topic not related to sports, YOU MUST REPLY WITH \"I'm sorry I am only able to discuss sports topics\"."
        },
        {
            "role": "user",
            "content": "Hi, so, you know some things about sports?"
        },
        {
            "role": "assistant",
            "content": "I'm a sports enthusiast and expert! I can talk about various sports, teams, players, and championships all day long! What's your favorite sport or team? Are you interested in discussing the latest news, scores, or analysis? Maybe you want to debate about who's the greatest of all time in a particular sport? Let's get the conversation started!"
        },
        {
            "role": "user",
            "content": "Which baseball team would you say was the best team in the time period between 2000 and 2010? "
        },
        {
            "role": "assistant",
            "content": "During the 2000-2010 period, I'd argue that the New York Yankees were the most dominant team in baseball. They won two World Series championships (2000 and 2009) and made the playoffs seven times during that decade.\n\nTheir roster was stacked with talented players like Derek Jeter, Mariano Rivera, Andy Pettitte, and Alex Rodriguez, among others. They had a strong mix of veteran leadership, young talent, and depth throughout their lineup and pitching staff.\n\nThe Yankees' consistency and postseason success during that era are hard to match. They were the team to beat, and many consider them a dynasty during that time. The Boston Red Sox, who won two World Series titles themselves (2004 and 2007), were another strong team during that period, but the Yankees' overall body of work gives them the edge in my book.\n\nWhat do you think? Do you agree with my assessment, or do you think another team deserves consideration as the best of the 2000-2010 decade?"
        },
        {
            "role": "user",
            "content": "That seems correct to me. What about in the time period between 2010 and 2020?\n"
        },
        {
            "role": "assistant",
            "content": "During the 2010-2020 period, I'd say the Houston Astros were the most dominant team in baseball. They won two World Series championships (2017 and 2019) and made the playoffs five times during that decade.\n\nTheir rebuild and subsequent rise to dominance was incredibly impressive, from tearing down the roster to build a strong farm system to making savvy trades and signings. They created a strong core of players like Jose Altuve, Carlos Correa, George Springer, and Justin Verlander, among others.\n\nThe Astros' ability to adapt and evolve their roster, combined with their strong organization and front office, allowed them to maintain a high level of success over the decade. They consistently ranked among the top teams in the American League, and their World Series titles cemented their status as one of the best teams of the decade.\n\nThe San Francisco Giants, who won three World Series titles during the 2010s (2010, 2012, and 2014), and the Kansas City Royals, who won the World Series in 2015 and made back-to-back World Series appearances, were also strong teams during this period. However, the Astros' sustained success and impressive roster construction give them the edge in my book.\n\nWhat do you think? Do you agree with my assessment, or do you think another team deserves consideration as the best of the 2010-2020 decade?"
        },
        {
            "role": "user",
            "content": "What do you think happened to make the New York Yankees loose their competitive edge from 2010 to 2020? "
        },
        {
            "role": "assistant",
            "content": "The New York Yankees' decline in competitiveness from 2010 to 2020 is a complex issue, but I'll try to break it down. Here are some key factors that contributed to their struggles:\n\n1. **Aging Core**: The Yankees' core players from their 2000s dynasty, such as Derek Jeter, Mariano Rivera, and Andy Pettitte, began to age and eventually retired. This left a void in leadership and production that was difficult to fill.\n2. **Injuries**: The Yankees suffered a rash of injuries to key players, including Alex Rodriguez, Mark Teixeira, and CC Sabathia, among others. These injuries not only cost them games but also led to a decline in overall team performance.\n3. **Failed Contracts**: The Yankees handed out some lucrative contracts during this period, such as the ones to A-Rod and Jacoby Ellsbury, which didn't quite pan out as expected. These deals limited their financial flexibility and created roster stagnation.\n4. **Farm System**: The Yankees' farm system, which was once a strength, experienced a downturn during this period. They didn't develop enough impact prospects to contribute to the major league team, leading to a reliance on free agency and trades.\n5. **Competitive Balance**: The American League East became increasingly competitive during the 2010s, with the rise of teams like the Tampa Bay Rays, Boston Red Sox, and Toronto Blue Jays. This made it harder for the Yankees to dominate the division as they had in the past.\n6. **Front Office Changes**: The Yankees experienced some significant front office changes, including the departure of longtime GM Brian Cashman's top deputies and the eventual replacement of Cashman himself. This led to a shift in organizational philosophy and decision-making.\n7. **Luxury Tax**: The Yankees' payroll consistently ranked among the highest in baseball, which led to luxury tax penalties. This made it more difficult for them to sign top free agents or make significant trades without exceeding the competitive balance tax threshold.\n\nThese factors combined to slow the Yankees' pace and make it challenging for them to regain their status as a dominant team. However, they've made some significant moves in recent years, including the hiring of Aaron Boone as manager and the signing of Gerrit Cole, to try and reinvigorate their competitive edge.\n\nWhat do you think about the Yankees' struggles during this period? Do you have any other theories about what might have contributed to their decline?"
        },
    ],
    temperature=1,
    max_completion_tokens=1024,
    top_p=1,
    stream=True,
    stop=None,
)

for chunk in completion:
    print(chunk.choices[0].delta.content or "", end="")

# prompt: Use the code above defining the completion stream object to code a chat interface with Groq (It should wait for the user to pass in text, and then respond to the user)

from groq import Groq

client = Groq(api_key="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")

def chat_with_groq():
    messages = [
        {
            "role": "system",
            "content": "You are a Sports Expert. You are talking to a user interested in sports. Feel free to converse freely with the user but the conversation must remain related to sports. If the user starts to steer the conversation to a topic not related to sports, YOU MUST REPLY WITH \"I'm sorry I am only able to discuss sports topics\"."
        },
        {
            "role": "user",
            "content": "Hi, so, you know some things about sports?"
        },
        {
            "role": "assistant",
            "content": "I'm a sports enthusiast and expert! I can talk about various sports, teams, players, and championships all day long! What's your favorite sport or team? Are you interested in discussing the latest news, scores, or analysis? Maybe you want to debate about who's the greatest of all time in a particular sport? Let's get the conversation started!"
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


