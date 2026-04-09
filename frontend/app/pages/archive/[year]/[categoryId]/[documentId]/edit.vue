<script setup lang="ts">
import type { CategoryResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const route = useRoute()
const year = computed(() => Number(route.params.year))
const categoryId = computed(() => route.params.categoryId as string)
const documentId = computed(() => route.params.documentId as string)

const { apiFetch } = useApi()
const { getDocument, updateDocument, uploadFile, uploadAttachment, deleteAttachment } = useDocuments()
const toast = useToast()

const { data: doc } = await useAsyncData(`doc-edit-${documentId.value}`, () => getDocument(documentId.value))

// Fetch categories for this year
const { data: categoriesData } = await useAsyncData(
  `categories-edit-${year.value}`,
  () => apiFetch<{ items: CategoryResponse[] }>(`/api/years/${year.value}/categories`)
)
const categories = computed(() => categoriesData.value?.items || [])
const currentCategory = computed(() => categories.value.find((c: CategoryResponse) => c.id === categoryId.value))

const selectedCategoryId = ref(categoryId.value)

// Track which existing attachments to delete on save
const pendingDeleteAttachmentIds = ref<string[]>([])

const visibleExistingAttachments = computed(() =>
  (doc.value?.attachments || []).filter(a => !pendingDeleteAttachmentIds.value.includes(a.id))
)

function markAttachmentForDelete(attachmentId: string) {
  pendingDeleteAttachmentIds.value.push(attachmentId)
}

const categoryChanged = computed(() => selectedCategoryId.value !== categoryId.value)

async function handleSubmit(data: Record<string, any>, file?: File, attachments?: File[]) {
  try {
    // Include category_id if changed
    const updateData = categoryChanged.value
      ? { ...data, category_id: selectedCategoryId.value }
      : data
    await updateDocument(documentId.value, updateData)
    if (file) {
      try {
        await uploadFile(documentId.value, file)
      } catch {
        toast.add({ title: 'Ogohlantirish', description: 'Hujjat yangilandi, lekin faylni yuklashda xatolik', color: 'warning', icon: 'i-lucide-alert-triangle' })
      }
    }
    // Delete marked attachments
    for (const attId of pendingDeleteAttachmentIds.value) {
      try {
        await deleteAttachment(documentId.value, attId)
      } catch { /* ignore */ }
    }
    // Upload new attachments
    if (attachments?.length) {
      for (let i = 0; i < attachments.length; i++) {
        try {
          await uploadAttachment(documentId.value, attachments[i]!, i)
        } catch {
          toast.add({ title: 'Ogohlantirish', description: `Ilovani yuklab bo'lmadi: ${attachments[i]!.name}`, color: 'warning', icon: 'i-lucide-alert-triangle' })
        }
      }
    }
    toast.add({ title: 'Muvaffaqiyat', description: 'Hujjat yangilandi', color: 'success', icon: 'i-lucide-check-circle' })
    navigateTo(`/archive/${year.value}/${selectedCategoryId.value}/${documentId.value}`)
  } catch (error: any) {
    toast.add({ title: 'Xatolik', description: error?.data?.detail || 'Yangilab bo\'lmadi', color: 'error', icon: 'i-lucide-alert-circle' })
  }
}
</script>

<template>
  <PagePanel title="Hujjatni tahrirlash" icon="i-lucide-file-pen">
    <template #headerLeft>
      <UButton icon="i-lucide-arrow-left" variant="ghost" :to="`/archive/${year}/${categoryId}/${documentId}`" />
    </template>
    <template #headerRight>
      <UBadge v-if="currentCategory" :label="currentCategory.name" variant="subtle" icon="i-lucide-folder" />
    </template>

    <div class="p-6">
      <!-- Category selector -->
      <div v-if="categories.length > 1" class="mb-6 flex items-center gap-3">
        <span class="text-sm font-medium text-muted">Nomenklatura:</span>
        <USelectMenu
          v-model="selectedCategoryId"
          value-key="value"
          :items="categories.map(c => ({ label: c.name, value: c.id }))"
          :search-input="{ placeholder: 'Qidirish...' }"
          class="w-64"
        />
      </div>

      <DocumentForm
        v-if="doc"
        :category-id="categoryId"
        :initial-data="doc"
        :force-dirty="categoryChanged || pendingDeleteAttachmentIds.length > 0"
        @submit="handleSubmit"
      >
        <!-- Existing attachments shown inside the form via slot -->
        <template #existing-attachments>
          <div v-if="visibleExistingAttachments.length" class="space-y-2 mb-3">
            <p class="text-xs text-muted font-medium">Mavjud ilovalar:</p>
            <div
              v-for="att in visibleExistingAttachments"
              :key="att.id"
              class="flex items-center gap-3 p-2 rounded-lg border border-default"
            >
              <UIcon name="i-lucide-file-text" class="text-primary shrink-0" />
              <span class="flex-1 text-sm font-medium text-highlighted truncate">{{ att.original_filename }}</span>
              <UButton icon="i-lucide-x" variant="ghost" size="xs" color="error" @click="markAttachmentForDelete(att.id)" />
            </div>
          </div>
        </template>
      </DocumentForm>
    </div>
  </PagePanel>
</template>
