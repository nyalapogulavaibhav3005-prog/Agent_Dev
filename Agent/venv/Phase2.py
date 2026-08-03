import os
from groq import Groq
from dotenv import load_dotenv


load_dotenv()
api_key=os.getenv("GROQ_API_KEY")
client=Groq(api_key=api_key)
   
class conversationManager:
    def __init__(self,system_prompt):
        self.system_prompt=system_prompt
        self.messages=[{"role":"system","content":system_prompt}]
    
    def add_user_message(self , msg):
        self.messages.append({"role":"user","content":msg})

    def get_response(self):
        message=client.chat.completions.create(
        messages=self.messages,
        model="llama-3.3-70b-versatile",
        )
        reply_text=message.choices[0].message.content
        self.messages.append({"role":"assistant","content":reply_text})
        return reply_text

    def chat(self,inp):
        self.add_user_message(inp)
        return self.get_response()
    
    def clear(self):
        self.messages=[{"role":"system","content":self.system_prompt}]
    
    def get_history(self):
        return (self.messages)
manage=conversationManager("You are my buddy")
print(manage.chat("Hey buddy , remember my name is alan"))
print(manage.get_history())
print(manage.chat("do you remember my name ?"))
