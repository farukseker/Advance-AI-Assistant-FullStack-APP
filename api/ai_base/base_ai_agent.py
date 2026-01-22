from langgraph.checkpoint.mongodb import MongoDBSaver
from pymongo import MongoClient

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from config import MONGO_URI, OPENROUTER_API_KEY, OPENROUTER_API_HOST
from tools import rag_search_tool, internet_search_tool, summarize_conversation, youtube_video_to_into_text_provider

mongo_client = MongoClient(MONGO_URI)

checkpointer = MongoDBSaver(
    mongo_client,
    db_name="chat",
    collection_name="langgraph_checkpoints"
)

tools = [rag_search_tool, internet_search_tool, summarize_conversation, youtube_video_to_into_text_provider]

__system_prompt = """Sen yardımsever bir AI asistansın. 
Görevlerin:
1. Kullanıcının sorularına doğru ve yardımcı yanıtlar ver
2. Teknik sorular için search_knowledge_base aracını kullan
3. Genel sohbette samimi ve doğal ol
4. Bilmediğin konularda araç kullanmayı tercih et

Önemli: Konuşma geçmişini hatırla ve bağlamı koru.

Kurallar:
- Selamlaşma, sohbet gibi genel mesajlarda araç KULLANMA
- "Bu belgede ne yazıyor?", "X hakkında bilgi ver" gibi sorularda search_knowledge_base kullan
- Spesifik dosya adı varsa onu filtre olarak kullan
- Kaynaklarını belirt
"""


def create_agent_executor(
    model_name: str = "openai/gpt-oss-120b",
    system_prompt: str = __system_prompt
):
    """Create LangGraph ReAct agent with MongoDB checkpointer"""

    llm = ChatOpenAI(
        # model="openai/gpt-4.1-mini",
        model=model_name,
        temperature=0.7,
        base_url=OPENROUTER_API_HOST,
        api_key=OPENROUTER_API_KEY,
        streaming=True,
    )


    # LangGraph ReAct Agent with checkpointer
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
        checkpointer=checkpointer,  # Global checkpointer
        name="chat_agent"
    )

    return agent
