from dataclasses import dataclass
import hashlib

@dataclass
class Chunk:
    content: str
    file_path: str
    index: int
    start_line: int
    end_line: int
    language: str
    chunk_hash: str

class ChunkingService:
    """Service to split source code into meaningful chunks."""
    
    def __init__(self, chunk_size: int = 2000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_file(self, file_path: str, content: str) -> list[Chunk]:
        """
        Splits file content into chunks. 
        For now, implementing a simple character/line-based splitting.
        Future: Use tree-sitter or language-specific parsers.
        """
        lines = content.splitlines()
        chunks = []
        current_chunk_lines = []
        current_size = 0
        start_line = 1
        chunk_idx = 0
        
        language = self._get_language(file_path)

        for i, line in enumerate(lines):
            line_len = len(line) + 1 # +1 for newline
            
            if current_size + line_len > self.chunk_size and current_chunk_lines:
                # Flush current chunk
                chunk_text = "\n".join(current_chunk_lines)
                end_line = start_line + len(current_chunk_lines) - 1
                
                chunks.append(Chunk(
                    content=chunk_text,
                    file_path=file_path,
                    index=chunk_idx,
                    start_line=start_line,
                    end_line=end_line,
                    language=language,
                    chunk_hash=self._hash_text(chunk_text)
                ))
                
                # Start new chunk with overlap
                # Simple logic: keep last N lines that fit inside overlap size
                overlap_lines = []
                overlap_size = 0
                for l in reversed(current_chunk_lines):
                    if overlap_size + len(l) + 1 <= self.chunk_overlap:
                        overlap_lines.insert(0, l)
                        overlap_size += len(l) + 1
                    else:
                        break
                
                current_chunk_lines = overlap_lines
                current_size = overlap_size
                start_line = (i + 1) - len(current_chunk_lines) + 1
                chunk_idx += 1
            
            current_chunk_lines.append(line)
            current_size += line_len
            
        # Flush last chunk
        if current_chunk_lines:
            chunk_text = "\n".join(current_chunk_lines)
            end_line = start_line + len(current_chunk_lines) - 1
            chunks.append(Chunk(
                content=chunk_text,
                file_path=file_path,
                index=chunk_idx,
                start_line=start_line,
                end_line=end_line,
                language=language,
                chunk_hash=self._hash_text(chunk_text)
            ))
            
        return chunks

    def _get_language(self, file_path: str) -> str:
        ext = file_path.split('.')[-1].lower() if '.' in file_path else ""
        map = {
            "py": "python", "js": "javascript", "ts": "typescript", 
            "tsx": "typescript", "jsx": "javascript", "rs": "rust", 
            "go": "go", "md": "markdown", "java": "java", "c": "c", "cpp": "cpp"
        }
        return map.get(ext, "text")

    def _hash_text(self, text: str) -> str:
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
