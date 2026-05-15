<script setup lang="ts">
import type {
  ArchiveFolderResponse,
  CategoryResponse,
  DocumentTypeResponse,
  SearchFilters,
  SearchHit,
  SearchResponse,
  SearchSort,
  YearResponse,
} from '~/types'

definePageMeta({ layout: 'dashboard' })

const route = useRoute()
const router = useRouter()
const { apiFetch } = useApi()
const { search } = useSearch()

// ─── URL-backed reactive state (refresh-safe deep links) ──────────────────
const q = ref(typeof route.query.q === 'string' ? route.query.q : '')
const sort = ref<SearchSort>(
  (typeof route.query.sort === 'string' && ['relevance', 'date_desc', 'date_asc'].includes(route.query.sort))
    ? (route.query.sort as SearchSort)
    : 'relevance',
)
const page = ref(Number(route.query.page) || 1)

function readListParam(name: string): string[] {
  const v = route.query[name]
  if (!v) return []
  return Array.isArray(v) ? v.map(String) : String(v).split(',').filter(Boolean)
}
function readNumberList(name: string): number[] {
  return readListParam(name).map(Number).filter(n => !isNaN(n))
}

const yearFilter = ref<number[]>(readNumberList('year_value'))
const categoryFilter = ref<string[]>(readListParam('category_id'))
const viewFilter = ref<string[]>(readListParam('document_view'))
const typeFilter = ref<string[]>(readListParam('document_type_id'))
const folderFilter = ref<string[]>(readListParam('archive_folder_id'))
const dateFrom = ref<string>(typeof route.query.date_from === 'string' ? route.query.date_from : '')
const dateTo = ref<string>(typeof route.query.date_to === 'string' ? route.query.date_to : '')

// Sync state → URL so refresh preserves filters and snippets are shareable.
function syncUrl() {
  router.replace({
    query: {
      ...(q.value ? { q: q.value } : {}),
      ...(yearFilter.value.length ? { year_value: yearFilter.value.join(',') } : {}),
      ...(categoryFilter.value.length ? { category_id: categoryFilter.value.join(',') } : {}),
      ...(viewFilter.value.length ? { document_view: viewFilter.value.join(',') } : {}),
      ...(typeFilter.value.length ? { document_type_id: typeFilter.value.join(',') } : {}),
      ...(folderFilter.value.length ? { archive_folder_id: folderFilter.value.join(',') } : {}),
      ...(dateFrom.value ? { date_from: dateFrom.value } : {}),
      ...(dateTo.value ? { date_to: dateTo.value } : {}),
      ...(sort.value !== 'relevance' ? { sort: sort.value } : {}),
      ...(page.value > 1 ? { page: String(page.value) } : {}),
    },
  })
}

// ─── Reference data for filter labels + facet rendering ───────────────────
const { data: years } = await useAsyncData('search-years', () => apiFetch<{ items: YearResponse[] }>('/api/years'))
const { data: categories } = await useAsyncData('search-categories', () => apiFetch<{ items: CategoryResponse[] }>('/api/categories'))
const { data: docTypes } = await useAsyncData('search-doc-types', () => apiFetch<{ items: DocumentTypeResponse[] }>('/api/document-types'))
const { data: folders } = await useAsyncData('search-folders', () => apiFetch<{ items: ArchiveFolderResponse[] }>('/api/archive-folders'))

const yearOptions = computed(() => (years.value?.items || []).map(y => ({ label: String(y.value), value: y.value })))
const categoryById = computed(() => Object.fromEntries((categories.value?.items || []).map(c => [c.id, c.name])))
const docTypeById = computed(() => Object.fromEntries((docTypes.value?.items || []).map(d => [d.id, d.name])))
const folderById = computed(() => Object.fromEntries((folders.value?.items || []).map(f => [f.id, `${f.index_code} — ${f.title}`])))

const categoryOptions = computed(() => (categories.value?.items || []).map(c => ({ label: c.name, value: c.id })))
const docTypeOptions = computed(() => (docTypes.value?.items || []).map(d => ({ label: d.name, value: d.id })))
const folderOptions = computed(() => (folders.value?.items || []).map(f => ({ label: `${f.index_code} — ${f.title}`, value: f.id })))

const viewOptions = [
  { label: DOCUMENT_VIEW_LABELS.incoming, value: 'incoming' },
  { label: DOCUMENT_VIEW_LABELS.outgoing, value: 'outgoing' },
  { label: DOCUMENT_VIEW_LABELS.internal, value: 'internal' },
  { label: DOCUMENT_VIEW_LABELS.appeal, value: 'appeal' },
]
const sortOptions = [
  { label: 'Aniqlik bo\'yicha', value: 'relevance' as SearchSort },
  { label: 'Sana (yangidan eskigacha)', value: 'date_desc' as SearchSort },
  { label: 'Sana (eskidan yangigacha)', value: 'date_asc' as SearchSort },
]

// ─── Search state ─────────────────────────────────────────────────────────
const result = ref<SearchResponse | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const debounceTimer = ref<ReturnType<typeof setTimeout> | null>(null)

function buildFilters(): SearchFilters {
  return {
    ...(yearFilter.value.length ? { year_value: [...yearFilter.value] } : {}),
    ...(categoryFilter.value.length ? { category_id: [...categoryFilter.value] } : {}),
    ...(viewFilter.value.length ? { document_view: [...viewFilter.value] } : {}),
    ...(typeFilter.value.length ? { document_type_id: [...typeFilter.value] } : {}),
    ...(folderFilter.value.length ? { archive_folder_id: [...folderFilter.value] } : {}),
    ...(dateFrom.value ? { date_from: dateFrom.value } : {}),
    ...(dateTo.value ? { date_to: dateTo.value } : {}),
  }
}

async function runSearch() {
  loading.value = true
  error.value = null
  try {
    const r = await search({
      q: q.value || undefined,
      filters: buildFilters(),
      facets: ['year_value', 'category_id', 'document_view', 'document_type_id', 'archive_folder_id'],
      page: page.value,
      page_size: 20,
      sort: sort.value,
    })
    result.value = r
  } catch (e: any) {
    if (e?.name === 'AbortError') return
    error.value = e?.data?.detail || e?.message || 'Qidiruv xatosi'
  } finally {
    loading.value = false
  }
}

function scheduleSearch(immediate = false) {
  if (debounceTimer.value) clearTimeout(debounceTimer.value)
  if (immediate) {
    runSearch()
  } else {
    debounceTimer.value = setTimeout(runSearch, 300)
  }
}

// Reset to page 1 whenever query/filters change.
watch([q, yearFilter, categoryFilter, viewFilter, typeFilter, folderFilter, dateFrom, dateTo, sort], () => {
  page.value = 1
  syncUrl()
  scheduleSearch()
}, { deep: true })

watch(page, () => {
  syncUrl()
  scheduleSearch(true)
})

onMounted(() => {
  // Autofocus the search box and run an immediate search reflecting URL state.
  searchInputRef.value?.input?.focus?.()
  scheduleSearch(true)
})

const searchInputRef = ref<any>(null)

// ─── Facet helpers ────────────────────────────────────────────────────────
function facetCount(field: string, value: string | number): number | null {
  const buckets = result.value?.facets?.[field]
  if (!buckets) return null
  const hit = buckets.find(b => String(b.value) === String(value))
  return hit ? hit.count : 0
}

const hasFilters = computed(() =>
  !!q.value || !!dateFrom.value || !!dateTo.value
  || yearFilter.value.length || categoryFilter.value.length
  || viewFilter.value.length || typeFilter.value.length || folderFilter.value.length,
)
function clearAll() {
  q.value = ''
  yearFilter.value = []
  categoryFilter.value = []
  viewFilter.value = []
  typeFilter.value = []
  folderFilter.value = []
  dateFrom.value = ''
  dateTo.value = ''
  sort.value = 'relevance'
  page.value = 1
}

// ─── Result rendering helpers ─────────────────────────────────────────────
function formatDate(iso: string | null): string {
  if (!iso) return '—'
  const parts = iso.split('T')[0]?.split('-')
  if (!parts || parts.length !== 3) return iso
  return `${parts[2]}.${parts[1]}.${parts[0]}`
}

function firstSnippet(hit: SearchHit): string | null {
  const h = hit.highlights
  return h.title?.[0] || h.short_desc?.[0] || h.extracted_text?.[0] || h.attachments?.[0] || h.note?.[0] || null
}

function totalLabel(total: number, took: number): string {
  return `${total} ta natija topildi (${took} ms)`
}

const total = computed(() => result.value?.total ?? 0)
const items = computed(() => result.value?.items ?? [])
const totalPages = computed(() => Math.ceil(total.value / 20))
</script>

<template>
  <PagePanel title="Kengaytirilgan qidiruv" icon="i-lucide-search">
    <template #headerLeft>
      <UButton icon="i-lucide-arrow-left" variant="ghost" to="/archive" />
    </template>
    <template #toolbar>
      <UInput
        ref="searchInputRef"
        v-model="q"
        icon="i-lucide-search"
        placeholder="Hujjatlarda qidirish..."
        class="w-96"
        size="lg"
        autofocus
      />
      <USelect v-model="sort" :items="sortOptions" value-key="value" class="w-56" size="lg" />
      <UButton
        v-if="hasFilters"
        icon="i-lucide-x"
        variant="ghost"
        color="error"
        size="md"
        label="Tozalash"
        @click="clearAll"
      />
    </template>

    <div class="flex h-full overflow-hidden">
      <!-- Filters panel -->
      <aside class="w-72 shrink-0 border-r border-default overflow-y-auto p-4 space-y-5 bg-elevated/20">
        <!-- Year -->
        <div>
          <h3 class="text-xs font-bold uppercase text-muted mb-2">Yil</h3>
          <div class="space-y-1">
            <label
              v-for="opt in yearOptions"
              :key="opt.value"
              class="flex items-center gap-2 text-sm cursor-pointer hover:text-highlighted"
            >
              <UCheckbox
                :model-value="yearFilter.includes(opt.value)"
                @update:model-value="v => v ? yearFilter.push(opt.value) : (yearFilter = yearFilter.filter(x => x !== opt.value))"
              />
              <span class="flex-1">{{ opt.label }}</span>
              <UBadge
                v-if="facetCount('year_value', opt.value) !== null"
                :label="String(facetCount('year_value', opt.value))"
                variant="soft"
                size="xs"
                color="neutral"
              />
            </label>
          </div>
        </div>

        <!-- Document view -->
        <div>
          <h3 class="text-xs font-bold uppercase text-muted mb-2">{{ LABELS.document_view }}</h3>
          <div class="space-y-1">
            <label
              v-for="opt in viewOptions"
              :key="opt.value"
              class="flex items-center gap-2 text-sm cursor-pointer hover:text-highlighted"
            >
              <UCheckbox
                :model-value="viewFilter.includes(opt.value)"
                @update:model-value="v => v ? viewFilter.push(opt.value) : (viewFilter = viewFilter.filter(x => x !== opt.value))"
              />
              <span class="flex-1">{{ opt.label }}</span>
              <UBadge
                v-if="facetCount('document_view', opt.value) !== null"
                :label="String(facetCount('document_view', opt.value))"
                variant="soft"
                size="xs"
                color="neutral"
              />
            </label>
          </div>
        </div>

        <!-- Date range -->
        <div>
          <h3 class="text-xs font-bold uppercase text-muted mb-2">Sana oralig'i</h3>
          <div class="space-y-2">
            <DatePicker v-model="dateFrom" placeholder="Boshlanish" size="sm" />
            <DatePicker v-model="dateTo" placeholder="Tugash" size="sm" />
          </div>
        </div>

        <!-- Category -->
        <div v-if="categoryOptions.length">
          <h3 class="text-xs font-bold uppercase text-muted mb-2">Nomenklatura</h3>
          <USelectMenu
            v-model="categoryFilter"
            :items="categoryOptions"
            value-key="value"
            multiple
            :search-input="{ placeholder: 'Qidirish...' }"
            placeholder="Barchasi"
            size="sm"
            class="w-full"
          />
        </div>

        <!-- Document type -->
        <div v-if="docTypeOptions.length">
          <h3 class="text-xs font-bold uppercase text-muted mb-2">Hujjat turi</h3>
          <USelectMenu
            v-model="typeFilter"
            :items="docTypeOptions"
            value-key="value"
            multiple
            :search-input="{ placeholder: 'Qidirish...' }"
            placeholder="Barchasi"
            size="sm"
            class="w-full"
          />
        </div>

        <!-- Archive folder -->
        <div v-if="folderOptions.length">
          <h3 class="text-xs font-bold uppercase text-muted mb-2">{{ LABELS.archive_folder }}</h3>
          <USelectMenu
            v-model="folderFilter"
            :items="folderOptions"
            value-key="value"
            multiple
            :search-input="{ placeholder: 'Qidirish...' }"
            placeholder="Barchasi"
            size="sm"
            class="w-full"
          />
        </div>
      </aside>

      <!-- Results -->
      <div class="flex-1 overflow-y-auto">
        <div class="p-5 max-w-4xl mx-auto">
          <!-- Stats -->
          <div v-if="result && !loading" class="mb-4 text-sm text-muted">
            {{ totalLabel(total, result.took_ms) }}
          </div>

          <!-- Error -->
          <UAlert
            v-if="error"
            color="error"
            variant="soft"
            :title="error"
            class="mb-4"
          />

          <!-- Skeleton -->
          <div v-if="loading && !result" class="space-y-3">
            <USkeleton v-for="i in 5" :key="i" class="h-28 w-full rounded-xl" />
          </div>

          <!-- Empty state -->
          <EmptyState
            v-else-if="!loading && total === 0"
            icon="i-lucide-search-x"
            title="Natija topilmadi"
            :description="hasFilters ? 'Filtrlar yoki qidiruv so\'rovini o\'zgartirib ko\'ring' : 'Qidiruv so\'rovini kiriting'"
          />

          <!-- Results -->
          <div v-else class="space-y-3">
            <article
              v-for="hit in items"
              :key="hit.id"
              class="border border-default rounded-xl p-4 hover:bg-elevated/30 transition-colors"
            >
              <div class="flex items-start gap-3">
                <UIcon name="i-lucide-file-text" class="text-primary shrink-0 text-xl mt-0.5" />
                <div class="flex-1 min-w-0">
                  <NuxtLink
                    v-if="hit.year_value && hit.category_id"
                    :to="`/archive/${hit.year_value}/${hit.category_id}/${hit.id}`"
                    class="text-base font-semibold text-primary hover:underline"
                  >
                    <span v-if="hit.highlights.title?.[0]" v-html="hit.highlights.title[0]" />
                    <span v-else>{{ hit.title || '—' }}</span>
                  </NuxtLink>
                  <p
                    v-if="firstSnippet(hit) && !hit.highlights.title?.[0]"
                    class="text-sm text-muted line-clamp-2 mt-1"
                    v-html="firstSnippet(hit)"
                  />
                  <p
                    v-else-if="hit.highlights.short_desc?.[0]"
                    class="text-sm text-muted line-clamp-2 mt-1"
                    v-html="hit.highlights.short_desc[0]"
                  />
                  <p
                    v-else-if="hit.short_desc"
                    class="text-sm text-muted line-clamp-2 mt-1"
                  >{{ hit.short_desc }}</p>

                  <!-- Attachment snippet -->
                  <div
                    v-if="hit.highlights.attachments?.[0]"
                    class="mt-2 pl-3 border-l-2 border-primary/30"
                  >
                    <p class="text-xs text-muted mb-0.5 flex items-center gap-1">
                      <UIcon name="i-lucide-paperclip" class="text-xs" />
                      Ilovadan
                    </p>
                    <p class="text-sm" v-html="hit.highlights.attachments[0]" />
                  </div>

                  <!-- Metadata badges -->
                  <div class="flex flex-wrap items-center gap-2 mt-3">
                    <UBadge
                      v-if="hit.year_value"
                      :label="String(hit.year_value)"
                      variant="subtle"
                      size="xs"
                      icon="i-lucide-calendar"
                    />
                    <UBadge
                      v-if="hit.document_view && hit.document_view !== 'unknown'"
                      :label="DOCUMENT_VIEW_LABELS[hit.document_view as keyof typeof DOCUMENT_VIEW_LABELS] || hit.document_view"
                      variant="subtle"
                      size="xs"
                      color="primary"
                    />
                    <UBadge
                      v-if="hit.category_name"
                      :label="hit.category_name"
                      variant="subtle"
                      size="xs"
                      color="neutral"
                    />
                    <UBadge
                      v-if="hit.document_type_name"
                      :label="hit.document_type_name"
                      variant="subtle"
                      size="xs"
                      color="neutral"
                    />
                    <UBadge
                      v-if="hit.document_number"
                      :label="hit.document_number"
                      variant="outline"
                      size="xs"
                      color="neutral"
                    />
                    <span class="text-xs text-muted ml-auto">{{ formatDate(hit.date) }}</span>
                  </div>
                </div>
              </div>
            </article>
          </div>

          <!-- Pagination -->
          <div v-if="totalPages > 1" class="flex justify-center mt-6">
            <UPagination v-model:page="page" :total="total" :items-per-page="20" />
          </div>
        </div>
      </div>
    </div>
  </PagePanel>
</template>
