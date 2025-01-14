import json
from typing import Any, Dict, List, Optional

import openai
from openai.types.chat import ChatCompletion, ParsedChatCompletion


class LLMBackend:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key="sk-BaPj2TiMrz6RlaG1fXnEhjADjhrAQQGKpoAVfwMXfxfEq5EG",
            base_url="https://api.kksj.org/v1",
        )

    def call(self, **kwargs) -> ChatCompletion:
        try:
            response = self.client.chat.completions.create(**kwargs)
            return response
        except Exception as e:
            raise e
    
    def call_parse(self, **kwargs) -> ParsedChatCompletion:
        try:
            response = self.client.beta.chat.completions.parse(**kwargs)
            return response
        except Exception as e:
            raise e
