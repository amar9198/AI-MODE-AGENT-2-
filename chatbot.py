from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

model = ChatGroq(model="openai/gpt-oss-120b",temperature=0.9)

print("choose your AI mode")
print("press 1 for Angry mode")
print("press 2 for funny mode")
print("press 3 for sad mode")

choice = int(input("Enter your choice: "))

if choice ==1:
    mode = "You are an angry AI agent. You respond aggressively and impatiently"
elif choice ==2:
    mode = "You are very funny AI agent. You respond with humor and jokes"
elif choice ==3:
    mode = "You are a sad AI agent. You respond with sad mode and emotions"
    

messages = [
    SystemMessage(content=mode)

]

print("-----------------Welcome type 0 to exit the application-----------------")
while True:
    
    prompt = input("You : ")
    messages.append(HumanMessage(content=prompt))
    if prompt == "0":                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
        break                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        

    response = model.invoke(messages)
    messages.append(AIMessage(content=response.content))

    print("Bot :", response.content)

print(messages)    