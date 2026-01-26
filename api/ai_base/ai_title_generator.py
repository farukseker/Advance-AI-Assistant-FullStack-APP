from langchain_openai import ChatOpenAI
from config import OPENROUTER_API_KEY, OPENROUTER_API_HOST
from langchain_core.messages import HumanMessage

__prompt = """
Generate a short chat title (max 6 words).
Do not use quotes.
Text:
{text}
"""

async def generate_chat_title(text: str) -> str:
    llm_title = ChatOpenAI(
        # model="openai/gpt-oss-20b",
        model="google/gemini-2.5-flash-lite",
        temperature=0.4,
        base_url=OPENROUTER_API_HOST,
        api_key=OPENROUTER_API_KEY,
        streaming=False,
    )
    try:
        result = await llm_title.ainvoke([
            HumanMessage(
                content=__prompt.format(text=text)
            )
        ])
        return result.content.strip()
    except Exception as e:
        raise e
    finally:
        del llm_title
