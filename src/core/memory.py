from typing import Dict, List, Optional

import tiktoken
from openai.types.chat import ChatCompletionMessage, ChatCompletionMessageToolCall

PRICE_PER_MILLION_TOKENS = {
    "gpt-3.5-turbo": (0.5, 1.5),
    "gpt-4": (30, 60),
    "gpt-4o-2024-11-20": (2.5, 10),
    "gpt-4-turbo-2024-04-09": (10, 30),
    "gpt-4-0125-preview": (10, 30),
    "claude-3-5-sonnet-20241022": (3, 15),
}

class Memory:
    def __init__(self, system_prompt: str, model_name: str = "gpt-4o-2024-11-20"):
        self.messages: List[Dict] = []
        self.messages.append({"role": "system", "content": system_prompt})
        self.retry_msg_idx = []
        self.encoding = tiktoken.encoding_for_model("gpt-4o-2024-11-20")
        self.model_name = model_name
    
    def add_message(self, message):
        self.messages.append(message)
    
    def get_messages(self) -> List[Dict]:
        """
            Get all messages, remove previous retry messages
            except the last two retry messages to save cost.
        """
        messages = []
        useless_msg_idx = []
        if len(self.retry_msg_idx) > 2:
            useless_msg_idx = self.retry_msg_idx[:-2]
        for i, msg in enumerate(self.messages):
            if i not in useless_msg_idx:
                messages.append(msg)
        return messages

    def clear(self):
        self.messages = []

    def serialize(self) -> str:
        messages = []
        all_in_tokens = 0
        all_out_tokens = 0
        
        message_tokens = []
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
                tokens = sum(
                    [self.get_tool_call_tokens(toolcall) for toolcall in message.tool_calls]
                )
                message_tokens.append(tokens)
            else:
                messages.append(message)
                message_tokens.append(len(self.encoding.encode(message["content"])))
        
        # Calculate cost
        costs = []
        for i in range(2, len(message_tokens), 2):
            in_tokens = sum(message_tokens[:i])
            out_tokens = message_tokens[i]
            all_in_tokens += in_tokens
            all_out_tokens += out_tokens
            costs.append(
                self.in_tokens_cost(in_tokens) +
                self.out_tokens_cost(out_tokens)
            )

        return {
            "messages": messages,
            "all_in_tokens": all_in_tokens,
            "all_out_tokens": all_out_tokens,
            "money": sum(costs),
        }
    
    def get_tool_call_tokens(self, tool_call: ChatCompletionMessageToolCall) -> int:
        return (
            len(self.encoding.encode(tool_call.function.name)) +
            len(self.encoding.encode(tool_call.function.arguments))
        )
    
    def in_tokens_cost(self, tokens: int):
        return tokens / 1000000 * PRICE_PER_MILLION_TOKENS[self.model_name][0]
    
    def out_tokens_cost(self, tokens: int):
        return tokens / 1000000 * PRICE_PER_MILLION_TOKENS[self.model_name][1]