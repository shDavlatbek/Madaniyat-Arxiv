<script setup lang="ts">
import type { CategoryResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const route = useRoute()
const year = computed(() => Number(route.params.year))
const categoryId = computed(() => route.params.categoryId as string)

const { apiFetch } = useApi()
const { createDocument, uploadFile } = useDocuments()
const toast = useToast()

// Fetch category name for display
const { data: categoriesData } = await useAsyncData(
  `categories-create-${year.value}`,
  () => apiFetch<{ items: CategoryResponse[] }>(`/api/years/${year.value}/categories`)
)
const categories = computed(() => categoriesData.value?.items || [])
const currentCategory = computed(() => categories.value.find(c => c.id === categoryId.value))

async function handleSubmit(data: Record<string, any>, file?: File) {
  try {
    const doc = await createDocument({
      ...data,
      year_id: year.value,
      category_id: categoryId.value,
    })
    if (file && doc?.id) {
      try {
        await uploadFile(doc.id, file)
      } catch {
        toast.add({ title: 'Ogohlantirish', description: 'Hujjat yaratildi, lekin faylni yuklashda xatolik', color: 'warning', icon: 'i-lucide-alert-triangle' })
      }
    }
    toast.add({ title: 'Muvaffaqiyat', description: 'Hujjat yaratildi', color: 'success', icon: 'i-lucide-check-circle' })
    navigateTo(`/archive/${year.value}`)
  } catch (error: any) {
    toast.add({ title: 'Xatolik', description: error?.data?.detail || 'Hujjat yaratib bo\'lmadi', color: 'error', icon: 'i-lucide-alert-circle' })
  }
}
</script>

<template>
  <PagePanel title="Yangi hujjat" icon="i-lucide-file-plus">
    <template #headerLeft>
      <UButton icon="i-lucide-arrow-left" variant="ghost" :to="`/archive/${year}`" />
    </template>
    <template #headerRight>
      <UBadge v-if="currentCategory" :label="currentCategory.name" variant="subtle" icon="i-lucide-folder" />
    </template>

    <div class="p-6">
      <!-- Category selector if we want to change -->
      <div v-if="categories.length > 1" class="mb-6 flex items-center gap-3">
        <span class="text-sm text-muted">Nomenklatura:</span>
        <div class="flex flex-wrap gap-2">
          <UButton
            v-for="cat in categories"
            :key="cat.id"
            :label="cat.name"
            :variant="categoryId === cat.id ? 'solid' : 'outline'"
            :color="categoryId === cat.id ? 'primary' : 'neutral'"
            size="sm"
            @click="navigateTo(`/archive/${year}/${cat.id}/create`, { replace: true })"
          />
        </div>
      </div>

      <DocumentForm :category-id="categoryId" :default-year="year" @submit="handleSubmit" />
    </div>
  </PagePanel>
</template>
