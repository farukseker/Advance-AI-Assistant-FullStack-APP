from typing import List, Dict, Optional, Tuple
from pathlib import Path
import tempfile
import uuid
import numpy as np
from openai import OpenAI

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from services import MultiSourceIngestor, QdrantStorage
from config import OPENROUTER_API_KEY, OPENROUTER_API_HOST, DEFAULT_MODEL


class DocumentProcessor:
    def __init__(self, ingestor: MultiSourceIngestor):
        self.ingestor = ingestor
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
        )

    def stream_pdf_chunks(
        self,
        content: bytes,
        filename: str,
    ):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(content)
            pdf_path = tmp.name

        try:
            loader = PyPDFLoader(pdf_path)

            for page_doc in loader.lazy_load():
                if not page_doc.page_content.strip():
                    continue

                chunks = self.splitter.split_documents([page_doc])
                texts = [c.page_content for c in chunks if c.page_content.strip()]

                if not texts:
                    continue

                embeddings = self.ingestor.embed_texts(texts)

                yield texts, embeddings, page_doc.metadata.get("page")

        finally:
            Path(pdf_path).unlink(missing_ok=True)

    def process_small_file(
        self,
        content: bytes,
        filename: str,
    ) -> Tuple[List[str], List[List[float]]]:
        ext = Path(filename).suffix.lower()

        if ext == ".pdf":
            docs = self._load_pdf(content)
        elif ext in {".txt", ".md"}:
            docs = self._load_text(content, filename)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        chunks = [
            d.page_content
            for d in self.splitter.split_documents(docs)
            if d.page_content.strip()
        ]

        embeddings = self.ingestor.embed_texts(chunks)
        return chunks, embeddings

class VectorSearchEngine:
    def __init__(self, ingestor: MultiSourceIngestor):
        self.ingestor = ingestor

    def search_in_memory(
            self,
            query: str,
            chunks: List[str],
            embeddings: List[List[float]],
            top_k: int = 3
    ) -> List[str]:
        query_embedding = self.ingestor.embed_texts([query])[0]

        scores = [
            (i, self._cosine(query_embedding, emb))
            for i, emb in enumerate(embeddings)
        ]

        scores.sort(key=lambda x: x[1], reverse=True)
        return [chunks[i] for i, _ in scores[:top_k]]

    def search_in_database(
            self,
            query: str,
            vector_db: QdrantStorage,
            top_k: int = 3,
            filename: Optional[str] = None
    ) -> Dict[str, any]:
        query_embedding = self.ingestor.embed_texts([query])[0]
        return vector_db.search(
            query_vector=query_embedding,
            top_k=top_k,
            filename=filename
        )

    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


class LLMQueryEngine:
    def __init__(self, model: str = DEFAULT_MODEL):
        self.client = OpenAI(
            base_url=OPENROUTER_API_HOST,
            api_key=OPENROUTER_API_KEY,
        )
        self.model = model

    def generate_answer(
            self,
            question: str,
            contexts: List[str],
            sources: Optional[List[str]] = None
    ) -> str:
        if not contexts:
            return "No relevant information found."

        context_text = "\n\n".join(
            f"[Chunk {i + 1}]\n{c}" for i, c in enumerate(contexts)
        )

        source_info = f"\nSources: {', '.join(sources)}" if sources else ""

        prompt = f"""Answer the question using only the information below.
If the answer is not present, say so explicitly.
You may respond in any language.

Documents:
{context_text}
{source_info}

Question: {question}

Answer:
"""

        res = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            extra_headers={
                "HTTP-Referer": "farukseker.com.tr",
                "X-Title": "farukseker",
            }
        )

        return res.choices[0].message.content


class RAGService:
    """RAG Service for document processing and question answering."""

    TEMP_COLLECTION_NAME = "temp-collection"

    def __init__(self):
        self.ingestor = MultiSourceIngestor()
        self.vector_db = QdrantStorage()
        self.doc_processor = DocumentProcessor(self.ingestor)
        self.search_engine = VectorSearchEngine(self.ingestor)
        self.llm_engine = LLMQueryEngine()

    def process_and_store(
            self,
            content: bytes,
            filename: str,
    ) -> Dict[str, any]:

        ext = Path(filename).suffix.lower()
        total_chunks = 0

        if ext == ".pdf":
            for texts, embeddings, page in self.doc_processor.stream_pdf_chunks(
                    content, filename
            ):
                ids = [str(uuid.uuid4()) for _ in texts]
                payloads = [
                    {
                        "text": t,
                        "source": filename,
                        "page": page,
                    }
                    for t in texts
                ]

                self.vector_db.upsert(
                    ids=ids,
                    vectors=embeddings,
                    payloads=payloads,
                )

                total_chunks += len(texts)

            return {
                "status": "success",
                "filename": filename,
                "chunks_processed": total_chunks,
                "saved_to_db": True,
                "streaming": True,
            }

        chunks, embeddings = self.doc_processor.process_small_file(content, filename)

        ids = [str(uuid.uuid4()) for _ in chunks]
        payloads = [
            {
                "text": chunk,
                "source": filename,
                "chunk_index": i,
                "total_chunks": len(chunks),
            }
            for i, chunk in enumerate(chunks)
        ]

        self.vector_db.upsert(
            ids=ids,
            vectors=embeddings,
            payloads=payloads,
        )

        return {
            "status": "success",
            "filename": filename,
            "chunks_processed": len(chunks),
            "saved_to_db": True,
            "streaming": False,
        }

    def ask_with_temporary_file(
            self,
            question: str,
            content: bytes,
            filename: str,
            top_k: int = 3
    ) -> Dict[str, any]:
        """
        Geçici collection kullanarak dosya üzerinde soru-cevap yapar.
        İşlem sonunda geçici veriler silinir.
        """

        # Geçici collection oluştur (düzeltilmiş parametre: collection)
        temp_db = QdrantStorage(collection_name=self.TEMP_COLLECTION_NAME)

        # Her chunk için benzersiz UUID oluştur (Qdrant uyumlu format)
        ids: List[str] = []

        try:
            # Dosyayı işle
            chunks, embeddings = self.doc_processor.process_file(content, filename)

            # Her chunk için ayrı UUID oluştur (pure UUID format)
            ids = [str(uuid.uuid4()) for _ in chunks]

            payloads = [
                {
                    "text": chunk,
                    "source": filename,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
                for i, chunk in enumerate(chunks)
            ]

            # Geçici collection'a kaydet
            temp_db.upsert(
                ids=ids,
                vectors=embeddings,
                payloads=payloads
            )

            # Arama yap
            result = self.search_engine.search_in_database(
                query=question,
                vector_db=temp_db,
                top_k=top_k,
                filename=filename
            )

            # Cevap üret
            answer = self.llm_engine.generate_answer(
                question=question,
                contexts=result["contexts"],
                sources=[filename]
            )

            return {
                "question": question,
                "answer": answer,
                "source": filename,
                "contexts_used": len(result["contexts"]),
                "total_chunks": len(chunks),
                "temporary": True
            }

        finally:
            # Response sonrası geçici verileri sil
            if ids:  # Sadece ID'ler oluşturulduysa sil
                self._cleanup_temp_data(temp_db, ids)

    def _cleanup_temp_data(
            self,
            temp_db: QdrantStorage,
            ids: List[str]
    ) -> None:
        """Geçici collection'dan belirtilen ID'leri siler."""
        try:
            temp_db.delete_by_ids(ids)
        except Exception as e:
            # Silme hatası olursa log tut ama işlemi durdurma
            print(f"Warning: Failed to cleanup temp data: {e}")

    def search_in_database(self, query, top_k: Optional[int] = 3, filename: Optional[str] = None) -> Dict[str, any]:
        result = self.search_engine.search_in_database(
            query=query,
            vector_db=self.vector_db,
            top_k=top_k,
            filename=filename
        )

        return {
            "question": query,
            "source": result["sources"],
            "contexts": result["contexts"],
            "contexts_used": list(result["contexts"]),
        }

    def ask_from_database(
            self,
            question: str,
            top_k: int = 3,
            filename: Optional[str] = None
    ) -> Dict[str, any]:

        result = self.search_engine.search_in_database(
            query=question,
            vector_db=self.vector_db,
            top_k=top_k,
            filename=filename
        )

        answer = self.llm_engine.generate_answer(
            question=question,
            contexts=result["contexts"],
            sources=result["sources"]
        )

        return {
            "question": question,
            "answer": answer,
            "sources": result["sources"],
            "contexts": result["contexts"],
            "contexts_used": len(result["contexts"])
        }

    def list_stored_files(self) -> List[str]:
        return self.vector_db.list_sources()


__all__ = ["RAGService"]