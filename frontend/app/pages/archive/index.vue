<script setup lang="ts">
import type { CategoryResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const { apiFetch } = useApi()
const { data: catsData, status } = await useAsyncData('archive-categories', () =>
  apiFetch<{ items: CategoryResponse[] }>('/api/categories'),
)

const categories = computed(() => catsData.value?.items || [])

const search = ref('')
const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return categories.value
  return categories.value.filter(c => c.name.toLowerCase().includes(q))
})

// Create document flow: pick nomenklatura → navigate
const createOpen = ref(false)
const createCategoryId = ref<string | undefined>(undefined)

function openCreate() {
  createCategoryId.value = undefined
  createOpen.value = true
}
</script>

<template>
  <PagePanel title="Arxiv" icon="i-lucide-archive">
    <template #headerRight>
      <UBadge :label="`${categories.length} nomenklatura`" variant="subtle" class="mr-2" />
      <UButton icon="i-lucide-plus" label="Yangi hujjat" @click="openCreate" />
    </template>
    <template #toolbar>
      <UInput
        v-model="search"
        icon="i-lucide-search"
        placeholder="Nomenklatura qidirish..."
        class="w-64"
      />
    </template>

    <div v-if="status === 'pending'" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4 p-6">
      <USkeleton v-for="i in 8" :key="i" class="h-32 rounded-xl" />
    </div>
    <div v-else-if="filtered.length" class="p-6">
      <p class="text-sm text-muted mb-4">Nomenklaturani tanlang:</p>
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
        <NuxtLink
          v-for="cat in filtered"
          :key="cat.id"
          :to="`/archive/${cat.id}`"
        >
          <UCard class="hover:ring-2 hover:ring-primary hover:shadow-md transition-all cursor-pointer text-center h-full group">
            <div class="flex flex-col items-center gap-3 py-3">
              <div class="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                <UIcon name="i-lucide-folder" class="text-primary text-xl" />
              </div>
              <span class="text-lg font-bold text-highlighted leading-tight">{{ cat.name }}</span>
            </div>
          </UCard>
        </NuxtLink>
      </div>
    </div>
    <div v-else class="flex items-center justify-center p-12">
      <EmptyState icon="i-lucide-folder-x" title="Nomenklaturalar topilmadi" description="Hozircha arxivda nomenklaturalar mavjud emas" />
    </div>
  </PagePanel>

  <!-- Create document: pick nomenklatura -->
  <UModal v-model:open="createOpen" title="Yangi hujjat yaratish">
    <template #body>
      <div class="space-y-3">
        <p class="text-sm text-muted">Hujjat qaysi nomenklaturaga tegishli?</p>
        <div v-if="categories.length" class="flex flex-col gap-2 max-h-80 overflow-y-auto">
          <UButton
            v-for="cat in categories"
            :key="cat.id"
            :label="cat.name"
            :variant="createCategoryId === cat.id ? 'solid' : 'outline'"
            :color="createCategoryId === cat.id ? 'primary' : 'neutral'"
            block
            class="justify-start"
            @click="createCategoryId = cat.id"
          />
        </div>
        <p v-else class="text-sm text-muted text-center py-4">Nomenklaturalar topilmadi</p>
      </div>
    </template>
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton variant="outline" label="Bekor qilish" @click="createOpen = false" />
        <UButton
          label="Davom etish"
          icon="i-lucide-arrow-right"
          :disabled="!createCategoryId"
          @click="createOpen = false; navigateTo(`/archive/${createCategoryId}/create`)"
        />
      </div>
    </template>
  </UModal>
</template>
