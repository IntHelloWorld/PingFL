from typing import Dict, List, Optional

import tiktoken

from core.prompt import SEARCH_AGENT_SYSTEM_PROMPT


class Memory:
    def __init__(self, system_prompt: str, model_name: str = "gpt-3.5-turbo"):
        self.messages: List[Dict] = []
        self.messages.append({"role": "system", "content": system_prompt})
        self.encoding = tiktoken.encoding_for_model(model_name)
    
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
