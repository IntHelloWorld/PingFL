from typing import Any, Dict

import anthropic
import openai
from openai.types.chat import ChatCompletion, ParsedChatCompletion
from tenacity import retry, stop_after_attempt, wait_exponential


class LLMBackend:
    def __init__(self, api_key: str, base_url: str):
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
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

class AnthropicBackend:
    def __init__(self, api_key: str, base_url: str):
        self.client = anthropic.Anthropic(
            api_key=api_key,
            base_url=base_url,
        )
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def call(self, **kwargs) -> Dict[str, Any]:
        try:
            response = self.client.messages.create(**kwargs)
            return response
        except Exception as e:
            raise e