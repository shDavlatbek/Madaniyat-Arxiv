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
  <UDashboardPanel>
    <template #header>
      <UDashboardNavbar title="Arxiv - Yillar">
        <template #right>
          <UBadge :label="`${years.length} yil`" variant="subtle" />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div v-if="status === 'pending'" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4 p-4">
        <USkeleton v-for="i in 8" :key="i" class="h-28 rounded-lg" />
      </div>
      <div v-else-if="years.length" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4 p-4">
        <NuxtLink
          v-for="year in years"
          :key="year.id"
          :to="`/archive/${year.value}`"
        >
          <UCard class="hover:ring-primary transition-all cursor-pointer text-center h-full">
            <div class="flex flex-col items-center gap-2 py-2">
              <UIcon name="i-lucide-calendar" class="text-primary text-3xl" />
              <span class="text-2xl font-bold text-highlighted">{{ year.value }}</span>
            </div>
          </UCard>
        </NuxtLink>
      </div>
      <div v-else class="flex items-center justify-center p-12">
        <UEmpty icon="i-lucide-calendar-x" title="Yillar topilmadi" description="Hozircha arxivda yillar mavjud emas" />
      </div>
    </template>
  </UDashboardPanel>
</template>
