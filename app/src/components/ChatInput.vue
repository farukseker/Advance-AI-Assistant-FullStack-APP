<template>

<div class="flex flex-col gap-2">
    <input 
        type="file"
        class="rounded-full transition-all duration-300"
        @change="onFileChange"
        accept="
        .pdf,.doc,.docx,
        application/pdf,
        application/msword,
        application/vnd.openxmlformats-officedocument.wordprocessingml.document,
        image/*"
        :class="addAttachment
            ? 'file-input file-input-sm translate-y-0'
            : 'h-0 -translate-y-full z-10'"
    >
    <div class="relative flex flex-col">
        <div class="dropdown dropdown-top dropdown-end absolute top-0 left-0 mt-1 ms-1 z-30">
        <button 
            tabindex="0"
            type="button" 
            class="btn btn-sm btn-circle"
        > 
            <Icon :icon="faPlusCircle" /> 
        </button>
        
        <ul 
            tabindex="0"
            class="dropdown-content menu bg-base-100 rounded-box z-50 w-52 p-2 shadow-lg mb-2"
        > 
            <li>
                <button type="button" class="btn flex justify-start" :class="addAttachment ? 'btn-accent':'btn-ghost'" @click="addAttachment=!addAttachment">
                    <span class="text-start">
                        Add a attachment
                    </span>
                </button>
            </li> 
            <li class="border-b"></li> 
            <li><button type="button">Youtube</button></li> 
            <li><button type="button">Search</button></li> 
            <li><button type="button">Think</button></li> 
            <li><button type="button">Generare Image</button></li> 
            <li> 
            <details open> 
                <summary>Models</summary> 
                <ul> 
                <li><a>Grok Fast 4.1</a></li> 
                <li><a>Gpt 4</a></li> 
                </ul> 
            </details> 
            </li> 
        </ul> 
        </div>
    <form @submit.prevent="sendMessages">
        <!-- Input label -->
        <label class="input validator w-full rounded-full m-auto px-1"> 
        <input 
            type="text" 
            class="ps-10"
            v-model="query" 
            required 
            placeholder="!q query !y youtube , type ur message here"
        > 

        <button class="btn btn-sm btn-circle" type="button"> 

            <span v-if="!isRecording" @click="startRecording" :class="onAudioProceses ? 'text-primary animate-spin':''"> 
            <Icon v-if="onAudioProceses" :icon="faDharmachakra" />
            <Icon v-else :icon="faMicrophone" /> 
            </span> 
            <span v-else @click="stopRecording" class="text-primary animate-pulse delay-75"> 
            <Icon :icon="faDotCircle" /> 
            </span> 
        </button> 
        
        <button class="btn btn-sm btn-circle btn-accent" type="submit"> 
            <Icon class="pt-0.5" :icon="faPaperPlane" /> 
        </button> 
        </label>
    </form>
    
    </div>
</div>

</template>

<script setup>
import { faPlusCircle, faMicrophone, faDotCircle, faPaperPlane, faCircleStop, faDharmachakra } from '@fortawesome/free-solid-svg-icons'
import axios from 'axios'
import { onMounted, ref } from 'vue'

const emits = defineEmits(['send'])


const query = ref('')


const addAttachment = ref(false)
const attachment = ref(null)
const onFileChange = (e) => {
  attachment.value = e.target.files[0] || null
}
// enctype="multipart/form-data"

const responseText = ref('')
const isRecording = ref(false)
const mediaRecorder = ref(null)
const onAudioProceses = ref(false)

// Start recording
const startRecording = async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
  mediaRecorder.value = new MediaRecorder(stream, { mimeType: "audio/webm" })
  
  mediaRecorder.value.start()
  isRecording.value = true
}

// Stop recording and send to FastAPI
const stopRecording = async () => {
  if (!mediaRecorder.value) return
  
  isRecording.value = false

  // Promise ile onstop event'ini bekle
  const audioBlob = await new Promise((resolve) => {
    const chunks = []
    
    mediaRecorder.value.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.push(e.data)
    }

    mediaRecorder.value.onstop = () => {
      const blob = new Blob(chunks, { type: "audio/wav" })
      resolve(blob)
    }

    mediaRecorder.value.stop()
  })

  // Stream'i durdur
  mediaRecorder.value.stream.getTracks().forEach(track => track.stop())

  if (!audioBlob) return
  onAudioProceses.value = true
  const formData = new FormData()
  formData.append("file", audioBlob, "audio.wav")

  try {
    const res = await axios.post("http://localhost:8000/audio/transcribe", formData, {
      headers: { "Content-Type": "multipart/form-data" }
    })
    query.value = query.value + ' ' + res.data.text
  } catch (err) {
    console.error(err)
    responseText.value = "Error transcribing audio"
  } finally {
    onAudioProceses.value = false  
  }
}

const sendMessages = async () => {
  emits('send', {
    query: query.value,
    attachment: attachment.value
  })
}


</script>