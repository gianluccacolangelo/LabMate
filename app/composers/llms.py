from abc import ABC, abstractmethod
import google.generativeai as genai
from google.generativeai import GenerationConfig
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core.exceptions import ResourceExhausted
from transformers import AutoModelForCausalLM, AutoTokenizer
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

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

class HuggingFaceProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: str = "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF"):
        # Initialize Hugging Face model and tokenizer
        self.api_key = api_key  # Unused but kept for consistency
        self.model_name = model_name
        self._setup_model()

    def _setup_model(self):
        """Private method to load the model and tokenizer."""
        print(f"Loading model: {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.bfloat16,
            device_map="auto"
        )
        print("Model loaded successfully.")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=1, max=10),
        retry=retry_if_exception_type(ResourceExhausted),
        reraise=True
    )
    def generate_query(self, prompt: str) -> str:
        """Generates a response from the model."""
        try:
            print(f"Generating response for prompt: {prompt}")

            # Tokenize the prompt
            inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda")

            # Generate a response
            outputs = self.model.generate(
                inputs["input_ids"],
                max_new_tokens=100,
                pad_token_id=self.tokenizer.eos_token_id
            )

            # Decode the response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response

        except ResourceExhausted as e:
            print(f"Resource exhausted. Retrying... (Error: {e})")
            raise


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_query(self, user_interest: str, platform: str) -> str:
        # Placeholder for actual Anthropic API call
        return f"Anthropic generated query for {user_interest} on {platform}"


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash", temperature: float = 0.0):
        genai.configure(api_key=api_key)
        self.model_name = model_name
        self.temperature = temperature
        
        # Create GenerationConfig with temperature
        generation_config = GenerationConfig(temperature=self.temperature)
        
        # Initialize the model with the generation config
        self.model = genai.GenerativeModel(model_name=model_name, generation_config=generation_config)
        
        self.model_info = genai.get_model(f"models/{model_name}")
        
        # Print model name, temperature, and token limits
        print(f"Model: {model_name}")
        print(f"Temperature: {temperature}")
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


class LLMFactory:
    @staticmethod
    def create_provider(provider_type: str, api_key: str, **kwargs) -> LLMProvider:
        if provider_type.lower() == "openai":
            return OpenAIProvider(api_key)
        elif provider_type.lower() == "huggingface":
            model_name = kwargs.get("model_name", "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF")
            return HuggingFaceProvider(api_key, model_name)
        elif provider_type.lower() == "anthropic":
            return AnthropicProvider(api_key)
        elif provider_type.lower() == "gemini":
            model_name = kwargs.get("model_name", "gemini-1.5-flash")
            temperature = kwargs.get("temperature", 0.0)
            return GeminiProvider(api_key, model_name, temperature)
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")
