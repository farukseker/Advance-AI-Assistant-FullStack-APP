<template>
  <div class="flex flex-col gap-4">
    <!-- File list -->
    <div
      v-if="files.length"
      class="w-full rounded-lg border border-base-300 p-3 space-y-2 text-sm"
    >
      <div
        v-for="(file, i) in files"
        :key="i"
        class="flex justify-between items-center"
      >
        <span class="truncate">{{ file.name }}</span>
        <button class="btn btn-xs btn-ghost" @click="removeFile(i)">✕</button>
      </div>
    </div>

    <!-- Drop zone -->
    <div
      ref="dropZone"
      class="flex-1 flex items-center justify-between gap-4 rounded-lg border-2 border-dashed border-base-300 bg-base-100 p-4 cursor-pointer transition"
      :class="isDragging ? 'border-primary bg-base-200' : ''"
      @dragenter.prevent="onDragEnter"
      @dragover.prevent="onDragOver"
      @dragleave.prevent="onDragLeave"
      @drop.prevent="onDrop"
      @click="openFilePicker"
    >
      <div class="text-sm text-base-content/70">
        <p class="font-medium">Drag and drop files here</p>
        <p class="text-xs">PDF · DOC · DOCX · CSV · max 200MB</p>
      </div>

      <span class="btn btn-outline btn-sm">Browse</span>

      <input
        ref="fileInput"
        type="file"
        class="hidden"
        multiple
        accept=".pdf,.doc,.docx,.csv"
        @change="onFileSelect"
      />
    </div>
  </div>

  <!-- Load button -->
  <div v-if="files.length" class="mt-4 flex justify-end">
    <button
      class="btn btn-primary"
      :disabled="loading"
      @click="loadFiles"
    >
      {{ loading ? 'Loading…' : 'Load files' }}
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const isDragging = ref(false)
const fileInput = ref(null)
const files = ref([])
const loading = ref(false)

const allowedTypes = [
  'application/pdf',
  'text/csv',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
]

function onDragEnter() {
  isDragging.value = true
}

function onDragOver() {
  isDragging.value = true
}

function onDragLeave() {
  isDragging.value = false
}

function onDrop(e) {
  isDragging.value = false
  handleFiles(e.dataTransfer.files)
}

function openFilePicker() {
  fileInput.value.click()
}

function onFileSelect(e) {
  handleFiles(e.target.files)
  e.target.value = ''
}

function handleFiles(fileList) {
  const valid = [...fileList].filter(
    f => allowedTypes.includes(f.type)
  )

  valid.forEach(f => {
    if (!files.value.find(x => x.name === f.name && x.size === f.size)) {
      files.value.push(f)
    }
  })
}

function removeFile(index) {
  files.value.splice(index, 1)
}

async function loadFiles() {
  loading.value = true

  try {
    for (const file of files.value) {
      await uploadToVectorDB(file)
    }
    files.value = []
  } finally {
    loading.value = false
  }
}

async function uploadToVectorDB(file) {
  const formData = new FormData()
  formData.append('file', file)

  await axios.post(`${import.meta.env.VITE_API_PATH}/embed/load-document`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
</script>
