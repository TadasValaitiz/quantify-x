from datetime import datetime
import json
from typing import Any, Dict, Optional
from pydantic import BaseModel


class ChatMessage(BaseModel):
    id: Optional[int]
    conversation_id: int
    role: str
    content: str
    context: Optional[Dict] = None
    created_at: str

    def __init__(
        self,
        id: Optional[int],
        conversation_id: int,
        role: str,
        content: str,
        context: Optional[Dict],
        created_at: str,
    ):
        super().__init__(
            id=id,
            conversation_id=conversation_id,
            role=role,
            content=content,
            context=context,
            created_at=created_at
        )

    @classmethod
    def from_dict(cls, message: Dict[str, Any]):
        id = message["id"]
        conversation_id = message["conversation_id"]
        role = message["role"]
        content = message["content"]
        context = (
            json.loads(message["context"]) if message["context"] is not None else None
        )
        created_at = message["created_at"]

        return cls(id, conversation_id, role, content, context, created_at)

    @classmethod
    def new_message(cls, conversation_id:int, role:str,content:str, context:Optional[Dict]):
        created_at = datetime.now().isoformat()
        return cls(None, conversation_id, role, content, context, created_at)