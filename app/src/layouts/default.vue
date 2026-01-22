<template>
    <section class="w-full flex">
        <div
            class="w-full md:w-64 fixed z-20 top-4 md:top-12 left-0 md:left-4 px-4 md:px-0"
            :class="toggle_menu ? 'md:flex' : 'flex'"
            @click="toggle_menu = !toggle_menu"
        >
        <button
            class="btn"
            :class="toggle_menu ? 'w-full btn-ghost':'btn-primary btn-circle shadow'"
        >
            <span v-if="toggle_menu">Pars</span>
            <Icon v-else :icon="faAngleRight" />
        </button>
        </div>
        
        <aside
        class="fixed md:relative top-0 left-0 z-10 h-screen
                transition-all duration-300"
        :class="toggle_menu
            ? 'w-screen md:w-84 translate-x-0'
            : 'w-0 -translate-x-full md:w-0 z-10'"
        >
            <hr class="my-2">
            <ul 
                tabindex="0"
                class="menu bg-base-100 rounded-box p-2 shadow-lg mb-2 w-full pt-16"
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
                <li > 
                    <details open> 
                        <summary>History</summary> 
                        <ul class="overflow-auto h-[60vh]"> 
                            <li v-for="chat in chats">
                                <a 
                                    :class="$router.currentRoute.value.params.chat_id === chat.chat_id ? 'bg-accent':''"
                                    @click="$router.push({
                                        name: 'chat',
                                        params: {
                                        chat_id: chat.chat_id
                                    }
                                    })"
                                >{{chat.title}}</a>
                            </li> 
                        </ul> 
                    </details> 
                </li>
            </ul>
        </aside>
        <article class="w-full h-screen">
            <Notifications position="bottom right" :max="5" />
            <RouterView />
        </article>
    </section>

</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { faEllipsis, faBars, faChevronLeft, faAngleRight } from '@fortawesome/free-solid-svg-icons'
import { useThemeStore } from '@/stores/theme'
import { Notifications } from '@kyvg/vue3-notification'
import { ref } from 'vue'
import axios from 'axios'


const themeStore = useThemeStore()
const toggle_menu = ref(true)    

const chats = ref() 
const load_chats = async () => {
    let r = await axios.get(`${import.meta.env.VITE_API_PATH}/ai/chats`, {
        params: {
            user_id: 'pars',
            limit: 100
        }
    })
    chats.value = r.data.chats
} 



onMounted(() => {
  themeStore.sync_theme()
  load_chats()
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
