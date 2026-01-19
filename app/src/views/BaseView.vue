<template>
<section class="w-full relative flex flex-col h-full bg-base-300 justify-center">
<article class="border w-full flex justify-center absolute top-0 left-0">
</article>
<article class="w-full  flex justify-center px-20 my-14 overflow-auto">

</article>
<article class="w-full flex flex-col justify-center sticky bottom-10 left-0 px-80">

<div class="relative flex flex-col">
    <!-- Dropdown menü - label dışında -->
    <div class="dropdown dropdown-top dropdown-end absolute  top-0 left-0 mt-1 ms-1 z-10">
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
        <li><button type="button">Add a attachment</button></li> 
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
<form @submit="">
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
        <span v-if="!isRecording" @click="startRecording"> 
          <Icon :icon="faMicrophone" /> 
        </span> 
        <span v-else @click="stopRecording" class="text-primary animate-pulse delay-75"> 
          <Icon :icon="faDotCircle" /> 
        </span> 
      </button> 
      
      <button class="btn btn-sm btn-circle btn-accent" type="submit"> 
        <Icon class="pt-0.5" :icon="faPaperPlane" /> 
      </button> 
    </label>

    <div class="">{{ responseText }}</div>
    <div class="validator-hint hidden">Enter valid email address</div>
</form>
 
</div>


</article>
</section>
</template>
<script setup>
import { faPlusCircle, faMicrophone, faDotCircle, faPaperPlane } from '@fortawesome/free-solid-svg-icons'
import { onMounted, ref } from 'vue'
import axios from 'axios'

const query = ref('')
const responseText = ref('')
const isRecording = ref(false)
const mediaRecorder = ref(null)

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
  }
}

// Optional: send query as text to API
const sendQuery = async () => {
  if (!query.value) return

  try {
    const res = await axios.post("http://localhost:8000/query", { query: query.value })
    responseText.value = res.data.text
  } catch (err) {
    console.error(err)
    responseText.value = "Error sending query"
  }
}

const isDropdownOpen = ref(false)

const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value
}

const closeDropdown = () => {
  isDropdownOpen.value = false
}
</script>