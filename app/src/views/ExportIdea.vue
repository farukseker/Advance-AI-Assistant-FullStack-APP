<script setup>
import { ref, nextTick } from 'vue';
// Virtual scroller importları (main.js'de global plugin olarak da ekleyebilirsin)
import { DynamicScroller, DynamicScrollerItem } from 'vue-virtual-scroller';
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css';
import MessageBubble from '../components/MessageBubble.vue';

// Mesaj verisi
const messages = ref([
  { id: 1, role: 'assistant', content: 'Merhaba, sana nasıl yardımcı olabilirim?' }
]);

const scroller = ref(null); // Scroller referansı
const isStreaming = ref(false);

// STREAMING SİMÜLASYONU
const startStreaming = async () => {
  if (isStreaming.value) return;
  isStreaming.value = true;

  // 1. Yeni boş mesaj ekle
  const newMessageId = Date.now();
  const newMessage = { id: newMessageId, role: 'assistant', content: '' };
  messages.value.push(newMessage);

  // 2. Uzun bir markdown metni simüle et
  const fullText = `Vue 3 **Harika** bir framework!\n\nİşte bir kod örneği:\n\`\`\`javascript\nconsole.log("Merhaba Dünya");\n\`\`\`\n\nListe örneği:\n- Hızlı\n- Hafif\n- Güçlü`;
  
  const chunks = fullText.split(''); // Harf harf bölelim
  
  // 3. Harf harf ekleyerek streaming yap
  for (const char of chunks) {
    // Son mesajı güncelle
    const lastIndex = messages.value.length - 1;
    messages.value[lastIndex].content += char;

    // Sanallaştırma sırasında oto-scroll (en alta kaydırma)
    scrollToBottom();
    
    // Simüle edilmiş gecikme (network stream hızı)
    await new Promise(r => setTimeout(r, 30));
  }
  
  isStreaming.value = false;
};

const scrollToBottom = () => {
  nextTick(() => {
    if (scroller.value) {
      scroller.value.scrollToBottom();
    }
  });
};
</script>

<template>
  <div class="chat-container">
    
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

    <div class="controls">
      <button @click="startStreaming" :disabled="isStreaming">
        {{ isStreaming ? 'Yazıyor...' : 'Cevap Üret (Simüle Et)' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.chat-container { height: 500px; display: flex; flex-direction: column; border: 1px solid #ccc; }
.scroller { flex: 1; overflow-y: auto; padding: 10px; }
.controls { padding: 10px; border-top: 1px solid #eee; }
button { padding: 10px 20px; cursor: pointer; }
</style>