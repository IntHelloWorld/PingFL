from openai import OpenAI


def send_messages(messages):
    response = client.chat.completions.create(
        model="deepseek-chat", messages=messages, tools=tools
    )
    return response.choices[0].message


client = OpenAI(
    api_key="sk-666cc3eea6ca4464ad9793b2c77927df",
    base_url="https://api.deepseek.com/v1",
)

# client = OpenAI(
#     api_key="sk-HQQnwdTRf7YmbXqXNtRFonUGODg8sCCEkkohttYlYV0629ab",
#     base_url="https://api.key77qiqi.cn/v1",
# )

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather_of_Hangzhou",
            "description": "Get weather of Hangzhou",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        },
    },
]

messages = [
    {
        "role": "system",
        "content": "You are an AI assistant. You can answer questions about the weather. You can use the `get_weather` function to get the weather of a location. Please contain your thoughts in the argument of each function you initiate.",
    },
    {"role": "user", "content": "How's the weather in Hangzhou?"},
]
message = send_messages(messages)
print(f"User>\t {messages[0]['content']}")

tool = message.tool_calls[0]
print(tool)
messages.append(message)

messages.append({"role": "tool", "tool_call_id": tool.id, "content": "24℃"})
message = send_messages(messages)
print(f"Model>\t {message.content}")
