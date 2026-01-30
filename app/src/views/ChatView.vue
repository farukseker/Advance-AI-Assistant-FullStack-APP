<template>
<section class="w-full relative flex flex-col h-full bg-base-100 border-s border-green-200 ps-1 justify-center">
  <article class="text-end w-full flex justify-center absolute top-0 left-0">
    <span class="ms-auto me-4 text-accent">User {{ chat_id }}</span>
  </article>
  <article class="w-full h-full justify-center px-4 sm:px-6 md:px-10 xl:px-80 my-14 overflow-auto">
    <DynamicScroller
      ref="scroller"
      :items="messages"
      :min-item-size="50"
      class="scroller"
      key-field="id"
    >
      <template #default="{ item, index, active }">
        <DynamicScrollerItem
          :item="item"
          :active="active"
          :size-dependencies="[item.content]" 
          :data-index="index"
        >
          <MessageBubble 
            :key="item.id"
            :content="item.content"
            :role="item.role"
            :used="item.hasOwnProperty('used') ? item.used : null"
            :historyId="item.id"
            :attachments="item.hasOwnProperty('attachments') ? item.attachments:null"
            @update:attachments="attachments = $event"
          />
        </DynamicScrollerItem>
      </template>
    </DynamicScroller>
    <strong v-if="currentToolUsage" class="font-semibold animate-pulse" >Tool({{ currentToolUsage?.tool }}) :{{ currentToolUsage?.status }}:</strong>
    <pre v-if="currentToolUsage?.input" class="text-xs">{{ currentToolUsage?.input }}</pre>
  </article>
  <article class="w-full flex flex-col justify-center sticky bottom-10 left-0 px-4 sm:px-6 md:px-10 xl:px-80">
    <ChatInput @send="sendQuery" :on_send="on_send" />
  </article>
</section>
</template>
<script setup>
import axios from 'axios'
import ChatInput from '@/components/ChatInput.vue';
import { ref, nextTick , onMounted, watch } from 'vue';
import { DynamicScroller, DynamicScrollerItem } from 'vue-virtual-scroller';
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css'
import MessageBubble from '../components/MessageBubble.vue';
import { useLocalStorage } from '@vueuse/core'
import { useChatStore } from '@/stores/ChatStore'


const chat_store = useChatStore()


const swap_message = useLocalStorage('swap_message', null)
const swap_message_id = useLocalStorage('swap_message_id', null)
const swap_attachment = useLocalStorage('swap_attachment', null)

const { chat_id } = defineProps(['chat_id'])


const load_chat_history = async () => {
    let r = await axios.get(`${import.meta.env.VITE_API_PATH}/ai/chat/${chat_id}/history`)
    messages.value = r.data.history.map(m => ({
        id: m._id,          
        role: m.role === 'ai' ? 'assistant' : m.role,
        content: m.content,
        created_at: m.created_at,
        attachments: m.hasOwnProperty('attachments') ? m.attachments:null,
        used: m.hasOwnProperty('used') ? m.used : null
    }))
}

watch(
  () => chat_id,
  async (newId, oldId) => {
    if (!newId || newId === oldId) return
    await load_chat_history()
  },
  { immediate: true }
)

const isNearBottom = () => {
  const el = scroller.value?.$el
  if (!el) return false
  return el.scrollHeight - el.scrollTop - el.clientHeight < 40
}
const on_send = ref(false)

const scroller = ref(null); // Scroller referansı
const isStreaming = ref(false);

const messages = ref([
])

const scrollToBottom = async () => {
  await nextTick()
  const el = scroller.value?.$el
  if (el) {
    el.scrollTop = el.scrollHeight
  }
}

const currentToolUsage = ref(null)


const sendQuery = async ({query, attachment}) => {
  if (!query || isStreaming.value) return
  scrollToBottom()

  on_send.value = true
  isStreaming.value = true

  const formData = new FormData()
  formData.append("question", query)
  if (attachment) {
    formData.append("file", attachment)
  }

  // Kullanıcı mesajını ekle
  messages.value.push({
    id: Date.now(),
    role: "user",
    content: query
  })

  // Boş asistan mesajı ekle
  messages.value.push({
    id: Date.now() + 1,
    role: "assistant",
    content: "",
    used: [],
    toolUsages: [] // Tool kullanımlarını saklamak için
  })

  try {
    const response = await fetch(
      `${import.meta.env.VITE_API_PATH}/ai/chat/${chat_id}`,
      {
        method: 'POST',
        body: formData
      }
    )

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
        if (isNearBottom()) {
        scrollToBottom()
        }
          const jsonStr = line.slice(6).trim()
          if (!jsonStr) continue

          try {
            const data = JSON.parse(jsonStr)
            const lastIndex = messages.value.length - 1
            
            switch (data.type) {
              case 'token':
                // Normal token geldiğinde mesaja ekle
                messages.value[lastIndex].content += data.content
                break
                
              case 'tool_start':
                // Tool kullanımı başladığında bildirim göster
                currentToolUsage.value = {
                  id: Date.now(),
                  tool: data.tool,
                  input: data.input,
                  status: 'running',
                  output: null
                }
                
                messages.value[lastIndex].toolUsages.push(currentToolUsage.value)
                console.log(`🔧 Tool başlatıldı: ${data.tool}`, data.input)
                break
                
              case 'tool_end':
                // Tool kullanımı bittiğinde sonucu güncelle
                if (currentToolUsage.value) {
                  currentToolUsage.value.status = 'completed'
                  currentToolUsage.value.output = data.content
                  
                  console.log(`✅ Tool tamamlandı: ${data.tool}`, data.content)
                  currentToolUsage.value = null
                }
                break
                
              case 'done':
                messages.value[lastIndex].used = data.metadata
                break
              
              case 'token_usage':
                messages.value[lastIndex].used = data.data

              case 'error':
                throw new Error(data.message || 'Unknown error')
            }
            
            scrollToBottom()
          } catch (e) {
            console.error('JSON parse error:', e, jsonStr)
          }
        }
      }
    }

  } catch (error) {
    console.error('Streaming error:', error)
    const lastIndex = messages.value.length - 1
    messages.value[lastIndex].content = "Üzgünüm, bir hata oluştu."
  } finally {
    isStreaming.value = false
    currentToolUsage.value = null
    on_send.value = false
  }
}

onMounted(async () => {
    if (chat_id === swap_message_id.value){
        await chat_store.load_chat_list()
        swap_attachment.value
        await sendQuery({
            query: swap_message.value,
            attachment: swap_attachment.value
            }
        )
        swap_attachment.value = null
        swap_message.value = null
        swap_message_id.value = null
    } 
    // else {
    //     await load_chat_history()
    // }
})
</script>

<style>
.streaming-text::after {
  content: '▋';
  animation: blink 1s infinite;
}
.chat-container { height: 500px; display: flex; flex-direction: column; border: 1px solid #ccc; }
.scroller { flex: 1; overflow-y: auto; padding: 10px; }
.controls { padding: 10px; border-top: 1px solid #eee; }
</style>

