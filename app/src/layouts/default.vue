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
            : 'w-0 -translate-x-full pointer-events-none overflow-hidden'"
        >
            <hr class="my-2">
            <ul 
                tabindex="0"
                class="menu bg-base-100 p-2 mb-2 w-full pt-24 border-secondary-content border-b"
            > 
                <li>
                    <button class="btn btn-sm btn-primary" @click="$router.push({name:'home'})">
                        New Chat
                    </button>
                </li>
                <li>
                    <details open> 
                        <summary>Scripts</summary> 
                        <ul> 
                            <li>
                                
                                <RouterLink 
                                :class="$router.currentRoute.value.name === 'document-loader' ? 'bg-accent':''"
                                :to="{
                                    name:'document-loader'
                                }">
                                Documents
                                </RouterLink>
                            </li>
                            <li>
                                <RouterLink 
                                :class="$router.currentRoute.value.name === 'audio-create' ? 'bg-accent':''"
                                :to="{
                                    name:'audio-create'
                                }">
                                Text to speach
                                </RouterLink>
                            </li>
                        </ul> 
                    </details> 
                </li>
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
                        <ul class="overflow-auto h-[50vh]"> 
                            <li v-if="chat_list" v-for="chat in chat_list">
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
            <ul class="fixed bottom-0 left-0">
                pars
            </ul>
        </aside>
        <article class="w-full h-screen">
            <Notifications position="bottom right" :max="5" />
            <RouterView />
        </article>
    </section>

</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { faEllipsis, faBars, faChevronLeft, faAngleRight } from '@fortawesome/free-solid-svg-icons'
import { useThemeStore } from '@/stores/theme'
import { Notifications } from '@kyvg/vue3-notification'
import { ref } from 'vue'
import axios from 'axios'
import { storeToRefs } from "pinia";
import { useChatStore } from '@/stores/ChatStore'


const chat_store = useChatStore()
const { chat_list } = storeToRefs(chat_store)


const themeStore = useThemeStore()
const toggle_menu = ref(true)    


onMounted(() => {
  themeStore.sync_theme()
  chat_store.load_chat_list()
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
