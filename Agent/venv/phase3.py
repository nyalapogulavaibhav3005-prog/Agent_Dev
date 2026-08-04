import os
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime
import json

#making some basic tools 
def get_current_date_time():
    return datetime.now()
    
def length_converter(val, from_unit, to_unit):
    # Convert everything to meters first (Base unit)
    to_meters = {"m": 1.0, "km": 1000.0, "cm": 0.01, "mm": 0.001, "mile": 1609.34, "inch": 0.0254}
    
    if from_unit in to_meters and to_unit in to_meters:
        meters = val * to_meters[from_unit]
        return meters / to_meters[to_unit]
    return None

def weight_converter(val, from_unit, to_unit):
    # Convert everything to grams first (Base unit)
    to_grams = {"g": 1.0, "kg": 1000.0, "mg": 0.001, "lb": 453.592, "oz": 28.3495}
    
    if from_unit in to_grams and to_unit in to_grams:
        grams = val * to_grams[from_unit]
        return grams / to_grams[to_unit]
    return None

def temp_converter(val, from_unit, to_unit):
    if from_unit == to_unit:
        return val
    # Convert to Celsius first
    if from_unit == "c":
        celsius = val
    elif from_unit == "f":
        celsius = (val - 32) * 5/9
    elif from_unit == "k":
        celsius = val - 273.15
    else:
        return None
        
    # Convert Celsius to destination unit
    if to_unit == "c":
        return celsius
    elif to_unit == "f":
        return (celsius * 9/5) + 32
    elif to_unit == "k":
        return celsius + 273.15
    return None




get_current_date_time_Schema={
    "type":"function",
    "function":{
        "name":"get_current_date_time",
        "description":"Returns the current date and time. Use this when the user asks what day, date, or time it currently is",
        "parameters":{
            "type":"object",
            "properties":{},
            "required":[]
    }
 }
}

length_converter_schema={
    "type":"function",
    "function":{
        "name":"length_converter",
        "description":" Converts a length measurement from one unit to another (e.g. meters to miles). ",
        "parameters":{
            "type":"object",
            "properties":{
                "val":{
                    "type":"number",
                    "description":"The value which should be converted",   
                },
                "from_unit":{
                    "type":"string",
                    "enum":["m","km","cm","mm","mile","inch"],
                    "description":"the unit which we should convert from",
                },
                "to_unit":{
                    "type":"string",
                    "enum":["m","km","cm","mm","mile","inch"],
                    "description":"the unit which we shoulf convert the val to from the from_unit"
                }
            },
        "required":["val","from_unit","to_unit"]
        }
    }
}


weight_converter_schema={
    "type":"function",
    "function":{
        "name":"weight_converter",
        "description":" Converts a weight measurement from one unit to another (e.g. g to kgs). ",
        "parameters":{
            "type":"object",
            "properties":{
                "val":{
                    "type":"number",
                    "description":"The value which should be converted",   
                },
                "from_unit":{
                    "type":"string",
                    "enum":["g","kg","mg","lb","oz"],
                    "description":"the unit which we should convert from",
                },
                "to_unit":{
                    "type":"string",
                    "enum":["g","kg","mg","lb","oz"],
                    "description":"the unit which we shoulf convert the val to from the from_unit"
                }
            },
        "required":["val","from_unit","to_unit"]
        }
    }
}

temp_converter_schema={
    "type":"function",
    "function":{
        "name":"temp_converter",
        "description":" Converts a temperature measurement from one unit to another (e.g. c to f). ",
        "parameters":{
            "type":"object",
            "properties":{
                "val":{
                    "type":"number",
                    "description":"The value which should be converted",   
                },
                "from_unit":{
                    "type":"string",
                    "enum":["c","f","k"],
                    "description":"the unit which we should convert from",
                },
                "to_unit":{
                    "type":"string",
                    "enum":["c","f","k"],
                    "description":"the unit which we shoulf convert the val to from the from_unit"
                }
            },
        "required":["val","from_unit","to_unit"]
        }
    }
}
tools=[
    get_current_date_time_Schema,
    length_converter_schema,
    weight_converter_schema,
    temp_converter_schema
]

tool_functions={
    "get_current_date_time":get_current_date_time,
    "length_converter":length_converter,
    "weight_converter":weight_converter,
    "temp_converter":temp_converter
}


load_dotenv()
api_key=os.getenv("GROQ_API_KEY")
client=Groq(api_key=api_key)

class conversationManager:
    def __init__(self,system_prompt):
        self.system_prompt=system_prompt
        self.messages=[{"role":"system","content":system_prompt}]
    
    def add_user_message(self , msg):
        self.messages.append({"role":"user","content":msg})

    def get_response(self,c=0):
        message=client.chat.completions.create(
        messages=self.messages,
        model="llama-3.3-70b-versatile",
        tools=tools,
        tool_choice="auto"
        )
        api_reply=message.choices[0].message
        if c>=2:
            return api_reply.content
        if not message.choices[0].message.tool_calls:
            self.messages.append({"role":"assistant","content":api_reply.content,"tool_calls":api_reply.tool_calls})
            return api_reply.content
        else:
            full_message=api_reply.model_dump()
            cleaned_message={
                "role":"assistant",
                "content":full_message["content"],
                "tool_calls":full_message["tool_calls"]
            }
            self.messages.append(cleaned_message)
            for tool_call in api_reply.tool_calls:
                tool_id=tool_call.id 
                function_name=tool_call.function.name
                arguments=json.loads(tool_call.function.arguments)
                func=tool_functions[function_name]
                response=func(**arguments)
                self.messages.append({"role":"tool","tool_call_id":tool_id,"content":str(response)})
            return self.get_response(c+1)

    def chat(self,inp):
        self.add_user_message(inp)
        return self.get_response()
    
    def clear(self):
        self.messages=[{"role":"system","content":self.system_prompt}]
    
    def get_history(self):
        return (self.messages)
manager=conversationManager("you are my assistant and you need to call the tools which i make you to call, okay ?")
print(manager.chat("convert 100km to cm?"))