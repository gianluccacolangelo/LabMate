from abc import ABC, abstractmethod


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
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-pro-latest")

    def generate_query(self, prompt: str) -> str:
        # Placeholder for actual Gemini API call
        return self.model.generate_content(prompt).text

