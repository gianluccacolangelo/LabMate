from abc import ABC, abstractmethod
import google.generativeai as genai
from google.generativeai import GenerationConfig
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core.exceptions import ResourceExhausted


class LLMProvider(ABC):
    @abstractmethod
    def __init__(self, api_key: str):
        pass

    @abstractmethod
    def generate_query(self, user_interest: str, platform: str) -> str:
        pass


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_query(self, user_interest: str, platform: str) -> str:
        # Placeholder for actual OpenAI API call
        return f"OpenAI generated query for {user_interest} on {platform}"


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_query(self, user_interest: str, platform: str) -> str:
        # Placeholder for actual Anthropic API call
        return f"Anthropic generated query for {user_interest} on {platform}"


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        genai.configure(api_key=api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        self.model_info = genai.get_model(f"models/{model_name}")
        
        # Print model name and token limits
        print(f"Model: {model_name}")
        print(f"Input token limit: {self.model_info.input_token_limit}")
        print(f"Output token limit: {self.model_info.output_token_limit}")

    @retry(
        stop=stop_after_attempt(15),
        wait=wait_exponential(multiplier=2, min=4, max=10),
        retry=retry_if_exception_type(ResourceExhausted),
        reraise=True
    )
    def generate_query(self, prompt: str) -> str:
        try:
            return self.model.generate_content(prompt).text
        except ResourceExhausted as e:
            print(f"Rate limit exceeded. Retrying... (Error: {e})")
            raise
