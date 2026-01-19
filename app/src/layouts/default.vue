<template>
    <!--section class="h-screen">
        <header class="navbar shadow-sm z-10 bg-base-100">
            <div class="container mx-auto flex relative">
                <div class="flex-none">
                    <button v-if="$route.name !== 'home'" @click="$router.back" class="btn btn-square btn-ghost">
                        <Icon :icon="faChevronLeft" />
                    </button>
                    <a class="btn btn-ghost text-xl" href="/">Ulrich</a>
                </div>
                <div class="flex-1 flex absolute top-0 left-0 w-full h-full -z-10">
                    <h1 class="text-xl font-bold text-primary m-auto">{{ $route.meta.title}}</h1>
                </div>
                <div class="w-full"></div>
                <div class="flex-none">
                    <details class="dropdown dropdown-end">
                        <summary class="btn btn-ghost m-1">
                            <Icon :icon="faEllipsis" />
                        </summary>
                        <ul class="menu dropdown-content bg-base-100 rounded-box z-1 min-w-100 md:min-w-52 right-0 p-2 shadow-sm">
                            <li v-if="themeStore.theme === 'dark'" @click="themeStore.set_theme('light')">Dark Mode</li>
                            <li v-if="themeStore.theme === 'light'" @click="themeStore.set_theme('dark')">Light Mode</li>
                        </ul>
                    </details>
                </div>
            </div>
        </header>
        <article class="">
            <Notifications position="bottom right" :max="5" />
            <RouterView />
        </article>
    </section-->

    <section class="w-full flex">
        <article class="absolute md:relative top-0 left-0 w-full h-screen bg-base-100" :class="toggle_menu ? 'md:w-1/6':'md:w-[100px]'">
            <button class="btn btn-primary w-full" @click="toggle_menu =! toggle_menu">+</button>
            <ul class="w-full">
                <!-- <li class="grid grid-cols-6 items-center w-full btn">
                    <Icon :icon="faHome" class="col-span-1 text-center mx-auto" />
                    <h2 class="col-span-5 text-start font-semibold">Test</h2>
                </li> -->
                Home
                Pages
                Dashboard
                Content
                - tags
                todos
                user flow

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
