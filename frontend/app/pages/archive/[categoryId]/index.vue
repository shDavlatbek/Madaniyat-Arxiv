<script setup lang="ts">
import type { CategoryResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const route = useRoute()
const categoryId = computed(() => route.params.categoryId as string)

const { apiFetch } = useApi()
const { listDocuments } = useDocuments()

const search = ref('')
const dateFrom = ref('')
const dateTo = ref('')
const page = ref(1)
const fieldFilters = ref<Record<string, string>>({})

// Per-column search filters (client-side)
const filterTitle = ref('')
const filterShortDesc = ref('')
const filterSigner = ref('')
const filterDocNumber = ref('')

// The nomenklatura (category) whose documents this page lists.
const { data: catsData } = await useAsyncData(
  `archive-category-${categoryId.value}`,
  () => apiFetch<{ items: CategoryResponse[] }>('/api/categories'),
)
const category = computed(() => catsData.value?.items.find(c => c.id === categoryId.value) || null)
const categoryFields = computed(() => category.value?.fields || [])

// Reset page when filters change
watch([search, dateFrom, dateTo, filterTitle, filterShortDesc, filterSigner, filterDocNumber, fieldFilters], () => {
  page.value = 1
}, { deep: true })

const combinedSearch = computed(() => search.value || undefined)

const activeFieldFilters = computed(() => {
  const active: Record<string, string> = {}
  for (const [key, val] of Object.entries(fieldFilters.value)) {
    if (val && val.trim()) active[key] = val.trim()
  }
  return Object.keys(active).length > 0 ? active : undefined
})

// Fetch documents for this nomenklatura
const { data: docsData, status } = await useAsyncData(
  `docs-category-${categoryId.value}`,
  () => listDocuments({
    category_id: categoryId.value,
    search: combinedSearch.value,
    date_from: dateFrom.value || undefined,
    date_to: dateTo.value || undefined,
    page: page.value,
    field_filters: activeFieldFilters.value,
  }),
  { watch: [search, page, fieldFilters, dateFrom, dateTo], deep: true },
)

const allDocuments = computed(() => docsData.value?.items || [])
const documents = computed(() => {
  let docs = allDocuments.value
  if (filterTitle.value) {
    const q = filterTitle.value.toLowerCase()
    docs = docs.filter(d => d.title?.toLowerCase().includes(q))
  }
  if (filterShortDesc.value) {
    const q = filterShortDesc.value.toLowerCase()
    docs = docs.filter(d => d.short_desc?.toLowerCase().includes(q))
  }
  if (filterSigner.value) {
    const q = filterSigner.value.toLowerCase()
    docs = docs.filter(d => d.signer?.toLowerCase().includes(q))
  }
  if (filterDocNumber.value) {
    const q = filterDocNumber.value.toLowerCase()
    docs = docs.filter(d => d.document_number?.toLowerCase().includes(q))
  }
  return docs
})
const total = computed(() => docsData.value?.total || 0)

function formatDate(date: string) {
  if (!date) return '-'
  const parts = date.split('-')
  if (parts.length !== 3) return date
  return `${parts[2]}.${parts[1]}.${parts[0]}`
}

const columns = [
  { id: 'index', header: '№' },
  { accessorKey: 'title', header: 'Hujjat nomi' },
  { accessorKey: 'short_desc', header: 'Qisqacha tavsif' },
  { accessorKey: 'signer', header: 'Imzo' },
  { accessorKey: 'document_number', header: 'Tartib raqami' },
  { accessorKey: 'date', header: 'Qabul qilingan sana' },
]

const hasActiveFilters = computed(() =>
  !!search.value || !!dateFrom.value || !!dateTo.value
  || !!filterTitle.value || !!filterShortDesc.value || !!filterSigner.value || !!filterDocNumber.value
  || Object.values(fieldFilters.value).some(v => v?.trim())
)

function clearAllFilters() {
  search.value = ''
  dateFrom.value = ''
  dateTo.value = ''
  filterTitle.value = ''
  filterShortDesc.value = ''
  filterSigner.value = ''
  filterDocNumber.value = ''
  fieldFilters.value = {}
  page.value = 1
}
</script>

<template>
  <PagePanel :title="category?.name || 'Nomenklatura'" icon="i-lucide-folder">
    <template #headerLeft>
      <UButton icon="i-lucide-arrow-left" variant="ghost" to="/archive" />
    </template>
    <template #headerRight>
      <UBadge :label="`${total} hujjat`" variant="subtle" class="mr-2" />
      <UButton
        icon="i-lucide-plus"
        label="Yangi hujjat"
        @click="navigateTo(`/archive/${categoryId}/create`)"
      />
    </template>
    <template #toolbar>
      <UInput
        v-model="search"
        icon="i-lucide-search"
        placeholder="Umumiy qidirish..."
        class="w-64"
      />
      <UButton
        v-if="hasActiveFilters"
        icon="i-lucide-x"
        variant="ghost"
        color="error"
        size="sm"
        label="Tozalash"
        @click="clearAllFilters"
      />
    </template>

    <!-- Dynamic field filters -->
    <div v-if="categoryFields.length" class="border-b border-default px-5 py-2 bg-elevated/10">
      <div class="flex items-center gap-2 flex-wrap">
        <span class="text-xs text-muted font-medium shrink-0">Maydonlar:</span>
        <template v-for="field in categoryFields" :key="field.id">
          <UInput
            v-if="field.field_type === 'text' || field.field_type === 'textarea'"
            :model-value="fieldFilters[field.name] || ''"
            size="xs"
            icon="i-lucide-search"
            :placeholder="field.label"
            class="w-36"
            @update:model-value="fieldFilters[field.name] = $event"
          />
          <UInput
            v-else-if="field.field_type === 'number'"
            :model-value="fieldFilters[field.name] || ''"
            type="number"
            size="xs"
            icon="i-lucide-search"
            :placeholder="field.label"
            class="w-32"
            @update:model-value="fieldFilters[field.name] = $event"
          />
          <DatePicker
            v-else-if="field.field_type === 'date'"
            :model-value="fieldFilters[field.name] || ''"
            size="sm"
            @update:model-value="fieldFilters[field.name] = $event || ''"
          />
          <USelect
            v-else-if="field.field_type === 'select' && field.options"
            :model-value="fieldFilters[field.name] || ''"
            :items="field.options"
            size="xs"
            :placeholder="field.label"
            class="w-36"
            @update:model-value="fieldFilters[field.name] = $event"
          />
          <UInput
            v-else
            :model-value="fieldFilters[field.name] || ''"
            size="xs"
            icon="i-lucide-search"
            :placeholder="field.label"
            class="w-36"
            @update:model-value="fieldFilters[field.name] = $event"
          />
        </template>
      </div>
    </div>

    <UTable
      :data="documents"
      :columns="columns"
      :loading="status === 'pending'"
      class="w-full [&_th]:border [&_th]:border-default [&_td]:border [&_td]:border-default [&_th]:align-top"
    >
      <template #index-header>
        <div class="flex flex-col items-center gap-2">
          <span class="font-bold">№</span>
        </div>
      </template>
      <template #title-header>
        <div class="flex flex-col items-center gap-2">
          <span class="font-bold">Hujjat nomi</span>
          <UInput v-model="filterTitle" size="sm" placeholder="" class="w-full" />
        </div>
      </template>
      <template #short_desc-header>
        <div class="flex flex-col items-center gap-2">
          <span class="font-bold">Qisqacha tavsif</span>
          <UInput v-model="filterShortDesc" size="sm" placeholder="" class="w-full" />
        </div>
      </template>
      <template #signer-header>
        <div class="flex flex-col items-center gap-2">
          <span class="font-bold">Imzo</span>
          <UInput v-model="filterSigner" size="sm" placeholder="" class="w-full" />
        </div>
      </template>
      <template #document_number-header>
        <div class="flex flex-col items-center gap-1">
          <span class="font-bold">Tartib raqami</span>
          <UInput v-model="filterDocNumber" size="sm" placeholder="" class="w-full" />
        </div>
      </template>
      <template #date-header>
        <div class="flex flex-col items-center gap-2">
          <span class="font-bold">Qabul qilingan sana</span>
          <DatePicker v-model="dateFrom" size="sm" />
        </div>
      </template>

      <template #index-cell="{ row }">
        <span class="font-mono text-base font-semibold text-highlighted">{{ row.index + 1 + (page - 1) * 20 }}</span>
      </template>
      <template #title-cell="{ row }">
        <NuxtLink
          :to="`/archive/${categoryId}/${row.original.id}`"
          class="text-primary hover:underline font-semibold text-base"
        >
          {{ row.original.title }}
        </NuxtLink>
      </template>
      <template #short_desc-cell="{ row }">
        <span class="text-sm text-muted line-clamp-2">{{ row.original.short_desc || '-' }}</span>
      </template>
      <template #signer-cell="{ row }">
        <span class="text-base text-highlighted">{{ row.original.person_name || row.original.signer || '-' }}</span>
      </template>
      <template #document_number-cell="{ row }">
        <span class="font-mono text-base text-primary font-bold">{{ row.original.document_number }}</span>
      </template>
      <template #date-cell="{ row }">
        <span class="text-base text-highlighted whitespace-nowrap font-medium">{{ formatDate(row.original.date) }}</span>
      </template>
    </UTable>

    <div v-if="total > 20" class="flex justify-center p-4">
      <UPagination v-model:page="page" :total="total" :items-per-page="20" />
    </div>

    <div v-if="!documents.length && status !== 'pending'" class="flex items-center justify-center p-12">
      <EmptyState
        icon="i-lucide-file-x"
        title="Hujjatlar topilmadi"
        description="Bu nomenklaturada hujjatlar mavjud emas"
      />
    </div>
  </PagePanel>
</template>
