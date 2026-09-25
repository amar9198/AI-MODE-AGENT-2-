from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

model = ChatGroq(
    model="openai/gpt-oss-120b",temperature=0,max_tokens=20
)

response = model.invoke(
    "write a poem on AI."
)

print(response.content)