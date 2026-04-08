<script setup lang="ts">
import type { CategoryFieldResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const route = useRoute()
const year = computed(() => Number(route.params.year))
const categoryId = computed(() => route.params.categoryId as string)
const documentId = computed(() => route.params.documentId as string)

const { getDocument, deleteDocument } = useDocuments()
const { apiFetch } = useApi()
const toast = useToast()
const deleteOpen = ref(false)

const { data: doc } = await useAsyncData(`doc-${documentId.value}`, () => getDocument(documentId.value))
const { data: fields } = await useAsyncData(`fields-${categoryId.value}`, () =>
  apiFetch<CategoryFieldResponse[]>(`/api/categories/${categoryId.value}/fields`)
)

function getFieldLabel(fieldId: string) {
  return fields.value?.find(f => f.id === fieldId)?.label || fieldId
}

function getFieldValue(fieldId: string) {
  return doc.value?.field_values.find(fv => fv.category_field_id === fieldId)?.value || '-'
}

const config = useRuntimeConfig()

async function handleDelete() {
  try {
    await deleteDocument(documentId.value)
    toast.add({ title: 'Muvaffaqiyat', description: 'Hujjat o\'chirildi', color: 'success', icon: 'i-lucide-check-circle' })
    navigateTo(`/archive/${year.value}/${categoryId.value}`)
  } catch {
    toast.add({ title: 'Xatolik', description: 'O\'chirib bo\'lmadi', color: 'error', icon: 'i-lucide-alert-circle' })
  }
}
</script>

<template>
  <PagePanel :title="doc?.title || 'Hujjat'">
    <template #headerLeft>
      <UButton icon="i-lucide-arrow-left" variant="ghost" :to="`/archive/${year}/${categoryId}`" />
    </template>
    <template #headerRight>
      <div class="flex gap-2">
        <UButton
          icon="i-lucide-pencil"
          label="Tahrirlash"
          variant="soft"
          :to="`/archive/${year}/${categoryId}/${documentId}/edit`"
        />
        <UButton
          icon="i-lucide-trash-2"
          label="O'chirish"
          color="error"
          variant="soft"
          @click="deleteOpen = true"
        />
      </div>
    </template>

    <div v-if="doc" class="max-w-4xl mx-auto p-4 sm:p-6 space-y-6">
      <!-- Common fields -->
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-lucide-file-text" class="text-primary" />
            <span class="font-semibold">Asosiy ma'lumotlar</span>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p class="text-sm text-muted">Hujjat raqami</p>
            <p class="font-mono font-semibold text-highlighted">{{ doc.document_number }}</p>
          </div>
          <div>
            <p class="text-sm text-muted">Sana</p>
            <p class="text-highlighted">{{ doc.date }}</p>
          </div>
          <div>
            <p class="text-sm text-muted">Imzo qo'ygan shaxs</p>
            <p class="text-highlighted">{{ doc.signer || '-' }}</p>
          </div>
          <div>
            <p class="text-sm text-muted">Kimga</p>
            <p class="text-highlighted">{{ doc.target || '-' }}</p>
          </div>
          <div>
            <p class="text-sm text-muted">Sahifalar</p>
            <p class="text-highlighted">{{ doc.pages || '-' }}</p>
          </div>
          <div>
            <p class="text-sm text-muted">Fayl</p>
            <a
              v-if="doc.file_path"
              :href="`${config.public.apiBase}/api/documents/${doc.id}/file`"
              target="_blank"
              class="text-primary hover:underline flex items-center gap-1"
            >
              <UIcon name="i-lucide-download" />
              Yuklab olish
            </a>
            <p v-else class="text-muted">-</p>
          </div>
        </div>

        <div v-if="doc.short_desc" class="mt-4 pt-4 border-t border-default">
          <p class="text-sm text-muted">Qisqacha tavsif</p>
          <p class="text-highlighted mt-1">{{ doc.short_desc }}</p>
        </div>
      </UCard>

      <!-- Dynamic fields -->
      <UCard v-if="fields?.length && doc.field_values.length">
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-lucide-layers" class="text-primary" />
            <span class="font-semibold">Qo'shimcha maydonlar</span>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div v-for="field in fields" :key="field.id">
            <p class="text-sm text-muted">{{ field.label }}</p>
            <p class="text-highlighted">{{ getFieldValue(field.id) }}</p>
          </div>
        </div>
      </UCard>
    </div>
  </PagePanel>

  <UModal v-model:open="deleteOpen" title="Hujjatni o'chirish" description="Bu amalni qaytarib bo'lmaydi.">
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton variant="ghost" label="Bekor qilish" @click="deleteOpen = false" />
        <UButton color="error" label="O'chirish" icon="i-lucide-trash-2" @click="handleDelete" />
      </div>
    </template>
  </UModal>
</template>
