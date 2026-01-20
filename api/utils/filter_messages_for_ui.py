from typing import List

from langchain_core.messages import BaseMessage


def filter_messages_for_ui(messages: List[BaseMessage]) -> List[dict]:
    """Filter messages for UI display"""
    clean_list = []
    for m in messages:
        kwargs = m.additional_kwargs
        if kwargs.get("visible_to_user", True) == False:
            continue

        clean_list.append({
            "role": m.type,
            "content": m.content,
            "filename": kwargs.get("filename"),
            "timestamp": kwargs.get("timestamp")
        })
    return clean_list
