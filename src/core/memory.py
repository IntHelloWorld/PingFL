from typing import Dict, List, Optional

import tiktoken
from openai.types.chat import ChatCompletionMessage, ChatCompletionMessageToolCall

PRICE_PER_MILLION_TOKENS = {
    "gpt-3.5-turbo": (0.0006, 0.0006),
    "gpt-4": (0.0006, 0.0006),
    "gpt-4o-2024-11-20": (2.5, 10),
}

class Memory:
    def __init__(self, system_prompt: str, model_name: str = "gpt-4o-2024-11-20"):
        self.messages: List[Dict] = []
        self.messages.append({"role": "system", "content": system_prompt})
        self.encoding = tiktoken.encoding_for_model(model_name)
        self.model_name = model_name
    
    def add_message(self, message):
        self.messages.append(message)
    
    def get_messages(self) -> List[Dict]:
        return self.messages

    def clear(self):
        self.messages = []
    
    def get_token_count(self) -> int:
        total_tokens = 0
        for message in self.messages:
            total_tokens += len(self.encoding.encode(message["content"]))
        return total_tokens
    
    def get_tool_call_tokens(self, tool_call: ChatCompletionMessageToolCall) -> int:
        return (
            len(self.encoding.encode(tool_call.function.name)) +
            len(self.encoding.encode(tool_call.function.arguments))
        )

    def serialize(self) -> str:
        messages = []
        in_tokens = 0
        out_tokens = 0
        money = 0
        for message in self.messages:
            if isinstance(message, ChatCompletionMessage):
                messages.append(
                    {
                        "role": message.role,
                        "tool_calls": [
                            toolcall.model_dump_json() for toolcall in message.tool_calls
                        ],
                    }
                )
                out_tokens += sum(
                    [self.get_tool_call_tokens(toolcall) for toolcall in message.tool_calls]
                )
            else:
                messages.append(message)
                if message["role"] == "assistant":
                    out_tokens += len(self.encoding.encode(message["content"]))
                else:
                    in_tokens += len(self.encoding.encode(message["content"]))
        money = (
            in_tokens / 1000000 * PRICE_PER_MILLION_TOKENS[self.model_name][0] +
            out_tokens / 1000000 * PRICE_PER_MILLION_TOKENS[self.model_name][1]
        )
        return {
            "messages": messages,
            "in_tokens": in_tokens,
            "out_tokens": out_tokens,
            "money": money,
        }