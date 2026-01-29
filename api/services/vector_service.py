import time
from typing import List, Union
from pathlib import Path

from openai import OpenAI
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    WebBaseLoader,
)

from config import (
    OPENROUTER_API_HOST,
    OPENROUTER_API_KEY,
    BASE_EMBEDDING_MODEL,
)


class MultiSourceIngestor:
    def __init__(
        self,
        embed_model: str = BASE_EMBEDDING_MODEL,
        chunk_size: int = 800,
        chunk_overlap: int = 100,
        batch_size: int = 10,
        max_retries: int = 5,
        base_delay: float = 1.0,
    ):
        self.client = OpenAI(
            base_url=OPENROUTER_API_HOST,
            api_key=OPENROUTER_API_KEY,
            timeout=60,
        )

        self.embed_model = embed_model
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.base_delay = base_delay

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    # -------- loaders --------

    def load_pdf(self, path: Union[str, Path]) -> List[Document]:
        loader = PyPDFLoader(str(path))
        docs = loader.load()
        for d in docs:
            d.metadata["source"] = "pdf"
        return docs

    def load_web(self, url: str) -> List[Document]:
        loader = WebBaseLoader(url)
        docs = loader.load()
        for d in docs:
            d.metadata["source"] = "web"
            d.metadata["url"] = url
        return docs

    def load_raw_text(self, text: str, metadata: dict | None = None) -> List[Document]:
        meta = metadata or {}
        meta["source"] = "raw"
        return [Document(page_content=text, metadata=meta)]

    # -------- chunking --------

    def chunk_documents(self, docs: List[Document]) -> List[str]:
        chunks = self.splitter.split_documents(docs)
        return [c.page_content for c in chunks if c.page_content.strip()]

    # -------- embedding --------

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        vectors: List[List[float]] = []

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            vectors.extend(self._embed_with_retry(batch))

        return vectors

    def _embed_with_retry(self, batch: List[str]) -> List[List[float]]:
        for attempt in range(self.max_retries):
            try:
                res = self.client.embeddings.create(
                    model=self.embed_model,
                    input=batch,
                    extra_headers={
                        "HTTP-Referer": "farukseker.com.tr",
                        "X-Title": "farukseker",
                    },
                )
                return [d.embedding for d in res.data]

            except Exception:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(self.base_delay * (2 ** attempt))

    # -------- unified ingest --------

    def ingest(
        self,
        *,
        pdf_paths: List[Union[str, Path]] | None = None,
        urls: List[str] | None = None,
        raw_texts: List[str] | None = None,
    ) -> List[List[float]]:
        documents: List[Document] = []

        if pdf_paths:
            for p in pdf_paths:
                documents.extend(self.load_pdf(p))

        if urls:
            for u in urls:
                documents.extend(self.load_web(u))

        if raw_texts:
            for t in raw_texts:
                documents.extend(self.load_raw_text(t))

        texts = self.chunk_documents(documents)
        return self.embed_texts(texts)
