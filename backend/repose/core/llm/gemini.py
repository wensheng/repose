from typing import AsyncIterator, Optional, Any
import google.genai as genai
from google.genai import types

from .base import LLMClient, LLMConfig, Message, CompletionResult, CODE_EMBED_DIM

class GeminiClient(LLMClient):
    """Google Gemini implementation using google-genai SDK."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = genai.Client(api_key=config.api_key)
        self.model = config.model
        self.embed_model = "gemini-embedding-001"
    
    def _format_messages(self, messages: list[Message]) -> list:
        # Convert to Gemini format
        formatted = []
        for m in messages:
            role = m.role
            # Map standard roles to Gemini roles if needed
            if role == "system":
                # System instructions are passed differently in some APIs, 
                # but for simplicity treating as user or model in context often works,
                # or strictly separate system instructions config.
                # Here we map system -> user for simple compat or use system_instruction in config
                # For this implementation, let's keep it simple:
                pass 
            formatted.append({"role": role, "parts": [{"text": m.content}]})
        return formatted

    def _convert_response(self, response: Any) -> CompletionResult:
        # Extract content
        content = ""
        if response.text:
            content = response.text
            
        # Extract tool calls (if any)
        tool_calls = None
        # TODO: Implement tool call extraction logic based on response structure
            
        usage = None
        if hasattr(response, "usage_metadata"):
             usage = {
                 "input_tokens": response.usage_metadata.prompt_token_count,
                 "output_tokens": response.usage_metadata.candidates_token_count,
                 "total_tokens": response.usage_metadata.total_token_count,
             }

        return CompletionResult(content=content, tool_calls=tool_calls, usage=usage)

    async def complete(
        self,
        messages: list[Message],
        tools: Optional[list[dict]] = None
    ) -> CompletionResult:
        
        # separate system message if exist
        system_instruction = None
        contents = []
        for m in messages:
            if m.role == "system":
                system_instruction = m.content
            else:
                 contents.append(types.Content(
                     role="user" if m.role == "user" else "model",
                     parts=[types.Part.from_text(text=m.content)]
                 ))

        # Config
        config = types.GenerateContentConfig(
            temperature=self.config.temperature,
            max_output_tokens=self.config.max_tokens,
            system_instruction=system_instruction
        )
        
        # Tools configuration if provided (simplified)
        if tools:
             # TODO: Map generic tools dict to Gemini Tool types
             pass

        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=contents,
            config=config,
        )
        
        return self._convert_response(response)
    
    async def stream_complete(
        self,
        messages: list[Message],
        tools: Optional[list[dict]] = None
    ) -> AsyncIterator[str]:
        
        # Similar setup to complete
        system_instruction = None
        contents = []
        for m in messages:
            if m.role == "system":
                system_instruction = m.content
            else:
                 contents.append(types.Content(
                     role="user" if m.role == "user" else "model",
                     parts=[types.Part.from_text(text=m.content)]
                 ))
                 
        config = types.GenerateContentConfig(
            temperature=self.config.temperature,
            max_output_tokens=self.config.max_tokens,
            system_instruction=system_instruction
        )
        
        async for chunk in await self.client.aio.models.generate_content_stream(
            model=self.model,
            contents=contents,
            config=config
        ):
            if chunk.text:
                yield chunk.text
    
    async def generate_embedding(self, text: str) -> list[float]:
        result = await self.client.aio.models.embed_content(
            model=self.embed_model,
            config=types.EmbedContentConfig(output_dimensionality=CODE_EMBED_DIM),
            contents=text
        )
        return result.embeddings[0].values
    
    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        # Batch embedding requests
        # Note: Check API limits for batch size, often 100 or so
        results = []
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            result = await self.client.aio.models.embed_content(
                model=self.embed_model,
                config=types.EmbedContentConfig(output_dimensionality=CODE_EMBED_DIM),
                contents=batch
            )
            # result.embeddings is a list of ContentEmbedding
            results.extend([e.values for e in result.embeddings])
        return results
