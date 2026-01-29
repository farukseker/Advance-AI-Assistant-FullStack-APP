<template>
<section class="w-full relative flex flex-col h-full bg-base-100 border-s border-green-200 ps-1 justify-center">
    <article class="w-full m-auto justify-center px-4 sm:px-6 md:px-10 xl:px-80 my-14 overflow-auto">
        <form @submit.prevent="speaching">
            <fieldset class="fieldset w-full p-2 shadow my-2 rounded">
            <legend class="fieldset-legend w-full">Text to Speach</legend>
                <textarea required v-model="text" class="textarea h-24 w-full mx-auto outline-0 focus:outline-0 active:outline-0 hover:outline-0" placeholder="any text"></textarea>
                <div>
                    <select v-model="selected_speacher" class="select select-neutral" required>
                        <option disabled selected>Speach Model</option>
                        <option v-for="(speachers, index) in speachers_list" v-bind:key="`${index}_speacher`">{{speachers}}</option>
                    </select>
                    <button class="btn btn-accent float-end" :class="on_speach ? 'skeleton':''" :disabled="on_speach" type="submit">
                        Create speach
                    </button>
                </div>
            </fieldset>
        </form>
        <AudioPlayer  v-if="audio_ref" :audio-src="audio_ref" controls autoplay  />
    </article>
</section>
</template>

<script setup>
import axios from 'axios'
import { onMounted, ref } from 'vue'
import AudioPlayer from '@/components/AudioPlayer.vue'


const text = ref('')
const audio_ref = ref(null)

const selected_speacher = ref('tr-TR-AhmetNeural')
const speachers_list = ref([
    'tr-TR-EmelNeural',
    'tr-TR-AhmetNeural',   
    'en-US-AvaNeural',
    'en-US-AndrewNeural',
    'en-US-EmmaNeural',
    'en-US-BrianNeural',
    'en-US-AnaNeural',
    'en-US-AndrewMultilingualNeural',
    'en-US-AriaNeural',
    'en-US-AvaMultilingualNeural',
    'en-US-BrianMultilingualNeural',
    'en-US-ChristopherNeural',
    'en-US-EmmaMultilingualNeural',
    'en-US-EricNeural',
    'en-US-GuyNeural',
    'en-US-JennyNeural',
    'en-US-MichelleNeural',
    'en-US-RogerNeural',
    'en-US-SteffanNeural',
])
const get_speachers_list = async () => {
    let sl = await axios.get(`${import.meta.env.VITE_API_PATH}/audio/list`)
    speachers_list.value = sl.data
}
// onMounted(get_speachers_list)

const on_speach = ref(false)
const speaching = async () => {
    on_speach.value = true
    try {
        let ar = await axios.post(`${import.meta.env.VITE_API_PATH}/audio/create`, {
            "text": text.value,
            "voice": selected_speacher.value,
            "rate": 1,
            "volume": 20,
            "pitch": 10,
        })
        audio_ref.value = ar.data.audio_ref
    } finally {
        on_speach.value = false
    }
}
</script>