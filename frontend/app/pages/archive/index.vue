<script setup lang="ts">
import type { YearResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const { apiFetch } = useApi()
const { data: yearsData, status } = await useAsyncData('years', () =>
  apiFetch<{ items: YearResponse[] }>('/api/years')
)

const years = computed(() => yearsData.value?.items || [])
</script>

<template>
  <PagePanel title="Arxiv" icon="i-lucide-archive">
    <template #headerRight>
      <UBadge :label="`${years.length} yil`" variant="subtle" />
    </template>

    <div v-if="status === 'pending'" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4 p-6">
      <USkeleton v-for="i in 8" :key="i" class="h-32 rounded-xl" />
    </div>
    <div v-else-if="years.length" class="p-6">
      <p class="text-sm text-muted mb-4">Yilni tanlang:</p>
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
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
</template>
