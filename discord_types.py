from __future__ import annotations
from typing import Dict, List, Literal, NotRequired, Optional, TypedDict


class AuthorType(TypedDict):
    id: str
    username: str
    avatar: str
    discriminator: str
    public_flags: int
    global_name: str
    avatar_decoration_data: NotRequired["AvatarDecorationType"]
    banner: Optional[str]
    accent_color: Optional[str]


class AvatarDecorationType(TypedDict):
    asset: str
    sku_id: str
    expires_at: Optional[str]


class AttachmentType(TypedDict):
    id: str
    filename: str
    size: int
    url: str
    proxy_url: str
    width: int
    height: int
    content_type: str


class ReactionEmojiType(TypedDict):
    id: Optional[str]
    name: Optional[str]


class ReactionType(TypedDict):
    emoji: ReactionEmojiType
    count: int
    count_details: Dict[str, int]
    me: bool


class MessageReferenceType(TypedDict):
    message_id: str
    channel_id: str
    type: int


class ThreadMetadataType(TypedDict):
    archived: bool
    archive_timestamp: str  # ISO 8601 timestamp
    auto_archive_duration: int
    locked: bool
    create_timestamp: str  # ISO 8601 timestamp


class ThreadType(TypedDict):
    id: str
    type: int
    last_message_id: str
    flags: int
    guild_id: str
    name: str
    parent_id: str
    rate_limit_per_user: int
    bitrate: int
    user_limit: int
    rtc_region: Optional[str]
    owner_id: str
    thread_metadata: ThreadMetadataType
    message_count: int
    member_count: int
    total_message_sent: int
    member_ids_preview: List[str]


class MessageType(TypedDict):
    id: str
    content: str
    timestamp: str
    edited_timestamp: Optional[str]
    author: AuthorType
    attachments: List[AttachmentType]
    reactions: List[ReactionType]
    mentions: List[str]
    mention_roles: List[str]
    pinned: bool
    channel_id: str
    flags: int
    message_reference: Optional[MessageReferenceType]
    thread: Optional[ThreadType]
    type: Literal[
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20
    ]
