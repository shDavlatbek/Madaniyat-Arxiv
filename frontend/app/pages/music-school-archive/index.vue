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
const selectedDoc = ref<MusicSchoolDocumentResponse | null>(null)
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

// --- Form & Modal States ---
const formModalOpen = ref(false)
const specialtiesModalOpen = ref(false)
const editingDoc = ref<MusicSchoolDocumentResponse | null>(null)
const saving = ref(false)
const uploadProgress = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
const selectedUploadFile = ref<File | null>(null)

const formState = reactive({
  student_full_name: '',
  music_school_id: '',
  specialty_id: '',
  graduation_year: new Date().getFullYear(),
  diploma_serial: '',
  diploma_number: '',
  given_date: '',
  description: '',
})

// Specialty reactive state
const schoolSpecialties = ref<any[]>([])
const schoolSpecialtyOptions = computed(() =>
  schoolSpecialties.value.map(s => ({ label: s.name, value: s.id }))
)

async function fetchSchoolSpecialties() {
  if (!formState.music_school_id) {
    schoolSpecialties.value = []
    return
  }
  try {
    schoolSpecialties.value = await listSpecialties(formState.music_school_id)
  } catch (err) {
    console.error('Mutaxassisliklarni yuklashda xatolik:', err)
  }
}

watch(() => formState.music_school_id, () => {
  fetchSchoolSpecialties()
})

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

// Poll for OCR status changes on the currently viewed document
const ocrPolling = ref<ReturnType<typeof setInterval> | null>(null)

async function refreshSelectedDoc() {
  if (!selectedDoc.value) return
  try {
    const fresh = await getDocument(selectedDoc.value.id)
    selectedDoc.value = fresh
    // Update it in the flat list too
    const idx = documents.value.findIndex(d => d.id === fresh.id)
    if (idx !== -1) {
      documents.value[idx] = fresh
    }
  } catch (err) {
    console.error('Hujjatni qayta yuklashda xatolik:', err)
  }
}

watchEffect(() => {
  const inProgress = selectedDoc.value && (selectedDoc.value.ocr_status === 'pending' || selectedDoc.value.ocr_status === 'processing')
  if (inProgress && !ocrPolling.value) {
    ocrPolling.value = setInterval(() => {
      refreshSelectedDoc()
    }, 5000)
  } else if (!inProgress && ocrPolling.value) {
    clearInterval(ocrPolling.value)
    ocrPolling.value = null
  }
})

onBeforeUnmount(() => {
  if (ocrPolling.value) clearInterval(ocrPolling.value)
})

// --- Document Selection & Preview ---
function selectDocument(doc: any) {
  selectedDoc.value = doc
}

const fileUrl = computed(() => {
  if (!selectedDoc.value?.file_path) return null
  return `${config.public.apiBase}/api/music-school-documents/${selectedDoc.value.id}/file`
})

// --- File Downloads ---
async function downloadFile() {
  if (!fileUrl.value || !selectedDoc.value) return
  try {
    const token = useCookie('auth_token')
    const response = await fetch(fileUrl.value, {
      headers: token.value ? { Authorization: `Bearer ${token.value}` } : {},
    })
    if (!response.ok) throw new Error('Download failed')
    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${selectedDoc.value.student_full_name}_diplom.pdf`
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    toast.add({
      title: 'Xatolik',
      description: 'Faylni yuklab bo‘lmadi',
      color: 'error',
      icon: 'i-lucide-alert-circle',
    })
  }
}

// --- CRUD Actions ---
function openCreate() {
  editingDoc.value = null
  formState.student_full_name = ''
  formState.music_school_id = isMusicSchool.value ? musicSchoolId.value || '' : ''
  formState.specialty_id = ''
  formState.graduation_year = new Date().getFullYear()
  formState.diploma_serial = ''
  formState.diploma_number = ''
  formState.given_date = ''
  formState.description = ''
  selectedUploadFile.value = null
  formModalOpen.value = true
}

function openEdit(doc: MusicSchoolDocumentResponse) {
  editingDoc.value = doc
  formState.student_full_name = doc.student_full_name
  formState.music_school_id = doc.music_school_id
  formState.specialty_id = doc.specialty_id
  formState.graduation_year = doc.graduation_year
  formState.diploma_serial = doc.diploma_serial
  formState.diploma_number = doc.diploma_number
  formState.given_date = doc.given_date
  formState.description = doc.description || ''
  selectedUploadFile.value = null
  formModalOpen.value = true
}

function onFileChange(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files?.length) {
    selectedUploadFile.value = target.files[0]
  }
}

async function handleSave() {
  if (!formState.student_full_name.trim() || !formState.music_school_id || !formState.specialty_id) return
  saving.value = true
  try {
    const payload = {
      student_full_name: formState.student_full_name.trim(),
      music_school_id: formState.music_school_id,
      specialty_id: formState.specialty_id,
      graduation_year: Number(formState.graduation_year),
      diploma_serial: formState.diploma_serial.trim().toUpperCase(),
      diploma_number: formState.diploma_number.trim(),
      given_date: formState.given_date,
      description: formState.description.trim() || null,
    }

    let doc: MusicSchoolDocumentResponse
    if (editingDoc.value) {
      doc = await updateDocument(editingDoc.value.id, payload)
      toast.add({
        title: 'Muvaffaqiyat',
        description: 'Hujjat ma’lumotlari tahrirlandi',
        color: 'success',
        icon: 'i-lucide-check-circle',
      })
    } else {
      doc = await createDocument(payload)
      toast.add({
        title: 'Muvaffaqiyat',
        description: 'Hujjat kartochkasi yaratildi',
        color: 'success',
        icon: 'i-lucide-check-circle',
      })
    }

    // Handle File Upload if selected
    if (selectedUploadFile.value) {
      uploadProgress.value = true
      toast.add({
        title: 'Yuklash boshlandi',
        description: 'PDF fayl yuklanmoqda va OCR navbatiga qo‘yilmoqda...',
        color: 'neutral',
        icon: 'i-lucide-loader-2',
      })
      await uploadFile(doc.id, selectedUploadFile.value)
      toast.add({
        title: 'Fayl yuklandi',
        description: 'Fayl muvaffaqiyatli saqlandi va OCR navbatiga qo‘shildi',
        color: 'success',
        icon: 'i-lucide-check-circle',
      })
    }

    formModalOpen.value = false
    runSearch()
    if (selectedDoc.value && selectedDoc.value.id === doc.id) {
      refreshSelectedDoc()
    }
  } catch (err: any) {
    toast.add({
      title: 'Xatolik',
      description: err?.data?.detail || 'Hujjatni saqlashda xatolik',
      color: 'error',
      icon: 'i-lucide-alert-circle',
    })
  } finally {
    saving.value = false
    uploadProgress.value = false
  }
}

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
      <UButton icon="i-lucide-plus" label="Diplom qo‘shish" @click="openCreate" />
    </template>

    <!-- Toolbar Filters (Only shown when no document is open) -->
    <template v-if="!selectedDoc" #toolbar>
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
      <!-- ─── Main View 1: robust UTable (No document selected) ─── -->
      <div v-if="!selectedDoc" class="flex-1 flex flex-col overflow-y-auto">
        <UTable
          :data="documents"
          :columns="columns"
          :loading="listLoading"
          class="w-full cursor-pointer [&_th]:border [&_th]:border-default [&_td]:border [&_td]:border-default [&_th]:align-top"
          @select="(row: any) => selectDocument(row.original)"
        >
          <!-- Cell overrides -->
          <template #student_full_name-cell="{ row }">
            <span class="font-semibold text-highlighted text-base">{{ row.original.student_full_name }}</span>
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

      <!-- ─── Main View 2: Split-screen details + PDF preview ─── -->
      <div v-else class="flex-1 flex h-full overflow-hidden">
        <!-- Left Pane: Metadata Details (40% width) -->
        <div class="w-2/5 shrink-0 border-r border-default flex flex-col overflow-y-auto bg-elevated/10 p-5 space-y-5">
          <!-- Back button -->
          <div class="flex items-center justify-between shrink-0">
            <UButton
              icon="i-lucide-arrow-left"
              label="Ro‘yxatga qaytish"
              variant="ghost"
              @click="selectedDoc = null"
            />
            <div class="flex gap-1.5">
              <UButton
                icon="i-lucide-pencil"
                variant="soft"
                size="sm"
                label="Tahrirlash"
                @click="openEdit(selectedDoc)"
              />
              <UButton
                icon="i-lucide-trash-2"
                variant="soft"
                size="sm"
                color="error"
                label="O‘chirish"
                @click="confirmDelete(selectedDoc)"
              />
            </div>
          </div>

          <!-- Student diploma card -->
          <UCard>
            <template #header>
              <div class="flex items-center gap-2">
                <UIcon name="i-lucide-graduation-cap" class="text-primary text-xl" />
                <span class="font-bold text-highlighted">Bitiruvchi diplomi</span>
                <UBadge
                  :label="OCR_STATUS_LABELS[selectedDoc.ocr_status as keyof typeof OCR_STATUS_LABELS]"
                  :icon="OCR_STATUS_ICONS[selectedDoc.ocr_status as keyof typeof OCR_STATUS_ICONS]"
                  :color="OCR_STATUS_COLORS[selectedDoc.ocr_status as keyof typeof OCR_STATUS_COLORS]"
                  variant="subtle"
                  size="sm"
                  class="ml-auto"
                />
              </div>
            </template>

            <div class="space-y-4">
              <div>
                <p class="text-xs text-muted mb-0.5">O‘quvchi F.I.Sh.</p>
                <p class="text-base font-bold text-highlighted">{{ selectedDoc.student_full_name }}</p>
              </div>

              <div>
                <p class="text-xs text-muted mb-0.5">Musiqa maktabi</p>
                <p class="text-sm font-semibold text-highlighted">{{ selectedDoc.music_school_name }}</p>
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div>
                  <p class="text-xs text-muted mb-0.5">Cholg‘u / Yo‘nalish</p>
                  <p class="text-sm font-semibold text-highlighted">{{ selectedDoc.specialty }}</p>
                </div>
                <div>
                  <p class="text-xs text-muted mb-0.5">Bitirgan yili</p>
                  <p class="text-sm font-mono font-semibold text-highlighted">{{ selectedDoc.graduation_year }}</p>
                </div>
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div>
                  <p class="text-xs text-muted mb-0.5">Diplom seriyasi & raqami</p>
                  <p class="text-sm font-mono font-bold text-primary">
                    {{ selectedDoc.diploma_serial }} {{ selectedDoc.diploma_number }}
                  </p>
                </div>
                <div>
                  <p class="text-xs text-muted mb-0.5">Berilgan sana</p>
                  <p class="text-sm font-semibold text-highlighted">{{ formatDate(selectedDoc.given_date) }}</p>
                </div>
              </div>

              <div v-if="selectedDoc.description" class="pt-2 border-t border-default">
                <p class="text-xs text-muted mb-0.5">Eslatma / Izoh</p>
                <p class="text-sm text-highlighted whitespace-pre-wrap">{{ selectedDoc.description }}</p>
              </div>
            </div>
          </UCard>

          <!-- OCR Extracted Text Card (if ocr is ready) -->
          <UCard v-if="selectedDoc.ocr_status === 'done' && selectedDoc.extracted_text">
            <template #header>
              <div class="flex items-center gap-2">
                <UIcon name="i-lucide-scan-text" class="text-primary" />
                <span class="font-semibold text-highlighted">Raqamlashtirilgan matn (OCR)</span>
              </div>
            </template>
            <div class="max-h-60 overflow-y-auto bg-default/40 p-3 rounded-lg border border-default text-xs font-mono whitespace-pre-wrap select-all">
              {{ selectedDoc.extracted_text }}
            </div>
          </UCard>

          <!-- No File Uploaded panel -->
          <div v-if="!fileUrl" class="p-4 rounded-xl border border-dashed border-default bg-elevated/40 flex flex-col items-center justify-center text-center gap-3">
            <UIcon name="i-lucide-file-warning" class="text-3xl text-muted animate-pulse" />
            <div>
              <p class="text-sm font-semibold text-highlighted">Fayl biriktirilmagan</p>
              <p class="text-xs text-muted mt-1">Diplom PDF skanini biriktiring</p>
            </div>
            <UButton
              icon="i-lucide-upload"
              size="sm"
              label="Fayl yuklash"
              @click="$refs.fileInputDetails?.click()"
            />
            <input
              ref="fileInputDetails"
              type="file"
              accept=".pdf"
              class="hidden"
              @change="async (e: Event) => {
                const target = e.target as HTMLInputElement
                if (target.files?.length) {
                  uploadProgress = true
                  try {
                    await uploadFile(selectedDoc!.id, target.files[0])
                    toast.add({
                      title: 'Muvaffaqiyat',
                      description: 'Fayl muvaffaqiyatli yuklandi',
                      color: 'success',
                      icon: 'i-lucide-check-circle',
                    })
                    refreshSelectedDoc()
                  } catch (err: any) {
                    toast.add({
                      title: 'Xatolik',
                      description: err?.data?.detail || 'Yuklashda xatolik',
                      color: 'error',
                      icon: 'i-lucide-alert-circle',
                    })
                  } finally {
                    uploadProgress = false
                  }
                }
              }"
            />
          </div>

          <!-- File actions if PDF exists -->
          <div v-if="fileUrl" class="flex gap-2 justify-end pt-2">
            <UButton
              icon="i-lucide-download"
              label="PDF yuklab olish"
              variant="soft"
              @click="downloadFile"
            />
            <UButton
              icon="i-lucide-refresh-cw"
              label="Faylni almashtirish"
              variant="ghost"
              @click="$refs.fileInputDetailsReplace?.click()"
            />
            <input
              ref="fileInputDetailsReplace"
              type="file"
              accept=".pdf"
              class="hidden"
              @change="async (e: Event) => {
                const target = e.target as HTMLInputElement
                if (target.files?.length) {
                  uploadProgress = true
                  try {
                    await uploadFile(selectedDoc!.id, target.files[0])
                    toast.add({
                      title: 'Muvaffaqiyat',
                      description: 'Fayl almashtirildi',
                      color: 'success',
                      icon: 'i-lucide-check-circle',
                    })
                    refreshSelectedDoc()
                  } catch (err: any) {
                    toast.add({
                      title: 'Xatolik',
                      description: err?.data?.detail || 'Almashtirishda xatolik',
                      color: 'error',
                      icon: 'i-lucide-alert-circle',
                    })
                  } finally {
                    uploadProgress = false
                  }
                }
              }"
            />
          </div>
        </div>

        <!-- Right Pane: Interactive PDF Renderer (60% width) -->
        <div class="flex-1 flex flex-col h-full bg-white relative border-l border-default">
          <div v-if="uploadProgress" class="absolute inset-0 bg-white/70 dark:bg-black/70 flex items-center justify-center z-50">
            <div class="flex items-center gap-2 font-medium">
              <UIcon name="i-lucide-loader-2" class="animate-spin text-primary" />
              Fayl yuklanmoqda...
            </div>
          </div>

          <div v-if="fileUrl" class="flex-1 flex flex-col h-full">
            <ClientOnly>
              <DocumentPdfViewer
                :key="fileUrl"
                :pdf-url="fileUrl"
                class="flex-1 h-full"
              />
              <template #fallback>
                <div class="flex items-center justify-center h-full">
                  <div class="animate-pulse flex items-center gap-2 text-muted">
                    <UIcon name="i-lucide-loader-2" class="animate-spin" />
                    PDF preview yuklanmoqda...
                  </div>
                </div>
              </template>
            </ClientOnly>
          </div>

          <div v-else class="flex-1 flex flex-col items-center justify-center p-12 text-center text-muted gap-4">
            <UIcon name="i-lucide-file-text" class="text-6xl text-default" />
            <div>
              <p class="font-bold text-highlighted">PDF Skaner mavjud emas</p>
              <p class="text-sm">Ushbu diplom hujjati uchun hali elektron PDF variant biriktirilmagan</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </PagePanel>

  <!-- Create / Edit modal -->
  <UModal v-model:open="formModalOpen" :title="editingDoc ? 'Diplom kartochkasini tahrirlash' : 'Yangi diplom hujjati qo‘shish'">
    <template #body>
      <div class="space-y-4">
        <UFormField label="O‘quvchining to‘liq F.I.Sh." required>
          <UInput
            v-model="formState.student_full_name"
            placeholder="Masalan: Karimov Saidislom Alisher o‘g‘li"
            icon="i-lucide-user"
            size="lg"
            class="w-full"
          />
        </UFormField>

        <UFormField v-if="isAdmin" label="Musiqa maktabi" required>
          <USelectMenu
            v-model="formState.music_school_id"
            :items="schoolOptions"
            value-key="value"
            placeholder="Musiqa maktabini tanlang"
            class="w-full"
            :search-input="{ placeholder: 'Maktabni qidirish...' }"
          />
        </UFormField>

        <div class="grid grid-cols-2 gap-4">
          <UFormField label="Cholg‘u / Mutaxassislik" required>
            <USelectMenu
              v-model="formState.specialty_id"
              :items="schoolSpecialtyOptions"
              value-key="value"
              placeholder="Mutaxassislikni tanlang"
              class="w-full"
              size="lg"
              :search-input="{ placeholder: 'Mutaxassislikni qidirish...' }"
            />
          </UFormField>

          <UFormField label="Bitirgan yili" required>
            <UInput
              v-model="formState.graduation_year"
              type="number"
              icon="i-lucide-calendar"
              size="lg"
            />
          </UFormField>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <UFormField label="Diplom seriyasi (katta harfda)" required>
            <UInput
              v-model="formState.diploma_serial"
              placeholder="Masalan: D"
              icon="i-lucide-hash"
              size="lg"
              maxlength="5"
            />
          </UFormField>

          <UFormField label="Diplom raqami" required>
            <UInput
              v-model="formState.diploma_number"
              placeholder="Masalan: 012345"
              icon="i-lucide-hash"
              size="lg"
            />
          </UFormField>
        </div>

        <UFormField label="Berilgan sana" required>
          <DatePicker v-model="formState.given_date" size="lg" />
        </UFormField>

        <UFormField label="Eslatma / Izoh">
          <UTextarea
            v-model="formState.description"
            placeholder="Diplom bo‘yicha qo‘shimcha izohlar"
            :rows="3"
            class="w-full"
          />
        </UFormField>

        <!-- File Upload Selector in create form -->
        <UFormField :label="editingDoc ? 'Yangi fayl bilan almashtirish (skaner PDF)' : 'Diplom skaner fayli (PDF formatda)'">
          <div class="flex items-center gap-3">
            <UButton
              icon="i-lucide-file-up"
              label="PDF faylni tanlash"
              variant="outline"
              @click="fileInput?.click()"
            />
            <span class="text-xs text-muted truncate max-w-xs">
              {{ selectedUploadFile ? selectedUploadFile.name : 'Fayl tanlanmagan' }}
            </span>
          </div>
          <input
            ref="fileInput"
            type="file"
            accept=".pdf"
            class="hidden"
            @change="onFileChange"
          />
        </UFormField>
      </div>
    </template>
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton variant="ghost" label="Bekor qilish" @click="formModalOpen = false" />
        <UButton
          :label="editingDoc ? 'Saqlash' : 'Qo‘shish'"
          icon="i-lucide-save"
          :loading="saving"
          :disabled="!formState.student_full_name.trim() || !formState.music_school_id || !formState.specialty_id || !formState.diploma_serial.trim() || !formState.diploma_number.trim() || !formState.given_date"
          @click="handleSave"
        />
      </div>
    </template>
  </UModal>

  <!-- Delete confirm modal -->
  <UModal
    v-model:open="deleteOpen"
    title="Diplom hujjatini o‘chirish"
    :description="deleteTarget ? `«${deleteTarget.student_full_name}» o‘quvchisiga tegishli diplom hujjatini butunlay o‘chirib tashlashni tasdiqlaysizmi? Ushbu amalni qaytarib bo‘lmaydi.` : ''"
  >
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton variant="ghost" label="Bekor qilish" @click="deleteOpen = false" />
        <UButton color="error" label="O‘chirish" icon="i-lucide-trash-2" @click="handleDelete" />
      </div>
    </template>
  </UModal>

  <!-- Specialties Management Modal -->
  <MusicSchoolSpecialtiesModal
    v-model:open="specialtiesModalOpen"
    :school-id="activeSchoolId"
    @change="fetchSchoolSpecialties"
  />
</template>
