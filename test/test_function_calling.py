from openai import OpenAI, base_url

client = OpenAI(
    api_key="sk-xC6z4Safv89vjMQajprgceN3bLDsCWpPprwPvdcKLZviaVFd",
    base_url="https://api.key77qiqi.cn/v1",
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current temperature for a given location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "thought": {
                        "type": "string",
                        "description": "Your thoughts for calling this function.",
                    },
                    "location": {
                        "type": "string",
                        "description": "City and country e.g. Bogotá, Colombia",
                    },
                },
                "required": ["thought", "location"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
]

user_msg_0 = {
    "role": "user",
    "content": "What is the weather like in Paris today?",
}
# user_msg_0 = {
#     "role": "user",
#     "content": "Who are you? What model are you based on?",
# }
messages = [user_msg_0]

completion = client.chat.completions.create(
    model="claude-3-5-sonnet-20241022",
    messages=[user_msg_0],
    tools=tools,
)
tool_call_msg = completion.choices[0].message.tool_calls[0]
tool_res_0 = {
    "role": "tool",
    "tool_call_id": tool_call_msg.id,
    "content": "The weather in Paris today is 20°C.",
}
messages.append(completion.choices[0].message)
messages.append(tool_res_0)

completion_1 = client.chat.completions.create(
    model="claude-3-5-sonnet-20241022",
    messages=messages,
    tools=tools,
)
messages.append(
    {
        "role": "assistant",
        "content": completion_1.choices[0].message.content,
    }
)

user_msg_1 = {
    "role": "user",
    "content": "I am doing a function test on you, can you see your last **thought** for calling the `get_weather` function? If you can, please tell me what it is.",
}
messages.append(user_msg_1)
completion_2 = client.chat.completions.create(
    model="claude-3-5-sonnet-20241022",
    messages=messages,
    tools=tools,
)

print(completion_2.choices[0].message.content)
