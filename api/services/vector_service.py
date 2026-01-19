from typing import List, Union
from pathlib import Path
from config import OPENROUTER_API_HOST, OPENROUTER_API_KEY
from openai import OpenAI
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    WebBaseLoader,
)


class MultiSourceIngestor:
    def __init__(
        self,
        embed_model: str = "text-embedding-3-large",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        self.client = OpenAI(
            base_url=OPENROUTER_API_HOST,
            api_key=OPENROUTER_API_KEY,
        )

        self.embed_model = embed_model

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    # ---- Loaders ----

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

    # ---- Chunking ----

    def chunk_documents(self, docs: List[Document]) -> List[str]:
        chunks = self.splitter.split_documents(docs)
        return [c.page_content for c in chunks]

    # ---- Embedding ----

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(
            model=self.embed_model,
            input=texts,
            # encoding_format="float",
            extra_headers={
                "HTTP-Referer": "farukseker.com.tr",
                "X-Title": "farukseker",
            }
        )
        return [item.embedding for item in response.data]

    # ---- Unified ingest ----

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
