<template>
  <div class="audio-player">
    <button @click="togglePlay" class="play-button">
      <svg v-if="!isPlaying" width="16" height="16" viewBox="0 0 24 24" fill="white">
        <path d="M8 5v14l11-7z"/>
      </svg>
      <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="white">
        <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
      </svg>
    </button>

    <div class="progress-wrapper">
      <input 
        type="range" 
        class="progress-slider"
        :value="currentTime" 
        :max="duration"
        @input="seekAudio"
      />
    </div>

    <span class="time-display">-{{ formatTime(duration - currentTime) }}</span>

    <div class="speed-control">
      <button @click="toggleSpeedMenu" class="speed-button">
        Speed
        <span class="speed-value">Normal</span>
        <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor">
          <path d="M7 10l5 5 5-5z"/>
        </svg>
      </button>
      <div v-if="showSpeedMenu" class="speed-menu">
        <button @click="setSpeed(0.5)">0.5x</button>
        <button @click="setSpeed(0.75)">0.75x</button>
        <button @click="setSpeed(1)" class="active">Normal</button>
        <button @click="setSpeed(1.25)">1.25x</button>
        <button @click="setSpeed(1.5)">1.5x</button>
        <button @click="setSpeed(2)">2x</button>
      </div>
    </div>

    <button class="settings-button">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="white">
        <path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94L14.4 2.81c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>
      </svg>
    </button>

    <audio 
      ref="audioElement" 
      @timeupdate="updateProgress" 
      @loadedmetadata="onLoadedMetadata"
      @ended="onEnded"
    >
      <source :src="audioSrc" type="audio/mpeg">
    </audio>
  </div>
</template>

<script setup>
import "@/assets/AudioPlayer.css"
import { ref } from 'vue'

const props = defineProps({
  audioSrc: {
    type: String,
    required: true
  }
})

const audioElement = ref(null)
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const playbackRate = ref(1)
const speedLabel = ref('Normal')
const showSpeedMenu = ref(false)

const togglePlay = () => {
  if (isPlaying.value) {
    audioElement.value.pause()
  } else {
    audioElement.value.play()
  }
  isPlaying.value = !isPlaying.value
}

const updateProgress = () => {
  currentTime.value = audioElement.value.currentTime
}

const onLoadedMetadata = () => {
  duration.value = audioElement.value.duration
}

const onEnded = () => {
  isPlaying.value = false
  currentTime.value = 0
}

const seekAudio = (event) => {
  audioElement.value.currentTime = event.target.value
}

const toggleSpeedMenu = () => {
  showSpeedMenu.value = !showSpeedMenu.value
}

const setSpeed = (speed) => {
  playbackRate.value = speed
  audioElement.value.playbackRate = speed
  speedLabel.value = speed === 1 ? 'Normal' : `${speed}x`
  showSpeedMenu.value = false
}

const formatTime = (seconds) => {
  if (isNaN(seconds)) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

</script>