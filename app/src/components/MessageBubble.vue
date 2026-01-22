<script setup>
import { computed } from 'vue';
import MarkdownIt from 'markdown-it';
import hljs from 'highlight.js';
// İstediğin temayı seçebilirsin: github-dark, atom-one-dark, monokai vb.
import 'highlight.js/styles/github-dark.css'; 
import 'github-markdown-css/github-markdown.css'

const props = defineProps({
  content: { type: String, required: true },
  role: { type: String, default: 'user' }
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

const renderedContent = computed(() => md.render(props.content));
</script>

<template>
  <div class="chat" :class="role === 'assistant' ? 'chat-start w-full' : 'chat-end'">
    <div class="chat-bubble w-full" :class="role === 'assistant' ? 'bg-gray-100':'bg-cyan-300'">
        <div v-if="role === 'assistant'" class="markdown-body" v-html="renderedContent"></div>
        <pre v-else class="whitespace-pre-wrap">{{ props.content }}</pre>
    </div>
  </div>
</template>

<style scoped>
.message-row { display: flex; margin-bottom: 15px; width: 100%; }
.message-row.user { justify-content: flex-end; }
.message-row.assistant { justify-content: flex-start; }

.bubble {
  max-width: 85%;
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
  font-family: 'Inter', sans-serif;
}

.assistant .bubble {
  background-color: #f7f7f8;
  color: #2d2d2d;
  border: 1px solid #e5e5e5;
}

.user .bubble {
  background-color: #007bff;
  color: white;
}

:deep(.markdown-body pre) {
  margin: 10px 0;
  padding: 14px;
  border-radius: 8px;
  overflow-x: auto;
  background: #1e1e1e;
}

:deep(.markdown-body code) {
  font-family: 'Fira Code', 'Courier New', monospace;
  font-size: 0.9em;
}

:deep(.markdown-body :not(pre) > code) {
  background-color: rgba(0,0,0,0.1);
  padding: 2px 4px;
  border-radius: 4px;
  color: #e03131;
}


@media (prefers-color-scheme: light) {
  body {
    /*
    --color-canvas-default, copied from 
    https://github.com/sindresorhus/github-markdown-css/blob/main/github-markdown.css
    */
    background-color: #ffffff;
  }
}

@media (prefers-color-scheme: dark) {
  body {
    /* --color-canvas-default */
    background-color: #0d1117;
  }
}
</style>