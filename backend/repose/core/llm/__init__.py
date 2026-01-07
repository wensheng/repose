from .base import LLMClient, LLMConfig, Message
from .gemini import GeminiClient

def create_llm_client(config: LLMConfig) -> LLMClient:
    """Factory function to create appropriate LLM client."""
    clients = {
        "gemini": GeminiClient,
        # "openai": OpenAIClient,
        # "anthropic": AnthropicClient,
    }
    
    client_class = clients.get(config.provider)
    if not client_class:
        raise ValueError(f"Unknown LLM provider: {config.provider}")
    
    return client_class(config)
