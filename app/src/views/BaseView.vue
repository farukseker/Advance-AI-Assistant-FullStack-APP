<template>
  <section class="w-full h-screen flex justify-center">
      <article class="w-full flex flex-col justify-center sticky bottom-10 left-0 px-4 sm:px-6 md:px-10 xl:px-80">
      <ChatInput @send="sendQuery" :on_send="on_send" />
    </article>
  </section>
</template>

<script setup>
import ChatInput from '@/components/ChatInput.vue';
import { useLocalStorage } from '@vueuse/core'
import axios from 'axios';
import { useRouter } from 'vue-router'
import { ref } from "vue";

const router = useRouter()

const swap_message = useLocalStorage('swap_message', null)
const swap_message_title = useLocalStorage('swap_message_title', null)
const swap_message_id = useLocalStorage('swap_message_id', null)
const swap_attachment = useLocalStorage('swap_attachment', null)

const on_send = ref(false)

const sendQuery = async ({ query, attachment }) => {
  const response = await axios.post(
    `${import.meta.env.VITE_API_PATH}/ai/create-chat`,
    {
        message: query,
    }
  )
  
  if (response.status === 200){
    swap_message.value = query
    swap_message_id.value=response.data.chat_id
    swap_message_title.value=response.data.title
    swap_attachment.value=attachment
  }

  router.push({
    name: 'chat',
    params: {
      chat_id: response.data.chat_id
    }
  })
}

</script>