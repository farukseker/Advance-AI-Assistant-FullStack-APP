import json
from typing import Optional

from langchain.tools import tool
from pydantic import Field, BaseModel

from services import RAGService

class RagInput(BaseModel):
    query: str = Field(
        description="Search question or keywords"
    )

    filename: Optional[str] = Field(
        default=None,
        description="If a specific file is requested, the file name will be entered; otherwise, None will be entered."
    )


@tool("rag_search_tool", args_schema=RagInput)
def rag_search_tool(query: str, filename: str = None):
    """
    Şirket içi dökümanlarda, veritabanına yüklenmiş dosyalarda arama yapar.
    Teknik sorular, şirket politikaları veya döküman içeriği sorulduğunda bunu kullan.
    """
    try:
        rag_service = RAGService()

        # Context şişmesin diye top_k burada sabitlenebilir veya LLM'den istenebilir
        print(f"🛠️ RAG Tool Çalıştı: {query} (Dosya: {filename})")

        result = rag_service.ask_from_database(
            question=query,
            top_k=3,
            filename=filename
        )

        # Format result for LLM
        formatted_result = f"""
        Information founded:
        {result['answer']}

        Sources:
        {json.dumps(result['sources'], ensure_ascii=False, indent=2)}

        Related Text Chunks:
        {chr(10).join(f"- {chunk}" for chunk in result['chunks'])}
        """
        return formatted_result

    except Exception as e:
        return f"Search error: {str(e)}"
