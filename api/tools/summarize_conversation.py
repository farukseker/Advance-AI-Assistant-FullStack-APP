from langchain_core.tools import tool
from typing import Annotated


@tool
async def summarize_conversation(max_messages: Annotated[int, "Maximum number of messages to summarize"] = 20) -> str:
    """
    Use it to summarize long conversations.
    Only trigger when the conversation has 10 or more messages.
    """
    raise NotImplementedError