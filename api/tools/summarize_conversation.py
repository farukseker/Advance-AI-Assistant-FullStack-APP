from langchain_core.tools import tool
from typing import Annotated
from langchain_openai import ChatOpenAI
from config import OPENROUTER_API_KEY, OPENROUTER_API_HOST
from langchain_core.messages import HumanMessage

__prompt = """
Generate a summarize of messages.
Text:
{text}
"""

@tool
async def summarize_conversation(messages: Annotated[str, "Maximum number of messages to summarize"]) -> str:
    """
    Use it to summarize long conversations.
    Only trigger when the conversation has 10 or more messages.
    """
    llm = ChatOpenAI(
        model="openai/gpt-oss-20b",
        temperature=0.4,
        base_url=OPENROUTER_API_HOST,
        api_key=OPENROUTER_API_KEY,
        streaming=False,
    )
    try:
        result = await llm.ainvoke([
            HumanMessage(
                content=__prompt.format(text=messages)
            )
        ])
        return result.content.strip()
    except Exception as e:
        raise e
    finally:
        del llm
