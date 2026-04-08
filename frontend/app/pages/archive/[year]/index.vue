<script setup lang="ts">
import type { CategoryResponse, DocumentResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const route = useRoute()
const year = computed(() => Number(route.params.year))

const { apiFetch } = useApi()
const { listDocuments, deleteDocument } = useDocuments()
const toast = useToast()

const selectedCategoryId = ref<string | undefined>(undefined)
const search = ref('')
const dateFrom = ref('')
const dateTo = ref('')
const page = ref(1)
const showFieldSearch = ref(false)
const fieldFilters = ref<Record<string, string>>({})
const deleteOpen = ref(false)
const deleteTarget = ref<DocumentResponse | null>(null)

// Create document modal - category selection
const createOpen = ref(false)
const createCategoryId = ref<string | undefined>(undefined)

// Fetch categories for this year
const { data: categoriesData } = await useAsyncData(
  `categories-${year.value}`,
  () => apiFetch<{ items: CategoryResponse[] }>(`/api/years/${year.value}/categories`)
)

const categories = computed(() => categoriesData.value?.items || [])
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

// Reset page when search/date changes
watch([search, dateFrom, dateTo], () => {
  page.value = 1
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
const { data: docsData, status, refresh } = await useAsyncData(
  `docs-year-${year.value}`,
  () => listDocuments({
    year_id: year.value,
    category_id: selectedCategoryId.value || undefined,
    search: search.value || undefined,
    date_from: dateFrom.value || undefined,
    date_to: dateTo.value || undefined,
    page: page.value,
    field_filters: activeFieldFilters.value,
  }),
  { watch: [search, page, selectedCategoryId, fieldFilters, dateFrom, dateTo] }
)

const documents = computed(() => docsData.value?.items || [])
const total = computed(() => docsData.value?.total || 0)

// Get category name for a document
function getCategoryName(catId: string) {
  return categories.value.find(c => c.id === catId)?.name || '-'
}

const columns = computed(() => {
  const cols: Array<{ accessorKey?: string; id?: string; header: string }> = [
    { accessorKey: 'document_number', header: 'Raqam' },
    { accessorKey: 'title', header: 'Sarlavha' },
  ]
  if (!selectedCategoryId.value) {
    cols.push({ accessorKey: 'category_id', header: 'Nomenklatura' })
  }
  cols.push(
    { accessorKey: 'date', header: 'Sana' },
    { accessorKey: 'signer', header: 'Imzo' },
    { id: 'actions', header: '' },
  )
  return cols
})

function confirmDelete(doc: DocumentResponse) {
  deleteTarget.value = doc
  deleteOpen.value = true
}

async function handleDelete() {
  if (!deleteTarget.value) return
  try {
    await deleteDocument(deleteTarget.value.id)
    toast.add({ title: 'Muvaffaqiyat', description: 'Hujjat o\'chirildi', color: 'success', icon: 'i-lucide-check-circle' })
    deleteOpen.value = false
    refresh()
  } catch {
    toast.add({ title: 'Xatolik', description: 'Hujjatni o\'chirib bo\'lmadi', color: 'error', icon: 'i-lucide-alert-circle' })
  }
}

function toggleFieldSearch() {
  showFieldSearch.value = !showFieldSearch.value
  if (!showFieldSearch.value) {
    fieldFilters.value = {}
  }
}
</script>

<template>
  <PagePanel :title="`${year} yil`" icon="i-lucide-calendar">
    <template #headerLeft>
      <UButton icon="i-lucide-arrow-left" variant="ghost" to="/archive" />
    </template>
    <template #headerRight>
      <UBadge :label="`${total} hujjat`" variant="subtle" class="mr-2" />
      <UButton
        icon="i-lucide-plus"
        label="Yangi hujjat"
        @click="selectedCategoryId ? navigateTo(`/archive/${year}/${selectedCategoryId}/create`) : (createCategoryId = undefined, createOpen = true)"
      />
    </template>
    <template #toolbar>
      <USelect
        v-model="selectedCategoryId"
        :items="categoryItems"
        placeholder="Nomenklatura"
        icon="i-lucide-folder"
        class="w-56"
      />
      <UInput
        v-model="search"
        icon="i-lucide-search"
        placeholder="Qidirish..."
        class="w-64"
      />
      <DatePicker v-model="dateFrom" placeholder="Sanadan" size="sm" />
      <DatePicker v-model="dateTo" placeholder="Sanagacha" size="sm" />
      <UButton
        v-if="selectedCategoryId && categoryFields.length"
        :icon="showFieldSearch ? 'i-lucide-filter-x' : 'i-lucide-filter'"
        :variant="showFieldSearch ? 'soft' : 'ghost'"
        size="sm"
        :label="showFieldSearch ? 'Filtrni yopish' : 'Maydon filtri'"
        @click="toggleFieldSearch"
      />
    </template>

    <!-- Field filters panel -->
    <div v-if="showFieldSearch && categoryFields.length" class="border-b border-default px-5 py-3 bg-elevated/20">
      <p class="text-xs text-muted mb-2 font-medium">Maydonlar bo'yicha qidirish:</p>
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
        <div v-for="field in categoryFields" :key="field.id">
          <label class="text-xs text-muted mb-1 block">{{ field.label }}</label>
          <UInput
            v-if="field.field_type === 'text' || field.field_type === 'textarea'"
            :model-value="fieldFilters[field.name] || ''"
            size="sm"
            :placeholder="field.placeholder || field.label"
            @update:model-value="fieldFilters[field.name] = $event"
          />
          <UInput
            v-else-if="field.field_type === 'number'"
            :model-value="fieldFilters[field.name] || ''"
            type="number"
            size="sm"
            :placeholder="field.placeholder || field.label"
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
            size="sm"
            :placeholder="field.label"
            @update:model-value="fieldFilters[field.name] = $event"
          />
          <UInput
            v-else
            :model-value="fieldFilters[field.name] || ''"
            size="sm"
            :placeholder="field.placeholder || field.label"
            @update:model-value="fieldFilters[field.name] = $event"
          />
        </div>
      </div>
    </div>

    <UTable
      :data="documents"
      :columns="columns"
      :loading="status === 'pending'"
      class="w-full"
      @select="(row: any) => navigateTo(`/archive/${year}/${row.original.category_id}/${row.original.id}`)"
    >
      <template #document_number-cell="{ row }">
        <span class="font-mono text-primary font-semibold">
          {{ row.original.document_number }}
        </span>
      </template>
      <template #title-cell="{ row }">
        <span class="text-highlighted">
          {{ row.original.title }}
        </span>
      </template>
      <template #category_id-cell="{ row }">
        <UBadge :label="getCategoryName(row.original.category_id)" variant="subtle" color="neutral" />
      </template>
      <template #actions-cell="{ row }">
        <div class="flex justify-end">
          <UDropdownMenu :items="[
            [
              { label: 'Ko\'rish', icon: 'i-lucide-eye', onSelect: () => navigateTo(`/archive/${year}/${row.original.category_id}/${row.original.id}`) },
              { label: 'Tahrirlash', icon: 'i-lucide-pencil', onSelect: () => navigateTo(`/archive/${year}/${row.original.category_id}/${row.original.id}/edit`) },
            ],
            [
              { label: 'O\'chirish', icon: 'i-lucide-trash-2', color: 'error', onSelect: () => confirmDelete(row.original) },
            ],
          ]">
            <UButton icon="i-lucide-ellipsis-vertical" variant="ghost" size="xs" />
          </UDropdownMenu>
        </div>
      </template>
    </UTable>

    <div v-if="total > 20" class="flex justify-center p-4">
      <UPagination v-model:page="page" :total="total" :items-per-page="20" />
    </div>

    <div v-if="!documents.length && status !== 'pending'" class="flex items-center justify-center p-12">
      <EmptyState
        icon="i-lucide-file-x"
        title="Hujjatlar topilmadi"
        :description="selectedCategoryId ? 'Bu kategoriyada hujjatlar mavjud emas' : `${year} yil uchun hujjatlar mavjud emas`"
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

  <!-- Delete confirmation -->
  <UModal v-model:open="deleteOpen" title="Hujjatni o'chirish" description="Haqiqatan ham bu hujjatni o'chirmoqchimisiz? Bu amalni qaytarib bo'lmaydi.">
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton variant="ghost" label="Bekor qilish" @click="deleteOpen = false" />
        <UButton color="error" label="O'chirish" icon="i-lucide-trash-2" @click="handleDelete" />
      </div>
    </template>
  </UModal>
</template>
