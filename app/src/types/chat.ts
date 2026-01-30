export interface Chat {
    chat_id: string
    user_id: string
    title: string
    message_count: number
    created_at: string
    updated_at: string
}

export interface ChatList {
    chats: Chat
}