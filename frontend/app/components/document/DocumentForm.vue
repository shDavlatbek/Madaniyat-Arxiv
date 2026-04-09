<script setup lang="ts">
import { z } from 'zod'
import type { CategoryFieldResponse, DocumentResponse, PersonResponse } from '~/types'

const props = defineProps<{
  categoryId: string
  initialData?: DocumentResponse | null
  defaultYear?: number
  forceDirty?: boolean
}>()

const emit = defineEmits<{
  submit: [data: Record<string, any>, file?: File, attachments?: File[]]
}>()

const { apiFetch } = useApi()
const { getActivePersons } = usePersons()
const loading = ref(false)

// Fetch category fields
const { data: fields } = await useAsyncData(
  `fields-${props.categoryId}`,
  () => apiFetch<CategoryFieldResponse[]>(`/api/categories/${props.categoryId}/fields`),
)

// Build base schema
const baseSchema = z.object({
  title: z.string().min(1, 'Sarlavha kiritilishi shart'),
  document_number: z.string().min(1, 'Hujjat raqami kiritilishi shart'),
  date: z.string().min(1, 'Sana kiritilishi shart'),
  short_desc: z.string().optional(),
  pages: z.coerce.number().optional(),
  person_id: z.string().optional(),
  archive_number: z.string().optional(),
})

// State
const state = reactive<Record<string, any>>({
  title: props.initialData?.title || '',
  document_number: props.initialData?.document_number || '',
  date: props.initialData?.date || (props.defaultYear ? `${props.defaultYear}-01-01` : ''),
  short_desc: props.initialData?.short_desc || '',
  pages: props.initialData?.pages || undefined,
  person_id: props.initialData?.person_id || undefined,
  archive_number: props.initialData?.archive_number || '',
})

// Snapshot of initial values for dirty tracking (edit mode)
const initialSnapshot = props.initialData
  ? JSON.stringify({
      title: props.initialData.title || '',
      document_number: props.initialData.document_number || '',
      date: props.initialData.date || '',
      short_desc: props.initialData.short_desc || '',
      pages: props.initialData.pages || undefined,
      person_id: props.initialData.person_id || undefined,
      archive_number: props.initialData.archive_number || '',
    })
  : null

const initialDynamicSnapshot = ref<string | null>(null)

// Year constraints for date picker
const docYear = computed(() => {
  if (props.defaultYear) return props.defaultYear
  if (props.initialData?.date) return Number(props.initialData.date.split('-')[0])
  return null
})
const dateMinDate = computed(() => docYear.value ? `${docYear.value}-01-01` : undefined)
const dateMaxDate = computed(() => docYear.value ? `${docYear.value}-12-31` : undefined)

// File upload
const selectedFile = ref<File | null>(null)
const isDragging = ref(false)

// Attachments (Ilovalar)
const attachmentFiles = ref<File[]>([])

function onAttachmentChange(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files) {
    for (const f of Array.from(input.files)) {
      attachmentFiles.value.push(f)
    }
  }
  input.value = ''
}

function removeAttachment(index: number) {
  attachmentFiles.value.splice(index, 1)
}

function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  selectedFile.value = input.files?.[0] || null
}

function onDrop(event: DragEvent) {
  isDragging.value = false
  const file = event.dataTransfer?.files?.[0]
  if (file) selectedFile.value = file
}

function removeFile() {
  selectedFile.value = null
  const input = document.getElementById('doc-file-input') as HTMLInputElement
  if (input) input.value = ''
}

function formatFileSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`
}

function getFileIcon(name: string) {
  const ext = name.split('.').pop()?.toLowerCase()
  if (['pdf'].includes(ext!)) return 'i-lucide-file-text'
  if (['doc', 'docx'].includes(ext!)) return 'i-lucide-file-type'
  if (['xls', 'xlsx'].includes(ext!)) return 'i-lucide-file-spreadsheet'
  if (['jpg', 'jpeg', 'png', 'gif'].includes(ext!)) return 'i-lucide-file-image'
  if (['zip', 'rar'].includes(ext!)) return 'i-lucide-file-archive'
  return 'i-lucide-file'
}

// Dynamic field state
const dynamicFields = reactive<Record<string, any>>({})

if (props.initialData?.field_values && fields.value) {
  for (const fv of props.initialData.field_values) {
    const fieldDef = fields.value.find(f => f.id === fv.category_field_id)
    if (fieldDef) {
      dynamicFields[fieldDef.name] = fv.value
    }
  }
}

// Store initial dynamic fields snapshot after populating
initialDynamicSnapshot.value = props.initialData ? JSON.stringify({ ...dynamicFields }) : null

// Person selector — fetch active persons based on document date
const activePersons = ref<PersonResponse[]>([])
const personItems = computed(() =>
  activePersons.value.map(p => {
    const tenure = p.tenures.find(t => {
      const sd = t.start_date
      const ed = t.end_date
      return sd <= (state.date || '') && (!ed || ed >= (state.date || ''))
    })
    let label = p.full_name
    if (tenure) {
      const sd = tenure.start_date.split('-').reverse().join('.')
      const ed = tenure.end_date ? tenure.end_date.split('-').reverse().join('.') : 'hozirgacha'
      label = `${p.full_name} — ${tenure.position} (${sd} — ${ed})`
    }
    return { label, value: p.id }
  })
)

async function fetchPersons() {
  if (!state.date) {
    activePersons.value = []
    return
  }
  try {
    const data = await getActivePersons(state.date)
    activePersons.value = data.items || []
  } catch {
    activePersons.value = []
  }
}

watch(() => state.date, fetchPersons, { immediate: true })

// Dirty tracking for edit mode
const isEditing = computed(() => !!props.initialData)

const isDirty = computed(() => {
  if (!isEditing.value) return true
  if (props.forceDirty) return true
  if (selectedFile.value) return true
  if (attachmentFiles.value.length) return true
  const currentSnapshot = JSON.stringify({
    title: state.title || '',
    document_number: state.document_number || '',
    date: state.date || '',
    short_desc: state.short_desc || '',
    pages: state.pages || undefined,
    person_id: state.person_id || undefined,
    archive_number: state.archive_number || '',
  })
  if (currentSnapshot !== initialSnapshot) return true
  if (JSON.stringify({ ...dynamicFields }) !== initialDynamicSnapshot.value) return true
  return false
})

async function handleSubmit() {
  loading.value = true
  try {
    emit('submit', {
      ...state,
      dynamic_fields: { ...dynamicFields },
    }, selectedFile.value || undefined, attachmentFiles.value.length ? [...attachmentFiles.value] : undefined)
  }
  finally {
    loading.value = false
  }
}
</script>

<template>
  <UForm
    :schema="baseSchema"
    :state="state"
    @submit="handleSubmit"
  >
    <div class="flex flex-col lg:flex-row gap-6">
      <!-- Left: Form fields -->
      <div class="flex-1 min-w-0 space-y-6">
        <!-- Main info -->
        <UCard :ui="{ header: 'border-b border-default', body: 'space-y-5' }">
          <template #header>
            <div class="flex items-center gap-2">
              <UIcon name="i-lucide-file-text" class="w-4 h-4 text-muted" />
              <h2 class="text-sm font-semibold text-highlighted">Asosiy ma'lumotlar</h2>
              <UBadge v-if="isEditing && isDirty" label="Tahrirlangan" variant="subtle" color="warning" size="xs" class="ml-auto" />
            </div>
          </template>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
            <UFormField label="Sarlavha" name="title" required help="Hujjatning to'liq nomi" class="md:col-span-2">
              <UInput v-model="state.title" icon="i-lucide-file-text" placeholder="Hujjat sarlavhasi" size="lg" class="w-full" />
            </UFormField>

            <UFormField label="Hujjat raqami" name="document_number" required>
              <UInput v-model="state.document_number" icon="i-lucide-hash" placeholder="123 yoki 123-A" size="lg" class="w-full" />
            </UFormField>

            <UFormField label="Imzo qo'ygan shaxs" name="person_id">
              <USelectMenu
                v-model="state.person_id"
                value-key="value"
                :items="personItems"
                :search-input="{ placeholder: 'Qidirish...' }"
                placeholder="Shaxsni tanlang"
                icon="i-lucide-user-check"
                size="lg"
                class="w-full"
              />
            </UFormField>
          </div>

          <div class="grid grid-cols-2 md:grid-cols-4 gap-5">
            <UFormField label="Sana" name="date" required>
              <DatePicker v-model="state.date" size="lg" :min-date="dateMinDate" :max-date="dateMaxDate" />
            </UFormField>

            <UFormField label="Sahifalar soni" name="pages">
              <UInput v-model="state.pages" type="number" icon="i-lucide-book-open" size="lg" class="w-full" />
            </UFormField>

            <UFormField label="Arxiv tartib raqami" name="archive_number" class="md:col-span-2">
              <UInput v-model="state.archive_number" icon="i-lucide-archive" placeholder="Arxiv tartib raqami" size="lg" class="w-full" />
            </UFormField>
          </div>

          <UFormField label="Qisqacha tavsif" name="short_desc" help="Ixtiyoriy — hujjat mazmuni haqida qisqacha">
            <UTextarea v-model="state.short_desc" :rows="6" placeholder="Hujjat haqida qisqacha..." class="w-full" />
          </UFormField>
        </UCard>

        <!-- Dynamic fields -->
        <UCard v-if="fields?.length" :ui="{ header: 'border-b border-default' }">
          <template #header>
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <UIcon name="i-lucide-layers" class="w-4 h-4 text-muted" />
                <h2 class="text-sm font-semibold text-highlighted">Qo'shimcha maydonlar</h2>
              </div>
              <UBadge :label="`${fields.length} ta maydon`" variant="subtle" color="neutral" size="sm" />
            </div>
          </template>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
            <DocumentFieldRenderer
              v-for="field in fields"
              :key="field.id"
              v-model="dynamicFields[field.name]"
              :field="field"
            />
          </div>
        </UCard>
      </div>

      <!-- Right: File upload + actions -->
      <div class="w-full lg:w-80 xl:w-96 shrink-0 space-y-6">
        <!-- File upload card -->
        <UCard :ui="{ header: 'border-b border-default' }">
          <template #header>
            <div class="flex items-center gap-2">
              <UIcon name="i-lucide-paperclip" class="w-4 h-4 text-muted" />
              <h2 class="text-sm font-semibold text-highlighted">Fayl biriktirish</h2>
            </div>
          </template>

          <!-- Existing file indicator -->
          <div
            v-if="initialData?.file_path && !selectedFile"
            class="flex items-center gap-3 p-3 mb-3 rounded-xl bg-primary-50 dark:bg-primary-950/50 border border-primary-200 dark:border-primary-900"
          >
            <div class="w-10 h-10 rounded-lg bg-primary-100 dark:bg-primary-900 flex items-center justify-center shrink-0">
              <UIcon name="i-lucide-file-check-2" class="w-5 h-5 text-primary-600 dark:text-primary-400" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-highlighted">Fayl biriktirilgan</p>
              <p class="text-xs text-muted">Yangi fayl tanlasangiz, eski fayl almashtiriladi</p>
            </div>
          </div>

          <!-- Dropzone -->
          <label
            for="doc-file-input"
            class="relative flex flex-col items-center justify-center w-full min-h-48 border-2 border-dashed rounded-xl cursor-pointer transition-all duration-200"
            :class="[
              selectedFile
                ? 'border-primary-400 bg-primary-50/50 dark:bg-primary-950/30'
                : isDragging
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-950/50 scale-[1.01]'
                  : 'border-default hover:border-primary-400 hover:bg-elevated/40',
            ]"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="onDrop"
          >
            <!-- Selected file state -->
            <div v-if="selectedFile" class="flex flex-col items-center gap-3 px-4 py-3">
              <div class="w-12 h-12 rounded-xl bg-primary-100 dark:bg-primary-900 flex items-center justify-center shrink-0">
                <UIcon :name="getFileIcon(selectedFile.name)" class="w-6 h-6 text-primary-600 dark:text-primary-400" />
              </div>
              <div class="text-center min-w-0">
                <p class="text-sm font-medium text-highlighted truncate max-w-56">{{ selectedFile.name }}</p>
                <p class="text-xs text-muted mt-0.5">{{ formatFileSize(selectedFile.size) }}</p>
              </div>
            </div>

            <!-- Empty state -->
            <div v-else class="flex flex-col items-center gap-2 py-6 px-4">
              <div class="w-12 h-12 rounded-full bg-elevated flex items-center justify-center mb-1">
                <UIcon name="i-lucide-upload-cloud" class="w-6 h-6 text-muted" />
              </div>
              <p class="text-sm font-medium text-highlighted text-center">
                Faylni tashlang yoki
                <span class="text-primary-600 dark:text-primary-400">tanlang</span>
              </p>
              <p class="text-xs text-muted text-center">PDF, DOCX, XLSX, JPG, PNG, ZIP</p>
            </div>

            <input
              id="doc-file-input"
              type="file"
              class="hidden"
              accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.gif,.zip,.rar"
              @change="onFileChange"
            >
          </label>

          <div v-if="selectedFile" class="flex justify-center mt-3">
            <UButton
              variant="ghost"
              size="xs"
              color="error"
              icon="i-lucide-trash-2"
              label="Faylni olib tashlash"
              @click.prevent="removeFile"
            />
          </div>
        </UCard>

        <!-- Attachments (Ilovalar) -->
        <UCard :ui="{ header: 'border-b border-default' }">
          <template #header>
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <UIcon name="i-lucide-paperclip" class="w-4 h-4 text-muted" />
                <h2 class="text-sm font-semibold text-highlighted">Ilovalar (PDF)</h2>
                <UBadge v-if="attachmentFiles.length" :label="String(attachmentFiles.length)" variant="subtle" size="xs" />
              </div>
              <label class="cursor-pointer">
                <UButton as="span" icon="i-lucide-plus" size="xs" variant="ghost" label="Qo'shish" />
                <input type="file" class="hidden" accept=".pdf" multiple @change="onAttachmentChange">
              </label>
            </div>
          </template>

          <!-- Existing attachments (edit mode) -->
          <slot name="existing-attachments" />

          <!-- New attachment files -->
          <div v-if="attachmentFiles.length" class="space-y-2">
            <p v-if="isEditing" class="text-xs text-muted font-medium">Yangi ilovalar:</p>
            <div
              v-for="(file, i) in attachmentFiles"
              :key="i"
              class="flex items-center gap-3 p-2 rounded-lg border border-default"
            >
              <UIcon name="i-lucide-file-text" class="text-primary shrink-0" />
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-highlighted truncate">{{ file.name }}</p>
                <p class="text-xs text-muted">{{ (file.size / 1024).toFixed(1) }} KB</p>
              </div>
              <UButton icon="i-lucide-x" variant="ghost" size="xs" color="error" @click="removeAttachment(i)" />
            </div>
          </div>
          <p v-else-if="!$slots['existing-attachments']" class="text-xs text-muted text-center py-3">Ilovalar qo'shilmagan</p>
        </UCard>

        <!-- Action buttons -->
        <div class="space-y-3 sticky top-4">
          <UButton
            type="submit"
            :label="isEditing ? 'Saqlash' : 'Hujjat yaratish'"
            icon="i-lucide-save"
            :loading="loading"
            :disabled="isEditing && !isDirty"
            block
            size="lg"
          />
          <UButton
            variant="ghost"
            color="neutral"
            label="Bekor qilish"
            icon="i-lucide-x"
            :disabled="loading"
            block
            size="lg"
            @click="$router.back()"
          />
        </div>
      </div>
    </div>
  </UForm>
</template>