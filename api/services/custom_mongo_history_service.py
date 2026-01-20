from langchain_mongodb import MongoDBChatMessageHistory
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from datetime import datetime


class CustomMongoHistory(MongoDBChatMessageHistory):
    """Extended MongoDB history with metadata support"""

    def add_user_message_with_attachment(self, content: str, filename: str = None, visible: bool = True):
        msg = HumanMessage(
            content=content,
            additional_kwargs={
                "filename": filename,
                "visible_to_user": visible,
                "type": "user_question",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        self.add_message(msg)

    def add_system_summary(self, summary_content: str):
        msg = SystemMessage(
            content=f"Sohbet Özeti: {summary_content}",
            additional_kwargs={
                "visible_to_user": False,
                "include_in_context": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        self.add_message(msg)

    def add_tool_log(self, tool_name: str, tool_output: str, tool_call_id: str):
        msg = AIMessage(
            content=tool_output,
            additional_kwargs={
                "is_tool_output": True,
                "tool_call_id": tool_call_id,
                "tool_name": tool_name,
                "visible_to_user": False,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        self.add_message(msg)
