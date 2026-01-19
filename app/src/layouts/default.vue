<template>
    <section class="w-full flex">
        <button v-if="!toggle_menu" class="btn btn-secondary btn-circle flex justify-center fixed z-10 top-4 left-4" @click="toggle_menu =! toggle_menu">
            <span class="m-auto text-center">-</span>
        </button>
        <article v-else class="absolute md:relative top-0 left-0 w-1/6 h-screen bg-base-100">
            <button class="btn btn-ghost w-full" @click="toggle_menu =! toggle_menu">+</button>
            <hr class="my-2">
            <ul 
                tabindex="0"
                class="menu bg-base-100 rounded-box p-2 shadow-lg mb-2 w-full"
            > 
                <li>
                    <details open> 
                        <summary>Prompts</summary> 
                        <ul> 
                            <li><a>AI Teacher</a></li> 
                            <li></li>
                            <li>+ Create a new prompt</li>
                        </ul> 
                    </details> 
                </li>
                <li></li>
                <li> 
                    <details open> 
                        <summary>History</summary> 
                        <ul> 
                            <li><a class="bg-accent">PyTroch</a></li> 
                        </ul> 
                    </details> 
                </li>
            </ul>
        </article>
        <article class="w-full h-screen">
            <Notifications position="bottom right" :max="5" />
            <RouterView />
        </article>
    </section>

</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { faEllipsis, faBars, faChevronLeft } from '@fortawesome/free-solid-svg-icons'
import { useThemeStore } from '@/stores/theme'
import { Notifications } from '@kyvg/vue3-notification'

const themeStore = useThemeStore()
import { ref } from 'vue'
const toggle_menu = ref(true)    
onMounted(() => {
  themeStore.sync_theme()
})
</script>


<style>
.v-enter-active,
.v-leave-active {
  transition: opacity 1.2s ease;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
}
</style>
