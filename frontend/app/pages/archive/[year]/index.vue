<script setup lang="ts">
import type { CategoryResponse, YearResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const route = useRoute()
const isAllYears = computed(() => route.params.year === 'all')
const year = computed(() => isAllYears.value ? null : Number(route.params.year))

const { apiFetch } = useApi()
const { listDocuments } = useDocuments()

const selectedCategoryId = ref<string | undefined>(undefined)
const selectedYearFilter = ref<number | undefined>(undefined)
const search = ref('')
const dateFrom = ref('')
const dateTo = ref('')
const page = ref(1)
const fieldFilters = ref<Record<string, string>>({})

// Per-column search filters
const filterTitle = ref('')
const filterShortDesc = ref('')
const filterSigner = ref('')
const filterDocNumber = ref('')
const filterArchiveNumber = ref('')

// Create document modal - category selection
const createOpen = ref(false)
const createCategoryId = ref<string | undefined>(undefined)

// Fetch years list (for "all" mode year filter)
const { data: yearsData } = await useAsyncData(
  'all-years',
  () => apiFetch<{ items: YearResponse[] }>('/api/years'),
  { immediate: isAllYears.value }
)
const yearItems = computed(() =>
  (yearsData.value?.items || []).map(y => ({ label: String(y.value), value: y.value }))
)

// Fetch categories — all or per year
const { data: categoriesData } = await useAsyncData(
  `categories-${year.value ?? 'all'}`,
  () => isAllYears.value
    ? apiFetch<{ items: CategoryResponse[] }>('/api/categories')
    : apiFetch<{ items: CategoryResponse[] }>(`/api/years/${year.value}/categories`)
)

const allCategories = computed(() => categoriesData.value?.items || [])
const categories = computed(() => {
  if (isAllYears.value && selectedYearFilter.value) {
    const yearObj = yearsData.value?.items.find(y => y.value === selectedYearFilter.value)
    if (yearObj) return allCategories.value.filter(c => c.year_id === yearObj.id)
  }
  return allCategories.value
})
const categoryItems = computed(() =>
  categories.value.map(c => ({ label: c.name, value: c.id }))
)

// Selected category's fields (for field search)
const selectedCategory = computed(() =>
  categories.value.find(c => c.id === selectedCategoryId.value) || null
)
const categoryFields = computed(() => selectedCategory.value?.fields || [])

// Reset page and field filters when category changes
watch(selectedCategoryId, () => {
  page.value = 1
  fieldFilters.value = {}
})

// Reset category and page when year filter changes (all-years mode)
watch(selectedYearFilter, () => {
  selectedCategoryId.value = undefined
  page.value = 1
  fieldFilters.value = {}
})

// Reset page when any filter changes
watch([search, dateFrom, dateTo, filterTitle, filterShortDesc, filterSigner, filterDocNumber, filterArchiveNumber], () => {
  page.value = 1
})

// Combine all text searches into one search string for the API
const combinedSearch = computed(() => {
  // The main search box searches across all fields via backend `search` param
  // Column-specific filters are client-side or we pass the main one
  return search.value || undefined
})

// Build active field filters (exclude empty values)
const activeFieldFilters = computed(() => {
  const active: Record<string, string> = {}
  for (const [key, val] of Object.entries(fieldFilters.value)) {
    if (val && val.trim()) active[key] = val.trim()
  }
  return Object.keys(active).length > 0 ? active : undefined
})

// Fetch documents
const { data: docsData, status } = await useAsyncData(
  `docs-year-${year.value ?? 'all'}`,
  () => listDocuments({
    year_id: isAllYears.value ? (selectedYearFilter.value || undefined) : year.value!,
    category_id: selectedCategoryId.value || undefined,
    search: combinedSearch.value,
    date_from: dateFrom.value || undefined,
    date_to: dateTo.value || undefined,
    page: page.value,
    field_filters: activeFieldFilters.value,
  }),
  { watch: [search, page, selectedCategoryId, fieldFilters, dateFrom, dateTo, selectedYearFilter] }
)

// Client-side filtering for per-column searches
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
  if (filterArchiveNumber.value) {
    const q = filterArchiveNumber.value.toLowerCase()
    docs = docs.filter(d => d.archive_number?.toLowerCase().includes(q))
  }
  return docs
})
const total = computed(() => docsData.value?.total || 0)

// Get category name for a document
function getCategoryName(catId: string) {
  return allCategories.value.find(c => c.id === catId)?.name || '-'
}

// Get year value for a document — year_id in response IS the year value (e.g. 2020)
function getYearValue(yearId: number) {
  return yearId
}

// Format date from YYYY-MM-DD to DD.MM.YYYY
function formatDate(date: string) {
  if (!date) return '-'
  const parts = date.split('-')
  if (parts.length !== 3) return date
  return `${parts[2]}.${parts[1]}.${parts[0]}`
}

const columns = computed(() => {
  const cols: Array<{ accessorKey?: string; id?: string; header: string }> = [
    { id: 'index', header: '№' },
    { accessorKey: 'title', header: 'Hujjat nomi' },
    { accessorKey: 'short_desc', header: 'Qisqacha tavsif' },
  ]
  if (isAllYears.value && !selectedYearFilter.value) {
    cols.push({ accessorKey: 'year_id', header: 'Yil' })
  }
  if (!selectedCategoryId.value) {
    cols.push({ accessorKey: 'category_id', header: 'Nomenklatura' })
  }
  cols.push(
    { accessorKey: 'signer', header: 'Imzo' },
    { accessorKey: 'document_number', header: 'Tartib raqami' },
    { accessorKey: 'archive_number', header: 'Arxiv tartib raqami' },
    { accessorKey: 'date', header: 'Qabul qilingan sana' },
  )
  return cols
})

const hasActiveFilters = computed(() =>
  !!selectedCategoryId.value || !!selectedYearFilter.value || !!search.value || !!dateFrom.value || !!dateTo.value
  || !!filterTitle.value || !!filterShortDesc.value || !!filterSigner.value || !!filterDocNumber.value || !!filterArchiveNumber.value
  || Object.values(fieldFilters.value).some(v => v?.trim())
)

function clearAllFilters() {
  selectedCategoryId.value = undefined
  selectedYearFilter.value = undefined
  search.value = ''
  dateFrom.value = ''
  dateTo.value = ''
  filterTitle.value = ''
  filterShortDesc.value = ''
  filterSigner.value = ''
  filterDocNumber.value = ''
  filterArchiveNumber.value = ''
  fieldFilters.value = {}
  page.value = 1
}
</script>

<template>
  <PagePanel :title="isAllYears ? 'Barcha yillar' : `${year} yil`" :icon="isAllYears ? 'i-lucide-layers' : 'i-lucide-calendar'">
    <template #headerLeft>
      <UButton icon="i-lucide-arrow-left" variant="ghost" to="/archive" />
    </template>
    <template #headerRight>
      <UBadge :label="`${total} hujjat`" variant="subtle" class="mr-2" />
      <UButton
        v-if="!isAllYears"
        icon="i-lucide-plus"
        label="Yangi hujjat"
        @click="selectedCategoryId ? navigateTo(`/archive/${year}/${selectedCategoryId}/create`) : (createCategoryId = undefined, createOpen = true)"
      />
    </template>
    <template #toolbar>
      <USelect
        v-if="isAllYears"
        v-model="selectedYearFilter"
        :items="yearItems"
        placeholder="Yil"
        icon="i-lucide-calendar"
        class="w-36"
      />
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

    <!-- Dynamic field filters (when category selected) -->
    <div v-if="selectedCategoryId && categoryFields.length" class="border-b border-default px-5 py-2 bg-elevated/10">
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
      <!-- Header slots with search inputs -->
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
      <template #year_id-header>
        <div class="flex flex-col items-center gap-2">
          <span class="font-bold">Yil</span>
        </div>
      </template>
      <template #category_id-header>
        <div class="flex flex-col items-center gap-1">
          <span class="font-bold">Nomenklatura</span>
          <USelectMenu
            v-model="selectedCategoryId"
            value-key="value"
            :items="categoryItems"
            :search-input="{ placeholder: 'Qidirish...' }"
            placeholder="Barchasi"
            size="sm"
            class="w-full"
          />
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
      <template #archive_number-header>
        <div class="flex flex-col items-center gap-1">
          <span class="font-bold">Arxiv tartib raqami</span>
          <UInput v-model="filterArchiveNumber" size="sm" placeholder="" class="w-full" />
        </div>
      </template>
      <template #date-header>
        <div class="flex flex-col items-center gap-2">
          <span class="font-bold">Qabul qilingan sana</span>
          <DatePicker v-model="dateFrom" size="sm" />
        </div>
      </template>

      <!-- Cell slots -->
      <template #index-cell="{ row }">
        <span class="font-mono text-base font-semibold text-highlighted">{{ row.index + 1 + (page - 1) * 20 }}</span>
      </template>
      <template #title-cell="{ row }">
        <NuxtLink
          :to="`/archive/${isAllYears ? getYearValue(row.original.year_id) : year}/${row.original.category_id}/${row.original.id}`"
          class="text-primary hover:underline font-semibold text-base"
        >
          {{ row.original.title }}
        </NuxtLink>
      </template>
      <template #short_desc-cell="{ row }">
        <span class="text-sm text-muted line-clamp-2">{{ row.original.short_desc || '-' }}</span>
      </template>
      <template #year_id-cell="{ row }">
        <UBadge :label="String(getYearValue(row.original.year_id))" variant="subtle" color="primary" size="md" />
      </template>
      <template #category_id-cell="{ row }">
        <UBadge :label="getCategoryName(row.original.category_id)" variant="subtle" color="neutral" size="md" />
      </template>
      <template #signer-cell="{ row }">
        <span class="text-base text-highlighted">{{ row.original.person_name || row.original.signer || '-' }}</span>
      </template>
      <template #document_number-cell="{ row }">
        <span class="font-mono text-base text-primary font-bold">{{ row.original.document_number }}</span>
      </template>
      <template #archive_number-cell="{ row }">
        <span class="font-mono text-base text-highlighted">{{ row.original.archive_number || '-' }}</span>
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
        :description="selectedCategoryId ? 'Bu kategoriyada hujjatlar mavjud emas' : isAllYears ? 'Hujjatlar topilmadi' : `${year} yil uchun hujjatlar mavjud emas`"
      />
    </div>
  </PagePanel>

  <!-- Category select for new document -->
  <UModal v-model:open="createOpen" title="Nomenklaturani tanlang">
    <template #body>
      <div class="space-y-3">
        <p class="text-sm text-muted">Hujjat qaysi nomenklaturaga tegishli?</p>
        <div class="flex flex-col gap-2">
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
        <div v-if="!categories.length" class="text-sm text-muted text-center py-4">
          Bu yil uchun nomenklaturalar topilmadi
        </div>
      </div>
    </template>
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton variant="outline" label="Bekor qilish" @click="createOpen = false" />
        <UButton
          label="Davom etish"
          icon="i-lucide-arrow-right"
          :disabled="!createCategoryId"
          @click="createOpen = false; navigateTo(`/archive/${year}/${createCategoryId}/create`)"
        />
      </div>
    </template>
  </UModal>

</template>
