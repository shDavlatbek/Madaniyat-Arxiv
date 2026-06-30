<script setup lang="ts">
import type {
  MusicSchoolResponse,
  MusicSchoolDocumentResponse,
  MusicSchoolSearchRequest,
  MusicSchoolSearchFilters,
} from '~/types'
import {
  LABELS,
  OCR_STATUS_LABELS,
  OCR_STATUS_COLORS,
  OCR_STATUS_ICONS,
} from '~/utils/labels'

definePageMeta({ layout: 'dashboard' })

const { isAdmin, isMusicSchool, musicSchoolId } = useAuth()
const {
  listSchools,
  searchDocuments,
  getDocument,
  createDocument,
  updateDocument,
  deleteDocument,
  uploadFile,
  listSpecialties,
} = useMusicSchool()
const toast = useToast()
const config = useRuntimeConfig()

// --- UI / Navigation States ---
const listLoading = ref(false)
const documents = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const page_size = 20

// --- Search & Filter States ---
const q = ref('')
const selectedSchoolId = ref<string>('')
const specialtyFilter = ref('')
const graduationYearFilter = ref<number | null>(null)
const dateFrom = ref('')
const dateTo = ref('')
const sort = ref('date_desc')

// --- Modal & Progress States ---
const specialtiesModalOpen = ref(false)
const uploadProgress = ref(false)

// --- Reference Data ---
const schools = ref<MusicSchoolResponse[]>([])
const schoolOptions = computed(() =>
  schools.value.map(s => ({ label: s.name, value: s.id }))
)

async function fetchSchools() {
  if (isAdmin.value) {
    try {
      const res = await listSchools()
      schools.value = res.items
    } catch (err) {
      console.error('Maktablar ro‘yxatini yuklashda xatolik:', err)
    }
  }
}

// --- Multi-Tenancy Resolution ---
const activeSchoolId = computed(() => {
  if (isMusicSchool.value) {
    return musicSchoolId.value || ''
  }
  return selectedSchoolId.value
})

// --- Main Search & Query Execution ---
async function runSearch() {
  listLoading.value = true
  try {
    const filters: MusicSchoolSearchFilters = {}

    // Lock query to user's school if role is music_school
    if (isMusicSchool.value && musicSchoolId.value) {
      filters.music_school_id = [musicSchoolId.value]
    } else if (selectedSchoolId.value) {
      filters.music_school_id = [selectedSchoolId.value]
    }

    if (graduationYearFilter.value) {
      filters.graduation_year = [graduationYearFilter.value]
    }

    if (specialtyFilter.value.trim()) {
      filters.specialty = [specialtyFilter.value.trim()]
    }

    if (dateFrom.value) {
      filters.date_from = dateFrom.value
    }
    if (dateTo.value) {
      filters.date_to = dateTo.value
    }

    const req: MusicSchoolSearchRequest = {
      q: q.value.trim() || undefined,
      filters,
      page: page.value,
      page_size,
      sort: sort.value,
    }

    const res = await searchDocuments(req)
    documents.value = res.items
    total.value = res.total
  } catch (err: any) {
    toast.add({
      title: 'Xatolik',
      description: err?.data?.detail || 'Hujjatlarni qidirib bo‘lmadi',
      color: 'error',
      icon: 'i-lucide-alert-circle',
    })
  } finally {
    listLoading.value = false
  }
}

// Watch filters to trigger search
watch(
  [q, selectedSchoolId, specialtyFilter, graduationYearFilter, dateFrom, dateTo, sort, page],
  () => {
    runSearch()
  }
)

// --- Document Selection & Preview ---
function selectDocument(doc: any) {
  navigateTo(`/music-school-archive/${doc.id}`)
}

// --- CRUD Actions ---
const deleteOpen = ref(false)
const deleteTarget = ref<MusicSchoolDocumentResponse | null>(null)

function confirmDelete(doc: MusicSchoolDocumentResponse) {
  deleteTarget.value = doc
  deleteOpen.value = true
}

async function handleDelete() {
  if (!deleteTarget.value) return
  try {
    await deleteDocument(deleteTarget.value.id)
    toast.add({
      title: 'Muvaffaqiyat',
      description: 'Hujjat tizimdan butunlay o‘chirildi',
      color: 'success',
      icon: 'i-lucide-check-circle',
    })
    deleteOpen.value = false
    if (selectedDoc.value?.id === deleteTarget.value.id) {
      selectedDoc.value = null
    }
    runSearch()
  } catch (err: any) {
    toast.add({
      title: 'Xatolik',
      description: err?.data?.detail || 'Hujjatni o‘chirib bo‘lmadi',
      color: 'error',
      icon: 'i-lucide-alert-circle',
    })
  }
}

// Format date helper
function formatDate(dateStr: string | null) {
  if (!dateStr) return '-'
  return dateStr.split('-').reverse().join('.')
}

// Columns definition for UTable
const columns = [
  { accessorKey: 'student_full_name', header: 'O‘quvchi F.I.Sh.' },
  { accessorKey: 'music_school_name', header: 'Musiqa maktabi' },
  { accessorKey: 'specialty', header: 'Cholg‘u / Yo‘nalish' },
  { accessorKey: 'graduation_year', header: 'Bitirgan yili' },
  { accessorKey: 'diploma', header: 'Diplom' },
  { accessorKey: 'given_date', header: 'Berilgan sana' },
  { accessorKey: 'ocr_status', header: 'Holat' },
]

onMounted(() => {
  fetchSchools()
  runSearch()
})

const sortOptions = [
  { label: 'Sana (yangidan eskigacha)', value: 'date_desc' },
  { label: 'Sana (eskidan yangigacha)', value: 'date_asc' },
]

const totalPages = computed(() => Math.ceil(total.value / page_size))
</script>

<template>
  <PagePanel title="Musiqa maktabi arxivi" icon="i-lucide-music-4">
    <template #headerRight>
      <UBadge :label="`${total} ta hujjat`" variant="subtle" class="mr-2" />
      <UButton
        v-if="activeSchoolId"
        icon="i-lucide-settings-2"
        label="Mutaxassisliklar"
        variant="outline"
        class="mr-2"
        @click="specialtiesModalOpen = true"
      />
      <UButton icon="i-lucide-plus" label="Diplom qo‘shish" to="/music-school-archive/create" />
    </template>

    <!-- Toolbar Filters -->
    <template #toolbar>
      <div class="flex items-center gap-3 flex-wrap flex-1">
        <UInput
          v-model="q"
          icon="i-lucide-search"
          placeholder="O‘quvchi, diplom, kalit so‘z..."
          class="w-64"
          size="md"
        />

        <USelectMenu
          v-if="isAdmin"
          v-model="selectedSchoolId"
          :items="schoolOptions"
          value-key="value"
          placeholder="Barcha maktablar"
          class="w-56"
          :search-input="{ placeholder: 'Maktabni qidirish...' }"
        />

        <UInput
          v-model="specialtyFilter"
          icon="i-lucide-music"
          placeholder="Cholg‘u (masalan: Dutor)"
          class="w-44"
          size="md"
        />

        <UInput
          v-model="graduationYearFilter"
          type="number"
          icon="i-lucide-calendar"
          placeholder="Yil"
          class="w-24"
          size="md"
        />

        <DatePicker v-model="dateFrom" placeholder="Boshlanish sanasi" size="sm" class="w-36" />
        <DatePicker v-model="dateTo" placeholder="Tugash sanasi" size="sm" class="w-36" />

        <USelect v-model="sort" :items="sortOptions" value-key="value" class="w-52" size="md" />
      </div>
    </template>

    <div class="flex h-full overflow-hidden">
      <!-- ─── Main View: robust UTable ─── -->
      <div class="flex-1 flex flex-col overflow-y-auto">
        <UTable
          :data="documents"
          :columns="columns"
          :loading="listLoading"
          class="w-full cursor-pointer [&_th]:border [&_th]:border-default [&_td]:border [&_td]:border-default [&_th]:align-top"
          @select="(row: any) => selectDocument(row.original)"
        >
          <!-- Cell overrides -->
          <template #student_full_name-cell="{ row }">
            <NuxtLink
              :to="`/music-school-archive/${row.original.id}`"
              class="text-primary hover:underline font-semibold text-base"
              @click.stop
            >
              {{ row.original.student_full_name }}
            </NuxtLink>
          </template>

          <template #music_school_name-cell="{ row }">
            <span class="text-sm text-highlighted">{{ row.original.music_school_name || '—' }}</span>
          </template>

          <template #specialty-cell="{ row }">
            <UBadge :label="row.original.specialty" variant="soft" color="primary" />
          </template>

          <template #graduation_year-cell="{ row }">
            <span class="font-mono text-sm font-semibold">{{ row.original.graduation_year }}</span>
          </template>

          <template #diploma-cell="{ row }">
            <span class="font-mono text-sm text-highlighted">
              {{ row.original.diploma_serial }}{{ row.original.diploma_number }}
            </span>
          </template>

          <template #given_date-cell="{ row }">
            <span class="text-sm whitespace-nowrap">{{ formatDate(row.original.given_date) }}</span>
          </template>

          <template #ocr_status-cell="{ row }">
            <UBadge
              :label="OCR_STATUS_LABELS[row.original.ocr_status as keyof typeof OCR_STATUS_LABELS]"
              :icon="OCR_STATUS_ICONS[row.original.ocr_status as keyof typeof OCR_STATUS_ICONS]"
              :color="OCR_STATUS_COLORS[row.original.ocr_status as keyof typeof OCR_STATUS_COLORS]"
              variant="subtle"
              size="sm"
            />
          </template>
        </UTable>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="flex justify-center p-4 border-t border-default bg-elevated/10">
          <UPagination v-model:page="page" :total="total" :items-per-page="page_size" />
        </div>

        <!-- Empty state -->
        <div v-if="!documents.length && !listLoading" class="flex items-center justify-center p-12 flex-1">
          <EmptyState
            icon="i-lucide-search-x"
            title="Diplom hujjatlari topilmadi"
            description="Qidiruv so‘rovingizga mos yoki ushbu bo‘limda birorta ham bitiruvchi diplomi mavjud emas."
          />
        </div>
      </div>
    </div>
  </PagePanel>

  <!-- Specialties Management Modal -->
  <MusicSchoolSpecialtiesModal
    v-model:open="specialtiesModalOpen"
    :school-id="activeSchoolId"
  />
</template>
