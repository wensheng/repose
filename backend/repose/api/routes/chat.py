from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from uuid import UUID
from typing import List

from repose.api import deps
from repose.core.config import settings
from repose.core.llm import create_llm_client, LLMConfig
from repose.core.rag.context_engine import ContextEngine

router = APIRouter()


class ChatRequest(BaseModel):
    repo_id: UUID
    message: str


@router.post("/query")
async def chat_query(
    request: ChatRequest,
    db: AsyncSession = Depends(deps.get_db),
):
    # Initialize LLM Client
    # In prod, this might be a singleton or cached
    llm_config = LLMConfig(
        provider="gemini",
        model="gemini-2.5-flash", # user specified placeholder or preference
        api_key=settings.GEMINI_API_KEY
    )
    llm_client = create_llm_client(llm_config)
    
    context_engine = ContextEngine(db, llm_client)
    
    try:
        stream_gen, sources = await context_engine.query(request.repo_id, request.message)
    except Exception as e:
        # Log error
        print(f"RAG Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    async def response_generator():
        # First send sources as a special event or just pure text?
        # For simple streaming, we might just append sources at the end or send JSON chunks.
        # Let's send a JSON chunk for sources first, then text chunks.
        # But standard formatting makes handling mixed types hard for simple clients.
        # Let's just stream text for now, and maybe format sources at the end.
        
        yield f"**Sources:**\n"
        for s in sources:
            yield f"- `{s.file_path}` ({s.start_line}-{s.end_line})\n"
        yield "\n---\n"
        
        async for chunk in stream_gen:
            yield chunk

    return StreamingResponse(response_generator(), media_type="text/plain")
