<script setup lang="ts">
import type { CategoryResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const route = useRoute()
const year = computed(() => Number(route.params.year))
const { apiFetch } = useApi()

const { data: categoriesData, status } = await useAsyncData(
  `categories-${year.value}`,
  () => apiFetch<{ items: CategoryResponse[] }>(`/api/years/${year.value}/categories`)
)

const categories = computed(() => categoriesData.value?.items || [])
</script>

<template>
  <PagePanel :title="`${year} yil - Kategoriyalar`">
    <template #headerLeft>
      <UButton icon="i-lucide-arrow-left" variant="ghost" to="/archive" />
    </template>
    <template #headerRight>
      <UBadge :label="`${categories.length} kategoriya`" variant="subtle" />
    </template>

    <div v-if="status === 'pending'" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
      <USkeleton v-for="i in 6" :key="i" class="h-32 rounded-lg" />
    </div>
    <div v-else-if="categories.length" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
      <NuxtLink
        v-for="cat in categories"
        :key="cat.id"
        :to="`/archive/${year}/${cat.id}`"
      >
        <UCard class="hover:ring-primary transition-all cursor-pointer h-full">
          <div class="flex items-start gap-3">
            <UIcon name="i-lucide-folder" class="text-primary text-2xl shrink-0 mt-0.5" />
            <div class="min-w-0">
              <h3 class="font-semibold text-highlighted truncate">{{ cat.name }}</h3>
              <p v-if="cat.description" class="text-sm text-muted mt-1 line-clamp-2">{{ cat.description }}</p>
              <UBadge :label="cat.code" variant="subtle" size="xs" class="mt-2" />
            </div>
          </div>
        </UCard>
      </NuxtLink>
    </div>
    <div v-else class="flex items-center justify-center p-12">
      <EmptyState icon="i-lucide-folder-x" title="Kategoriyalar topilmadi" :description="`${year} yil uchun kategoriyalar mavjud emas`" />
    </div>
  </PagePanel>
</template>
