<template>
<section class="w-full relative flex flex-col h-full bg-base-100 border-s border-green-200 ps-1 justify-center">
  <article class="text-end w-full flex justify-center absolute top-0 left-0">
    <span class="ms-auto me-4 text-accent">User</span>
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
          <MessageBubble :content="item.content" :role="item.role" />
        </DynamicScrollerItem>
      </template>
    </DynamicScroller>
  </article>
  <article class="w-full flex flex-col justify-center sticky bottom-10 left-0 px-4 sm:px-6 md:px-10 xl:px-80">
    <ChatInput @send="sendQuery" />
  </article>
</section>
</template>
<script setup>
import axios from 'axios'
import ChatInput from '@/components/ChatInput.vue';
import { ref, nextTick , onMounted} from 'vue';
import { DynamicScroller, DynamicScrollerItem } from 'vue-virtual-scroller';
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css';
import MessageBubble from '../components/MessageBubble.vue';

const isNearBottom = (el) =>  el.scrollHeight - el.scrollTop - el.clientHeight < 40
const chat_id = ref('')

const scroller = ref(null); // Scroller referansı
const isStreaming = ref(false);

const messages = ref([
  { id: 1, role: 'assistant', content: 'Merhaba, sana nasıl yardımcı olabilirim?' },
  { id: 2, role: 'user', content: 'Yaz kralllll?' }
])

const scrollToBottom = () => {
  nextTick(() => {
    if (scroller.value) {
      scroller.value.scrollToBottom()
    }
  })
}

const currentToolUsage = ref(null)

const sendQuery = async ({query, attachment}) => {
  if (!query || isStreaming.value) return
  
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
    toolUsages: [] // Tool kullanımlarını saklamak için
  })

  try {
    const response = await fetch(
      'http://localhost:8000/ai/chat/69708bdc4f04da701514a261',
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
                console.log('Stream completed')
                break
                
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
  }
}
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

