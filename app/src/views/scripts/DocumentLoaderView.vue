<template>
    <section class="w-full h-full grid grid-cols-3">
        <article class="p-3 col-span-2">
            <label>Load New Documents</label>
            <FileInput />
            <hr class="m-4 text-base-300">
            <label>Search documents</label>
            <input disabled type="text" class="w-full input" placeholder="type document name">
            <hr class="my-2 text-base-300">
            <div class="overflow-x-auto">
            <table class="table table-zebra">
                <thead class="bg-primary-content w-full">
                    <tr>
                        <th></th>
                        <th>Source Name</th>
                        <th>Doc Counts</th>
                        <th>remove</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(document, index) in documents_list.files" v-bind:key="`doc_ref_${index}`">
                        <th>1</th>
                        <td>{{ document.filename }}</td>
                        <td>{{ document.document_count }}</td>
                        <td class="cursor-pointer text-error" @click="removeDocument(document.filename)">Delete</td>
                    </tr>
                </tbody>
            </table>
            </div>
        </article>
        <article class="p-3">
            <label>Vector Query</label>
            <input type="text" v-model="search_document_query" @input.stop="search_document" class="w-full input outline-info border-base-300" placeholder="type document name">
            <hr class="m-4 text-base-300">
            <code>
                {{ search_document_results.results }}
            </code>

        </article>
    </section>    
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import axios from 'axios'
import FileInput from '@/components/FileInput.vue'

const documents_list = ref([])
const on_load_documents_list = ref(false)
const load_documents_list = async () => {
    on_load_documents_list.value = true
    try {
        let r = await axios.get(`${import.meta.env.VITE_API_PATH}/embed/list-files`)
        documents_list.value = r.data

    } finally {
        on_load_documents_list.value = false
    }
}

onMounted(load_documents_list)

const search_document_query = ref('')
const search_document_results = ref([])
const on_search_document = ref(false)
const search_document = async () => {
    on_search_document.value = true
    try {
        let r = await axios.get(`${import.meta.env.VITE_API_PATH}/embed/search?q=${search_document_query.value}&top_k=1`)
        search_document_results.value = r.data
    } finally {
        on_search_document.value = false
    }
}
const removeDocument = async (file_name) => {
    await axios.delete(`${import.meta.env.VITE_API_PATH}/embed/remove-file`, {
        data: {
            filename: file_name
        }
    })
    await load_documents_list()
}
</script>