from abc import ABC, abstractmethod
import google.generativeai as genai
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
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-pro-latest")

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

