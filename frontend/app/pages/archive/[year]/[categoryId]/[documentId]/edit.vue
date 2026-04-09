<script setup lang="ts">
import type { CategoryResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const route = useRoute()
const year = computed(() => Number(route.params.year))
const categoryId = computed(() => route.params.categoryId as string)
const documentId = computed(() => route.params.documentId as string)

const { apiFetch } = useApi()
const { getDocument, updateDocument, uploadFile } = useDocuments()
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

watch(selectedCategoryId, async (newCatId) => {
  if (newCatId && newCatId !== categoryId.value) {
    // Update category on backend first
    try {
      await updateDocument(documentId.value, { category_id: newCatId })
      navigateTo(`/archive/${year.value}/${newCatId}/${documentId.value}/edit`, { replace: true })
    } catch (error: any) {
      toast.add({ title: 'Xatolik', description: error?.data?.detail || 'Nomenklaturani o\'zgartirib bo\'lmadi', color: 'error', icon: 'i-lucide-alert-circle' })
      selectedCategoryId.value = categoryId.value
    }
  }
})

async function handleSubmit(data: Record<string, any>, file?: File) {
  try {
    await updateDocument(documentId.value, data)
    if (file) {
      try {
        await uploadFile(documentId.value, file)
      } catch {
        toast.add({ title: 'Ogohlantirish', description: 'Hujjat yangilandi, lekin faylni yuklashda xatolik', color: 'warning', icon: 'i-lucide-alert-triangle' })
      }
    }
    toast.add({ title: 'Muvaffaqiyat', description: 'Hujjat yangilandi', color: 'success', icon: 'i-lucide-check-circle' })
    navigateTo(`/archive/${year.value}/${categoryId.value}/${documentId.value}`)
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
        <USelect
          v-model="selectedCategoryId"
          :items="categories.map(c => ({ label: c.name, value: c.id }))"
          class="w-64"
        />
      </div>

      <DocumentForm
        v-if="doc"
        :category-id="categoryId"
        :initial-data="doc"
        @submit="handleSubmit"
      />
    </div>
  </PagePanel>
</template>
