<script setup>
import { computed, ref } from 'vue'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'
import '@/assets/MessageBubble.css'
import axios from 'axios'
import AudioPlayer from '@/components/AudioPlayer.vue'

import { getReadableText } from "@/utils/getReadableText"
import { copyTextToBoard } from "@/utils/copyTextToClipBoard"
import { faVoicemail, faCopy, faLayerGroup } from '@fortawesome/free-solid-svg-icons'

const show_more = ref(false)

const props = defineProps({
  historyId: { type: [String, Number], required: true },
  content: { type: String, required: true },
  role: { type: String, default: 'user' },
  used: { type: Object, default: null },
  attachments: { type: Object, default: {} }
})

const attachments = ref(props.attachments)


const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
  highlight: function (str, lang) {

    if (lang && hljs.getLanguage(lang)) {
      try {
        return '<pre class="hljs"><code>' +
               hljs.highlight(str, { language: lang, ignoreIllegals: true }).value +
               '</code></pre>';
      } catch (__) {}
    }

    return '<pre class="hljs"><code>' + md.utils.escapeHtml(str) + '</code></pre>';
  }
})

const renderedContent = computed(() => md.render(props.content))
const assistant_content_ref = ref(null)
const on_create_voice_recored = ref(false)
const send_create_voice_recored = async () => {
  on_create_voice_recored.value = true
  try {
    let ar = await axios.post(`${import.meta.env.VITE_API_PATH}/audio/create`, {
      "text": getReadableText(assistant_content_ref),
      // "voice": 'tr-TR-AhmetNeural',
      "voice": 'en-US-AndrewNeural',
      "rate": 10,
      "volume": 20,
      "pitch": 10,
    })
    
    attachments.value = { audio: ar.data.audio_ref }

    await axios.patch(`${import.meta.env.VITE_API_PATH}/ai/chat/${props.historyId}/merge/content/audio`, {
      history_id: props.historyId,
      content_s3_key: ar.data.audio_s3_key
    })
  }
  finally {
    on_create_voice_recored.value = false
  }
}

</script>

<template>
<div class="chat" :class="role === 'assistant' ? 'chat-start w-full' : 'chat-end'">
    <div class="chat-header">
      {{role === 'assistant' ? 'GPT-5.2':'' }}
      <!--time class="text-xs opacity-50">2 hours ago</time-->
    </div>
    <div class="chat-bubble shadow-md w-full" :class="role === 'assistant' ? 'bg-base-100 dark:bg-base-300':'bg-cyan-300 dark:bg-cyan-900  '">
        <div v-if="role === 'assistant'" ref="assistant_content_ref" class="markdown-body" v-html="renderedContent"></div>
        <pre v-else class="whitespace-pre-wrap">{{ show_more ? props?.content:props?.content?.slice(0, 100) }} <strong v-if="props?.content?.length > 100" class="underline" @click="show_more=!show_more">...</strong></pre>
        <div v-if="on_create_voice_recored" class="skeleton bg-primary-content h-4 w-full"></div>
        <div v-if="attachments">
          <AudioPlayer
            v-if="attachments?.audio"
            :key="`${props.historyId}-audio`"
            :audio-src="attachments.audio"
          />
        </div>
    </div>
    <div class="chat-footer rounded pt-2">
      <div class="tooltip" v-if="props?.used">
        <div class="tooltip-content p-2">
            <code class="text-xs">
              input: {{ props?.used?.input_tokens }}
              <br>
              output: {{ props?.used?.output_tokens }}
              <br>
              total: {{ props?.used?.total_tokens }}
              <br>
              reasoning: {{ props?.used?.reasoning  }}
              <br>
              input_details:
              <br>
               - cache_read: {{ props?.used?.input_token_details?.cache_read }}
            </code>
          </div>
          <button class="btn btn-sm btn-circle btn-neutral">
            <Icon :icon="faLayerGroup" />
          </button>
      </div>
      <button @click="copyTextToBoard(props.content)" class="btn btn-sm btn-circle btn-neutral">
        <Icon :icon="faCopy" />
      </button>
      <button @click="send_create_voice_recored" class="btn btn-sm btn-circle btn-neutral" :class="on_create_voice_recored ? 'animate-pulse delay-75 text-primary': ''">
        <Icon :icon="faVoicemail" />
      </button>
    </div>
  </div>
</template>
