<template>
<section class="w-full relative flex flex-col h-full bg-base-100 border-s border-green-200 ps-1 justify-center">
  <article class="text-end w-full flex justify-center absolute top-0 left-0">
    <span class="ms-auto me-4 text-accent">User</span>
  </article>
  <article class="w-full h-full justify-center px-4 sm:px-6 md:px-10 xl:px-80 my-14 overflow-auto">


 <DynamicScroller
    :items="messages"
    key-field="id"
    class="w-full h-full overflow-auto"
    :min-item-size="72"
  >
    <template #default="{ item: msg }">
      <DynamicScrollerItem
        :item="msg"
        :active="true"
        :size-dependencies="[msg.raw, msg.html]"
      >
        <div
          class="chat w-full"
          :class="msg.role === 'assistant' ? 'chat-start' : 'chat-end'"
        >
          <div class="chat-header">
            {{ msg.role === 'assistant' ? msg.model : 'User' }}
            <time class="text-xs opacity-50">{{ msg.time }}</time>
          </div>

          <div class="chat-bubble w-full">
            <div v-if="msg.done" v-html="msg.html" />
            <pre v-else class="whitespace-pre-wrap">{{ msg.raw }}</pre>
          </div>

          <div class="chat-footer opacity-50">
            Deliveredx
          </div>
        </div>
      </DynamicScrollerItem>
    </template>
  </DynamicScroller>

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

import { DynamicScroller, DynamicScrollerItem } from 'vue-virtual-scroller'

const isNearBottom = (el) =>
  el.scrollHeight - el.scrollTop - el.clientHeight < 40

const messages = [
  {
    id: '1',
    role: 'assistant',
    model: 'gpt-mini-4o',
    raw: 'I loved you.',
    done: true,
    html: '<p>I loved you.</p>',
    time: '2 hour ago',
  },
  {
    id: '2',
    role: 'user',
    raw: 'Ty I love you always.',
    done: true,
    html: '<p>Ty I love you always.</p>',
    time: '2 hour ago',
  },
  {
    id: '3',
    role: 'assistant',
    model: 'gpt-mini-4o',
    raw: '```js\nconsole.log("streaming")\n```',
    done: false,
    time: 'now',
  },
]
</script>

<style>
.streaming-text::after {
  content: '▋';
  animation: blink 1s infinite;
}
</style>

