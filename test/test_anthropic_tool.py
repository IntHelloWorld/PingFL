import anthropic

client = anthropic.Anthropic(
    api_key="sk-Qi8J9Hejw2kkxVUFJ2iOPS0G8Zekp8jZjQUvl4RMekDlP1OB",
    base_url="https://api.key77qiqi.cn",
)

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=[
        {
            "name": "get_weather",
            "description": "Get the current weather in a given location",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    }
                },
                "required": ["location"],
            },
        }
    ],
    messages=[
        {
            "role": "user",
            "content": "What's the weather like in San Francisco?",
        }
    ],
    # messages=[
    #     {
    #         "role": "user",
    #         "content": "Who are you?",
    #     }
    # ],
)
print(response)
