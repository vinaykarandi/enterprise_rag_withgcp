
from typing import List
import logfire


def chunk_text(
    text: str,
    chunk_size: int = 800,
    overlap: int = 100,
) -> List[str]:
    """
    Split extracted PDF text into chunks with a strict
    character limit, including paragraphs longer than chunk_size.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and < chunk_size")

    with logfire.span("Text Chunking", text_length=len(text)):
        if not text or not text.strip():
            return []

        # Normalize whitespace and preserve paragraph boundaries.
        paragraphs = text.split("\n\n")
        chunks = []
        current = ""

        def split_long_text(value: str) -> List[str]:
            step = chunk_size - overlap
            return [
                value[i:i + chunk_size].strip()
                for i in range(0, len(value), step)
                if value[i:i + chunk_size].strip()
            ]

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            # Critical fix: split paragraphs that are too long.
            if len(paragraph) > chunk_size:
                if current.strip():
                    chunks.append(current.strip())
                    current = ""

                chunks.extend(split_long_text(paragraph))
                continue

            candidate = (
                f"{current}\n\n{paragraph}".strip()
                if current.strip()
                else paragraph
            )

            if len(candidate) <= chunk_size:
                current = candidate
            else:
                if current.strip():
                    chunks.append(current.strip())
                current = paragraph

        if current.strip():
            chunks.append(current.strip())

        # Defensive validation.
        chunks = [c for c in chunks if c]
        assert all(len(c) <= chunk_size for c in chunks)

        logfire.info(
            "Generated chunks",
            chunk_count=len(chunks),
            max_chunk_chars=max(map(len, chunks), default=0),
        )

        return chunks
