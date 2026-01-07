from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert
import os
from uuid import UUID

from repose.core.llm import LLMClient, Message
from repose.core.rag.chunking import ChunkingService
from repose.models.embedding import CodeEmbedding

class ContextEngine:
    """RAG engine for repository context."""
    
    def __init__(self, db: AsyncSession, llm_client: LLMClient):
        self.db = db
        self.llm = llm_client
        self.chunker = ChunkingService()
    
    async def index_repository(self, repo_id: UUID, repo_path: str):
        """
        Indexes a repository by walking files, chunking, and embedding.
        Assumes repo_path is a local path where repo is cloned.
        """
        # 1. Walk directory and collect files
        files_to_process = []
        for root, _, files in os.walk(repo_path):
            if ".git" in root:
                continue
            for file in files:
                # Basic filter for now
                if file.endswith(('.py', '.js', '.ts', '.tsx', '.md', '.go', '.rs')):
                    files_to_process.append(os.path.join(root, file))
        
        # 2. Process files
        all_chunks = []
        for file_path in files_to_process:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                rel_path = os.path.relpath(file_path, repo_path)
                chunks = self.chunker.chunk_file(rel_path, content)
                all_chunks.extend(chunks)
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
                continue
                
        if not all_chunks:
            return
            
        # 3. Generate embeddings (Batching)
        batch_size = 50
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i:i + batch_size]
            texts = [c.content for c in batch]
            
            try:
                embeddings = await self.llm.generate_embeddings(texts)
                
                # 4. Store in DB
                for chunk, embedding in zip(batch, embeddings):
                    stmt = insert(CodeEmbedding).values(
                        repo_id=repo_id,
                        file_path=chunk.file_path,
                        chunk_index=chunk.index,
                        chunk_hash=chunk.chunk_hash,
                        content=chunk.content,
                        embedding=embedding,
                        language=chunk.language,
                        start_line=chunk.start_line,
                        end_line=chunk.end_line
                    )
                    # On conflict (same file+index), update content/hash/embedding
                    stmt = stmt.on_conflict_do_update(
                        index_elements=['repo_id', 'file_path', 'chunk_index'],
                        set_={
                            'content': stmt.excluded.content,
                            'chunk_hash': stmt.excluded.chunk_hash,
                            'embedding': stmt.excluded.embedding,
                            'start_line': stmt.excluded.start_line,
                            'end_line': stmt.excluded.end_line
                        }
                    )
                    await self.db.execute(stmt)
                    
                await self.db.commit()
                
            except Exception as e:
                print(f"Error generating embeddings for batch: {e}")
                await self.db.rollback()

    async def retrieve_similar(self, repo_id: UUID, query: str, top_k: int = 5) -> list[CodeEmbedding]:
        """Find most relevant code chunks for a query."""
        query_embedding = await self.llm.generate_embedding(query)
        
        # Using PGVector's cosine distance (smaller is better)
        stmt = select(CodeEmbedding).filter(
            CodeEmbedding.repo_id == repo_id
        ).order_by(
            CodeEmbedding.embedding.cosine_distance(query_embedding)
        ).limit(top_k)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def query(self, repo_id: UUID, question: str) -> any:
        """
        End-to-end RAG query: 
        1. Retrieve context
        2. Construct prompt
        3. Stream answer from LLM
        """
        
        context_chunks = await self.retrieve_similar(repo_id, question, top_k=5)
        
        context_str = "\n\n".join([
            f"File: {c.file_path} (Lines {c.start_line}-{c.end_line}):\n{c.content}"
            for c in context_chunks
        ])
        
        system_prompt = """You are an expert software engineer assisting with a codebase.
Use the provided Context to answer the user's question. 
If the answer isn't in the context, say so, but try to be helpful based on general knowledge if appropriate, 
while strictly distinguishing between context-based facts and general assumptions.
Always cite the file paths when referencing code."""

        user_prompt = f"""Context:
{context_str}

Question:
{question}
"""
        
        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=user_prompt)
        ]
        
        # We return the generator to be streamed by the API
        return self.llm.stream_complete(messages), context_chunks
