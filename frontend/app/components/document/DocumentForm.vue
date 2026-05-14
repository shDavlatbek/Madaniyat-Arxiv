<script setup lang="ts">
import { z } from 'zod'
import type { CategoryFieldResponse, DocumentResponse, PersonResponse, YearResponse } from '~/types'

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
const { list: listArchiveFolders } = useArchiveFolders()
const loading = ref(false)

// Fetch category fields
const { data: fields } = await useAsyncData(
  `fields-${props.categoryId}`,
  () => apiFetch<CategoryFieldResponse[]>(`/api/categories/${props.categoryId}/fields`),
)

// Archive folders (Yig'ma jild) + years — to scope folders to the document's year
const { data: archiveFoldersData } = await useAsyncData(
  'doc-form-archive-folders',
  () => listArchiveFolders(),
)
const { data: yearsForFolders } = await useAsyncData(
  'doc-form-years',
  () => apiFetch<{ items: YearResponse[] }>('/api/years?active_only=false'),
)

// Document types (Hujjat turi) — reference taxonomy
const { list: listDocumentTypes } = useDocumentTypes()
const { data: documentTypesData } = await useAsyncData(
  'doc-form-document-types',
  () => listDocumentTypes(),
)

// State
const state = reactive<Record<string, any>>({
  title: props.initialData?.title || '',
  document_number: props.initialData?.document_number || '',
  date: props.initialData?.date || (props.defaultYear ? `${props.defaultYear}-01-01` : ''),
  short_desc: props.initialData?.short_desc || '',
  pages: props.initialData?.pages || undefined,
  person_id: props.initialData?.person_id || undefined,
  archive_number: props.initialData?.archive_number || '',
  archive_folder_id: props.initialData?.archive_folder_id || undefined,
  // Phase 3 — document view + universal fields
  document_view: props.initialData?.document_view || 'unknown',
  document_type_id: props.initialData?.document_type_id || undefined,
  document_form: props.initialData?.document_form || '',
  sender: props.initialData?.sender || '',
  language: props.initialData?.language || '',
  related_document_number: props.initialData?.related_document_number || '',
  related_document_date: props.initialData?.related_document_date || '',
  // Phase 3 — view-specific fields
  received_date: props.initialData?.received_date || '',
  origin_organization: props.initialData?.origin_organization || '',
  sent_date: props.initialData?.sent_date || '',
  recipient_organization: props.initialData?.recipient_organization || '',
  applicant_full_name: props.initialData?.applicant_full_name || '',
  applicant_phone: props.initialData?.applicant_phone || '',
  // Murojaat (appeal) — reference FKs + extra fields
  region_id: props.initialData?.region_id || undefined,
  country_id: props.initialData?.country_id || undefined,
  reception_place_id: props.initialData?.reception_place_id || undefined,
  appeal_type_id: props.initialData?.appeal_type_id || undefined,
  person_type: props.initialData?.person_type || '',
  outgoing_number: props.initialData?.outgoing_number || '',
  outgoing_date: props.initialData?.outgoing_date || '',
  signed_by: props.initialData?.signed_by || '',
  note: props.initialData?.note || '',
})

// Phase 3 optional fields — empty strings become null before posting
const PHASE3_OPTIONAL_KEYS = [
  'document_form', 'sender', 'language', 'related_document_number',
  'related_document_date', 'received_date', 'origin_organization',
  'sent_date', 'recipient_organization', 'applicant_full_name', 'applicant_phone',
  'person_type', 'outgoing_number', 'outgoing_date', 'signed_by', 'note',
] as const

// Hujjat ko'rinishi select options (excludes 'unknown' — that's the unset state)
const documentViewItems = [
  { label: DOCUMENT_VIEW_LABELS.incoming, value: 'incoming' },
  { label: DOCUMENT_VIEW_LABELS.outgoing, value: 'outgoing' },
  { label: DOCUMENT_VIEW_LABELS.internal, value: 'internal' },
  { label: DOCUMENT_VIEW_LABELS.appeal, value: 'appeal' },
]

const languageItems = ["O'zbek", 'Rus', 'Ingliz']

// Required view-specific extras — mirrors REQUIRED_EXTRAS_BY_VIEW in the backend schema.
// Murojaat (appeal): the reference form marks no field as strictly required.
const requiredExtrasByView: Record<string, string[]> = {
  incoming: ['received_date', 'origin_organization'],
  outgoing: ['sent_date', 'recipient_organization'],
  appeal: [],
  internal: [],
  unknown: [],
}

// Schema is reactive: required view-specific extras toggle with document_view
const schema = computed(() => {
  const shape: Record<string, z.ZodTypeAny> = {
    title: z.string().min(1, 'Sarlavha kiritilishi shart'),
    document_number: z.string().min(1, 'Hujjat raqami kiritilishi shart'),
    date: z.string().min(1, 'Sana kiritilishi shart'),
    short_desc: z.string().optional(),
    pages: z.coerce.number().optional(),
    person_id: z.string().optional(),
    archive_number: z.string().optional(),
  }
  for (const key of requiredExtrasByView[state.document_view] || []) {
    shape[key] = z.string().min(1, 'Bu maydon majburiy')
  }
  return z.object(shape)
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
      archive_folder_id: props.initialData.archive_folder_id || undefined,
      document_view: props.initialData.document_view || 'unknown',
      document_type_id: props.initialData.document_type_id || undefined,
      document_form: props.initialData.document_form || '',
      sender: props.initialData.sender || '',
      language: props.initialData.language || '',
      related_document_number: props.initialData.related_document_number || '',
      related_document_date: props.initialData.related_document_date || '',
      received_date: props.initialData.received_date || '',
      origin_organization: props.initialData.origin_organization || '',
      sent_date: props.initialData.sent_date || '',
      recipient_organization: props.initialData.recipient_organization || '',
      applicant_full_name: props.initialData.applicant_full_name || '',
      applicant_phone: props.initialData.applicant_phone || '',
      region_id: props.initialData.region_id || undefined,
      country_id: props.initialData.country_id || undefined,
      reception_place_id: props.initialData.reception_place_id || undefined,
      appeal_type_id: props.initialData.appeal_type_id || undefined,
      person_type: props.initialData.person_type || '',
      outgoing_number: props.initialData.outgoing_number || '',
      outgoing_date: props.initialData.outgoing_date || '',
      signed_by: props.initialData.signed_by || '',
      note: props.initialData.note || '',
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

// Yig'ma jild options — scoped to the document's year when resolvable
const archiveFolderItems = computed(() => {
  const yearId = yearsForFolders.value?.items.find(y => y.value === docYear.value)?.id
  return (archiveFoldersData.value?.items || [])
    .filter(f => yearId == null ? true : f.year_id === yearId)
    .map(f => ({ label: `${f.index_code} — ${f.title}`, value: f.id }))
})

// Hujjat turi options
const documentTypeItems = computed(() =>
  (documentTypesData.value?.items || []).map(t => ({ label: t.name, value: t.id })),
)

// Murojaat (appeal) reference data — regions, reception places, appeal types
const { listRegions, listReceptionPlaces, listAppealTypes } = useReferences()
const { data: localRegionsData } = await useAsyncData(
  'doc-form-regions-local',
  () => listRegions('LOCAL'),
)
const { data: abroadRegionsData } = await useAsyncData(
  'doc-form-regions-abroad',
  () => listRegions('ABROAD'),
)
const { data: receptionPlacesData } = await useAsyncData(
  'doc-form-reception-places',
  () => listReceptionPlaces(),
)
const { data: appealTypesData } = await useAsyncData(
  'doc-form-appeal-types',
  () => listAppealTypes(),
)

// "Hududni tanlang" combines local regions with a synthetic "Xorijiy davlat"
// option; picking it enables the "Davlatni tanlang" (country) select.
const regionChoice = ref<string | undefined>(
  props.initialData?.country_id ? ABROAD_REGION_VALUE : (props.initialData?.region_id || undefined),
)
const isAbroad = computed(() => regionChoice.value === ABROAD_REGION_VALUE)

watch(regionChoice, (choice) => {
  if (choice === ABROAD_REGION_VALUE) {
    state.region_id = undefined
  } else {
    state.region_id = choice || undefined
    state.country_id = undefined
  }
})

const regionItems = computed(() => [
  ...(localRegionsData.value?.items || []).map(r => ({ label: r.name, value: r.id })),
  { label: ABROAD_REGION_LABEL, value: ABROAD_REGION_VALUE },
])
const countryItems = computed(() =>
  (abroadRegionsData.value?.items || []).map(r => ({ label: r.name, value: r.id })),
)
const receptionPlaceItems = computed(() =>
  (receptionPlacesData.value?.items || []).map(p => ({ label: p.name, value: p.id })),
)
const appealTypeItems = computed(() =>
  (appealTypesData.value?.items || []).map(t => ({ label: t.name, value: t.id })),
)

// "Kim tomonidan imzolangan (F.I.O)" becomes "Kim tomonidan yuborilgan" for a
// legal entity (Yuridik shaxs) — a legal entity sends, a person signs.
const signedByLabel = computed(() =>
  state.person_type === 'Yuridik shaxs' ? LABELS.signed_by_legal : LABELS.signed_by,
)

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
    archive_folder_id: state.archive_folder_id || undefined,
    document_view: state.document_view || 'unknown',
    document_type_id: state.document_type_id || undefined,
    document_form: state.document_form || '',
    sender: state.sender || '',
    language: state.language || '',
    related_document_number: state.related_document_number || '',
    related_document_date: state.related_document_date || '',
    received_date: state.received_date || '',
    origin_organization: state.origin_organization || '',
    sent_date: state.sent_date || '',
    recipient_organization: state.recipient_organization || '',
    applicant_full_name: state.applicant_full_name || '',
    applicant_phone: state.applicant_phone || '',
    region_id: state.region_id || undefined,
    country_id: state.country_id || undefined,
    reception_place_id: state.reception_place_id || undefined,
    appeal_type_id: state.appeal_type_id || undefined,
    person_type: state.person_type || '',
    outgoing_number: state.outgoing_number || '',
    outgoing_date: state.outgoing_date || '',
    signed_by: state.signed_by || '',
    note: state.note || '',
  })
  if (currentSnapshot !== initialSnapshot) return true
  if (JSON.stringify({ ...dynamicFields }) !== initialDynamicSnapshot.value) return true
  return false
})

async function handleSubmit() {
  loading.value = true
  try {
    const payload: Record<string, any> = { ...state, dynamic_fields: { ...dynamicFields } }
    // Empty strings → null so the backend's optional/date fields validate cleanly
    for (const key of PHASE3_OPTIONAL_KEYS) {
      if (payload[key] === '') payload[key] = null
    }
    emit(
      'submit',
      payload,
      selectedFile.value || undefined,
      attachmentFiles.value.length ? [...attachmentFiles.value] : undefined,
    )
  }
  finally {
    loading.value = false
  }
}
</script>

<template>
  <UForm
    :schema="schema"
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

            <UFormField :label="LABELS.archive_folder" name="archive_folder_id" class="md:col-span-2" help="Hujjat tegishli yig'ma jild">
              <USelectMenu
                v-model="state.archive_folder_id"
                value-key="value"
                :items="archiveFolderItems"
                :search-input="{ placeholder: 'Qidirish...' }"
                placeholder="Yig'ma jildni tanlang"
                icon="i-lucide-folder-archive"
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

        <!-- Document view + universal/conditional fields -->
        <UCard :ui="{ header: 'border-b border-default', body: 'space-y-5' }">
          <template #header>
            <div class="flex items-center gap-2">
              <UIcon name="i-lucide-list-tree" class="w-4 h-4 text-muted" />
              <h2 class="text-sm font-semibold text-highlighted">{{ LABELS.document_view }}</h2>
            </div>
          </template>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
            <UFormField :label="LABELS.document_view" name="document_view" help="Qo'shimcha maydonlar shunga qarab ochiladi">
              <USelectMenu
                v-model="state.document_view"
                value-key="value"
                :items="documentViewItems"
                :placeholder="`${LABELS.document_view}ni tanlang`"
                icon="i-lucide-list-tree"
                size="lg"
                class="w-full"
              />
            </UFormField>

            <UFormField :label="LABELS.document_type" name="document_type_id" help="Hujjat tasnifi (turlar ro'yxatidan)">
              <USelectMenu
                v-model="state.document_type_id"
                value-key="value"
                :items="documentTypeItems"
                :search-input="{ placeholder: 'Qidirish...' }"
                :placeholder="`${LABELS.document_type}ni tanlang`"
                icon="i-lucide-tags"
                size="lg"
                class="w-full"
              />
            </UFormField>
          </div>

          <!-- Universal fields — apply to every view -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
            <UFormField :label="LABELS.sender" name="sender">
              <UInput v-model="state.sender" icon="i-lucide-send" :placeholder="LABELS.sender" size="lg" class="w-full" />
            </UFormField>

            <UFormField :label="LABELS.document_form" name="document_form">
              <USelectMenu
                v-model="state.document_form"
                :items="[...DOCUMENT_FORM_OPTIONS]"
                :placeholder="`${LABELS.document_form}ni tanlang`"
                icon="i-lucide-file-stack"
                size="lg"
                class="w-full"
              />
            </UFormField>

            <UFormField :label="LABELS.language" name="language">
              <USelectMenu
                v-model="state.language"
                :items="languageItems"
                :placeholder="`${LABELS.language}ni tanlang`"
                icon="i-lucide-languages"
                size="lg"
                class="w-full"
              />
            </UFormField>

            <div class="hidden md:block" />

            <UFormField :label="LABELS.related_document_number" name="related_document_number">
              <UInput v-model="state.related_document_number" icon="i-lucide-link" placeholder="123-A" size="lg" class="w-full" />
            </UFormField>

            <UFormField :label="LABELS.related_document_date" name="related_document_date">
              <DatePicker v-model="state.related_document_date" size="lg" />
            </UFormField>
          </div>

          <!-- Conditional: incoming (Kiruvchi hujjat) -->
          <div v-if="state.document_view === 'incoming'" class="grid grid-cols-1 md:grid-cols-2 gap-5 pt-4 border-t border-default">
            <UFormField :label="LABELS.received_date" name="received_date" required>
              <DatePicker v-model="state.received_date" size="lg" />
            </UFormField>
            <UFormField :label="LABELS.origin_organization" name="origin_organization" required>
              <UInput v-model="state.origin_organization" icon="i-lucide-building" :placeholder="LABELS.origin_organization" size="lg" class="w-full" />
            </UFormField>
          </div>

          <!-- Conditional: outgoing (Chiquvchi hujjat) -->
          <div v-else-if="state.document_view === 'outgoing'" class="grid grid-cols-1 md:grid-cols-2 gap-5 pt-4 border-t border-default">
            <UFormField :label="LABELS.sent_date" name="sent_date" required>
              <DatePicker v-model="state.sent_date" size="lg" />
            </UFormField>
            <UFormField :label="LABELS.recipient_organization" name="recipient_organization" required>
              <UInput v-model="state.recipient_organization" icon="i-lucide-building" :placeholder="LABELS.recipient_organization" size="lg" class="w-full" />
            </UFormField>
          </div>

          <!-- Conditional: appeal (Murojaat) — reference form field set -->
          <div v-else-if="state.document_view === 'appeal'" class="space-y-5 pt-4 border-t border-default">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
              <UFormField :label="LABELS.region" name="region_id">
                <USelectMenu
                  v-model="regionChoice"
                  value-key="value"
                  :items="regionItems"
                  :search-input="{ placeholder: 'Qidirish...' }"
                  :placeholder="LABELS.region"
                  icon="i-lucide-map-pin"
                  size="lg"
                  class="w-full"
                />
              </UFormField>

              <UFormField :label="LABELS.country" name="country_id" :help="isAbroad ? undefined : `${LABELS.region}da “${ABROAD_REGION_LABEL}” tanlang`">
                <USelectMenu
                  v-model="state.country_id"
                  value-key="value"
                  :items="countryItems"
                  :search-input="{ placeholder: 'Qidirish...' }"
                  :placeholder="LABELS.country"
                  :disabled="!isAbroad"
                  icon="i-lucide-globe"
                  size="lg"
                  class="w-full"
                />
              </UFormField>

              <UFormField :label="LABELS.reception_place" name="reception_place_id" class="md:col-span-2">
                <USelectMenu
                  v-model="state.reception_place_id"
                  value-key="value"
                  :items="receptionPlaceItems"
                  :search-input="{ placeholder: 'Qidirish...' }"
                  :placeholder="LABELS.reception_place"
                  icon="i-lucide-inbox"
                  size="lg"
                  class="w-full"
                />
              </UFormField>

              <UFormField :label="LABELS.appeal_type" name="appeal_type_id">
                <USelectMenu
                  v-model="state.appeal_type_id"
                  value-key="value"
                  :items="appealTypeItems"
                  :placeholder="`${LABELS.appeal_type}ni tanlang`"
                  icon="i-lucide-megaphone"
                  size="lg"
                  class="w-full"
                />
              </UFormField>

              <UFormField :label="LABELS.person_type" name="person_type">
                <USelectMenu
                  v-model="state.person_type"
                  :items="[...PERSON_TYPE_OPTIONS]"
                  :placeholder="LABELS.person_type"
                  icon="i-lucide-user"
                  size="lg"
                  class="w-full"
                />
              </UFormField>

              <UFormField :label="LABELS.outgoing_number" name="outgoing_number">
                <UInput v-model="state.outgoing_number" icon="i-lucide-hash" :placeholder="LABELS.outgoing_number" size="lg" class="w-full" />
              </UFormField>

              <UFormField :label="LABELS.outgoing_date" name="outgoing_date">
                <DatePicker v-model="state.outgoing_date" size="lg" />
              </UFormField>

              <UFormField :label="signedByLabel" name="signed_by" class="md:col-span-2">
                <UInput v-model="state.signed_by" icon="i-lucide-pencil" :placeholder="signedByLabel" size="lg" class="w-full" />
              </UFormField>
            </div>

            <UFormField :label="LABELS.note" name="note">
              <UTextarea v-model="state.note" :rows="3" :placeholder="LABELS.note" class="w-full" />
            </UFormField>
          </div>

          <!-- Conditional: internal (Ichki hujjat) — no extra fields -->
          <p v-else-if="state.document_view === 'internal'" class="text-xs text-muted pt-4 border-t border-default">
            Ichki hujjat uchun qo'shimcha maydon talab qilinmaydi.
          </p>
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