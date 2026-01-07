from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Optional
from dataclasses import dataclass

CODE_EMBED_DIM = 1536

@dataclass
class LLMConfig:
    provider: str  # "gemini", "openai", "anthropic"
    model: str
    api_key: str
    temperature: float = 0.7
    max_tokens: int = 4096

@dataclass  
class Message:
    role: str  # "system", "user", "assistant"
    content: str

@dataclass
class ToolCall:
    name: str
    arguments: dict[str, Any]

@dataclass
class CompletionResult:
    content: str
    tool_calls: Optional[list[ToolCall]] = None
    usage: Optional[dict[str, int]] = None


class LLMClient(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
    
    @abstractmethod
    async def complete(
        self, 
        messages: list[Message],
        tools: Optional[list[dict]] = None
    ) -> CompletionResult:
        """Generate a completion."""
        pass
    
    @abstractmethod
    async def stream_complete(
        self,
        messages: list[Message],
        tools: Optional[list[dict]] = None
    ) -> AsyncIterator[str]:
        """Stream a completion token by token."""
        pass
    
    @abstractmethod
    async def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        pass
    
    @abstractmethod
    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts (batched)."""
        pass
