import { defineStore } from 'pinia'
import axios from 'axios'
import { ref } from 'vue'
import type { Chat } from '@/types/chat'


export const useChatStore = defineStore('chat-store', () => {
  const chat_list = ref<Chat[]>([])

  const load_chat_list = async (): Promise<void> => {
    const r = await axios.get<{ chats: Chat[] }>(
      `${import.meta.env.VITE_API_PATH}/ai/chats`,
      {
        params: {
          user_id: 'pars',
          limit: 100
        }
      }
    )

    chat_list.value = r.data.chats
  }

  return { chat_list, load_chat_list }
})
