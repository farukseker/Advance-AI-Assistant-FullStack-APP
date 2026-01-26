<script setup>
import { computed, ref } from 'vue'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'
import '@/assets/MessageBubble.css'

// İstediğin temayı seçebilirsin: github-dark, atom-one-dark, monokai vb.
// import 'github-markdown-css/github-markdown.css'
import { getReadableText } from "@/utils/getReadableText";
import { faVoicemail, faCopy, faLayerGroup } from '@fortawesome/free-solid-svg-icons'

const show_more = ref(false)

const props = defineProps({
  content: { type: String, required: true },
  role: { type: String, default: 'user' },
  used: { type: Object, default: null }
})

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
</script>

<template>
  <div class="chat" :class="role === 'assistant' ? 'chat-start w-full' : 'chat-end'">
    <div class="chat-header">
      Obi-Wan Kenobi
      <time class="text-xs opacity-50">2 hours ago</time>
    </div>
    <div class="chat-bubble shadow-md w-full" :class="role === 'assistant' ? 'bg-gray-100':'bg-cyan-300'">
        <div v-if="role === 'assistant'" class="markdown-body" v-html="renderedContent"></div>
        <pre v-else class="whitespace-pre-wrap">{{ show_more ? props?.content:props?.content?.slice(0, 100) }} <strong v-if="props?.content?.length > 100" class="underline" @click="show_more=!show_more">...</strong></pre>
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
      <button class="btn btn-sm btn-circle btn-neutral">
        <Icon :icon="faCopy" />
      </button>
      <button class="btn btn-sm btn-circle btn-neutral">
        <Icon :icon="faVoicemail" />
      </button>
    </div>
  </div>
</template>
