<script setup lang="ts">
import type { CategoryResponse, YearResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const { apiFetch } = useApi()
const { data: yearsData, status } = await useAsyncData('years', () =>
  apiFetch<{ items: YearResponse[] }>('/api/years')
)

const years = computed(() => yearsData.value?.items || [])

// Create document flow: pick year → pick category → navigate
const createOpen = ref(false)
const createYear = ref<number | undefined>(undefined)
const createCategoryId = ref<string | undefined>(undefined)
const createCategories = ref<CategoryResponse[]>([])
const loadingCategories = ref(false)

watch(createYear, async (val) => {
  createCategoryId.value = undefined
  createCategories.value = []
  if (!val) return
  loadingCategories.value = true
  try {
    const data = await apiFetch<{ items: CategoryResponse[] }>(`/api/years/${val}/categories`)
    createCategories.value = data.items || []
  } finally {
    loadingCategories.value = false
  }
})

function openCreate() {
  createYear.value = undefined
  createCategoryId.value = undefined
  createCategories.value = []
  createOpen.value = true
}
</script>

<template>
  <PagePanel title="Arxiv" icon="i-lucide-archive">
    <template #headerRight>
      <UBadge :label="`${years.length} yil`" variant="subtle" class="mr-2" />
      <UButton icon="i-lucide-plus" label="Yangi hujjat" @click="openCreate" />
    </template>

    <div v-if="status === 'pending'" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4 p-6">
      <USkeleton v-for="i in 8" :key="i" class="h-32 rounded-xl" />
    </div>
    <div v-else-if="years.length" class="p-6">
      <p class="text-sm text-muted mb-4">Yilni tanlang:</p>
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
        <NuxtLink to="/archive/all">
          <UCard class="hover:ring-2 hover:ring-primary hover:shadow-md transition-all cursor-pointer text-center h-full group ring-1 ring-primary/30 bg-primary/5">
            <div class="flex flex-col items-center gap-3 py-3">
              <div class="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center group-hover:bg-primary/30 transition-colors">
                <UIcon name="i-lucide-layers" class="text-primary text-xl" />
              </div>
              <span class="text-2xl font-bold text-primary">Barchasi</span>
            </div>
          </UCard>
        </NuxtLink>
        <NuxtLink
          v-for="year in years"
          :key="year.id"
          :to="`/archive/${year.value}`"
        >
          <UCard class="hover:ring-2 hover:ring-primary hover:shadow-md transition-all cursor-pointer text-center h-full group">
            <div class="flex flex-col items-center gap-3 py-3">
              <div class="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                <UIcon name="i-lucide-calendar" class="text-primary text-xl" />
              </div>
              <span class="text-2xl font-bold text-highlighted">{{ year.value }}</span>
            </div>
          </UCard>
        </NuxtLink>
      </div>
    </div>
    <div v-else class="flex items-center justify-center p-12">
      <EmptyState icon="i-lucide-calendar-x" title="Yillar topilmadi" description="Hozircha arxivda yillar mavjud emas" />
    </div>
  </PagePanel>

  <!-- Create document: pick year + category -->
  <UModal v-model:open="createOpen" title="Yangi hujjat yaratish">
    <template #body>
      <div class="space-y-4">
        <div>
          <p class="text-sm text-muted mb-2">Yilni tanlang:</p>
          <div class="flex flex-wrap gap-2">
            <UButton
              v-for="y in years"
              :key="y.id"
              :label="String(y.value)"
              :variant="createYear === y.value ? 'solid' : 'outline'"
              :color="createYear === y.value ? 'primary' : 'neutral'"
              size="sm"
              @click="createYear = y.value"
            />
          </div>
        </div>

        <div v-if="createYear">
          <p class="text-sm text-muted mb-2">Nomenklaturani tanlang:</p>
          <div v-if="loadingCategories" class="py-4 flex justify-center">
            <UIcon name="i-lucide-loader-2" class="animate-spin text-muted" />
          </div>
          <div v-else-if="createCategories.length" class="flex flex-col gap-2">
            <UButton
              v-for="cat in createCategories"
              :key="cat.id"
              :label="cat.name"
              :variant="createCategoryId === cat.id ? 'solid' : 'outline'"
              :color="createCategoryId === cat.id ? 'primary' : 'neutral'"
              block
              class="justify-start"
              @click="createCategoryId = cat.id"
            />
          </div>
          <p v-else class="text-sm text-muted text-center py-4">Bu yil uchun nomenklaturalar topilmadi</p>
        </div>
      </div>
    </template>
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton variant="outline" label="Bekor qilish" @click="createOpen = false" />
        <UButton
          label="Davom etish"
          icon="i-lucide-arrow-right"
          :disabled="!createYear || !createCategoryId"
          @click="createOpen = false; navigateTo(`/archive/${createYear}/${createCategoryId}/create`)"
        />
      </div>
    </template>
  </UModal>
</template>
