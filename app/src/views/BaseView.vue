<template>
<section class="w-full relative flex flex-col h-full bg-base-100 border-s border-green-200 ps-1 justify-center">
  <article class="text-end w-full flex justify-center absolute top-0 left-0">
    <span class="ms-auto me-4 text-accent">User</span>
  </article>
  <article class="w-full h-full justify-center px-4 sm:px-6 md:px-10 xl:px-80 my-14 overflow-auto">

  <div class="chat chat-start w-full">
    <div class="chat-header">
      grok/4.1-fast
      <time class="text-xs opacity-50">2 hours ago</time>
    </div>
    <div class="chat-bubble">You were the Chosen One!</div>
    <div class="chat-footer opacity-50">Seen</div>
  </div>
  <div class="chat chat-start">
    <div class="chat-header">
      gpt-mini-4o
      <time class="text-xs opacity-50">2 hour ago</time>
    </div>
    <div class="chat-bubble">I loved you.</div>
    <div class="chat-footer opacity-50">Delivered</div>
  </div>

  </article>
  <article class="w-full flex flex-col justify-center sticky bottom-10 left-0 px-4 sm:px-6 md:px-10 xl:px-80">
    <ChatInput />
  </article>
</section>
</template>
<script setup>
import { onMounted, ref } from 'vue'
import axios from 'axios'
import ChatInput from '@/components/ChatInput.vue';

</script>