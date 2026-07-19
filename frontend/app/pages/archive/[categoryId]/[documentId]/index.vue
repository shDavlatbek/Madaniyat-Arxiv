<script setup lang="ts">
import type { CategoryFieldResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const route = useRoute()
const categoryId = computed(() => route.params.categoryId as string)
const documentId = computed(() => route.params.documentId as string)

const { getDocument, deleteDocument } = useDocuments()
const { apiFetch } = useApi()
const { listRegions, listReceptionPlaces, listAppealTypes } = useReferences()
const { list: listArchiveFolders } = useArchiveFolders()
const toast = useToast()
const config = useRuntimeConfig()
const deleteOpen = ref(false)

const { data: doc, refresh: refreshDoc } = await useAsyncData(`doc-${documentId.value}`, () => getDocument(documentId.value))

// While OCR is mid-flight on the main file or any attachment, poll every
// 5 s so the badge transitions pending → processing → done without a manual
// refresh. The interval clears as soon as nothing is processing anymore.
const ocrPolling = ref<ReturnType<typeof setInterval> | null>(null)
function isOcrInProgress() {
  if (!doc.value) return false
  if (doc.value.ocr_status === 'pending' || doc.value.ocr_status === 'processing') return true
  return (doc.value.attachments || []).some(a => a.ocr_status === 'pending' || a.ocr_status === 'processing')
}
watchEffect(() => {
  if (!import.meta.client) return
  const inProgress = isOcrInProgress()
  if (inProgress && !ocrPolling.value) {
    ocrPolling.value = setInterval(() => { refreshDoc() }, 5000)
  } else if (!inProgress && ocrPolling.value) {
    clearInterval(ocrPolling.value)
    ocrPolling.value = null
  }
})
onBeforeUnmount(() => {
  if (ocrPolling.value) clearInterval(ocrPolling.value)
})
const { data: fields } = await useAsyncData(`fields-${categoryId.value}`, () =>
  apiFetch<CategoryFieldResponse[]>(`/api/categories/${categoryId.value}/fields`)
)

// Reference data — resolve FK ids to display names (region/country/reception place/appeal type/archive folder).
const { data: regionsData } = await useAsyncData('doc-view-regions', () => listRegions())
const { data: receptionPlacesData } = await useAsyncData('doc-view-reception-places', () => listReceptionPlaces())
const { data: appealTypesData } = await useAsyncData('doc-view-appeal-types', () => listAppealTypes())
const { data: archiveFoldersData } = await useAsyncData('doc-view-archive-folders', () => listArchiveFolders())

function getFieldValue(fieldId: string) {
  return doc.value?.field_values.find(fv => fv.category_field_id === fieldId)?.value || '-'
}

function lookupRegionName(id: string | null | undefined) {
  if (!id) return null
  return regionsData.value?.items.find(r => r.id === id)?.name || null
}
function lookupReceptionPlace(id: string | null | undefined) {
  if (!id) return null
  return receptionPlacesData.value?.items.find(p => p.id === id)?.name || null
}
function lookupAppealType(id: string | null | undefined) {
  if (!id) return null
  return appealTypesData.value?.items.find(t => t.id === id)?.name || null
}
function lookupArchiveFolder(id: string | null | undefined) {
  if (!id) return null
  const f = archiveFoldersData.value?.items.find(af => af.id === id)
  return f ? `${f.index_code} — ${f.title}` : null
}

function formatDate(value: string | null | undefined) {
  if (!value) return '-'
  return value.split('-').reverse().join('.')
}

// Pull the right "signed by" label depending on person type — a legal entity sends,
// a natural person signs. Mirrors the form logic in DocumentForm.vue.
const signedByLabel = computed(() =>
  doc.value?.person_type === 'Yuridik shaxs' ? LABELS.signed_by_legal : LABELS.signed_by,
)

// Badge color per view — incoming green, outgoing blue, appeal amber, internal neutral.
const documentViewColor = computed(() => {
  switch (doc.value?.document_view) {
    case 'incoming': return 'success' as const
    case 'outgoing': return 'info' as const
    case 'appeal': return 'warning' as const
    default: return 'neutral' as const
  }
})

const fileUrl = computed(() => {
  if (!doc.value?.file_path) return null
  return `${config.public.apiBase}/api/documents/${doc.value.id}/file`
})

const isPdf = computed(() => {
  if (!doc.value?.file_path) return false
  return doc.value.file_path.toLowerCase().endsWith('.pdf')
})

// Active PDF viewer URL (main file or selected attachment)
const activePdfUrl = ref<string | null>(null)
const activeFileName = ref<string>('')

function viewMainFile() {
  activePdfUrl.value = fileUrl.value
  activeFileName.value = 'Asosiy hujjat'
}

function viewAttachment(attachmentId: string, filename: string) {
  activePdfUrl.value = `${config.public.apiBase}/api/documents/${documentId.value}/attachments/${attachmentId}`
  activeFileName.value = filename
}

// Default to main file, or first attachment if no main file
watchEffect(() => {
  if (activePdfUrl.value) return
  if (isPdf.value && fileUrl.value) {
    activePdfUrl.value = fileUrl.value
    activeFileName.value = 'Asosiy hujjat'
  } else if (doc.value?.attachments?.length) {
    const first = doc.value.attachments[0]!
    activePdfUrl.value = `${config.public.apiBase}/api/documents/${documentId.value}/attachments/${first.id}`
    activeFileName.value = first.original_filename
  }
})

async function downloadFile() {
  if (!fileUrl.value) return
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
    a.download = doc.value?.file_path?.split('/').pop() || 'document'
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    toast.add({ title: 'Xatolik', description: 'Faylni yuklab bo\'lmadi', color: 'error', icon: 'i-lucide-alert-circle' })
  }
}

async function downloadAttachmentFile(attachmentId: string) {
  try {
    const config = useRuntimeConfig()
    const token = useCookie('auth_token')
    const response = await fetch(`${config.public.apiBase}/api/documents/${documentId.value}/attachments/${attachmentId}`, {
      headers: token.value ? { Authorization: `Bearer ${token.value}` } : {},
    })
    if (!response.ok) throw new Error('Download failed')
    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'attachment.pdf'
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    toast.add({ title: 'Xatolik', description: 'Faylni yuklab bo\'lmadi', color: 'error', icon: 'i-lucide-alert-circle' })
  }
}

async function handleDelete() {
  try {
    await deleteDocument(documentId.value)
    toast.add({ title: 'Muvaffaqiyat', description: 'Hujjat o\'chirildi', color: 'success', icon: 'i-lucide-check-circle' })
    navigateTo(`/archive/${categoryId.value}`)
  } catch {
    toast.add({ title: 'Xatolik', description: 'O\'chirib bo\'lmadi', color: 'error', icon: 'i-lucide-alert-circle' })
  }
}
</script>

<template>
  <PagePanel :title="doc?.title || 'Hujjat'" icon="i-lucide-file-text">
    <template #headerLeft>
      <UButton icon="i-lucide-arrow-left" variant="ghost" :to="`/archive/${categoryId}`" />
    </template>
    <template #headerRight>
      <div class="flex gap-2">
        <UButton
          v-if="fileUrl"
          icon="i-lucide-download"
          label="Yuklab olish"
          variant="outline"
          @click="downloadFile"
        />
        <UButton
          icon="i-lucide-pencil"
          label="Tahrirlash"
          variant="soft"
          :to="`/archive/${categoryId}/${documentId}/edit`"
        />
        <UButton
          icon="i-lucide-trash-2"
          label="O'chirish"
          color="error"
          variant="soft"
          @click="deleteOpen = true"
        />
      </div>
    </template>

    <div v-if="doc" class="flex h-full">
      <!-- Left: PDF Preview -->
      <div v-if="activePdfUrl" class="w-3/5 shrink-0 border-r border-default flex flex-col">
        <!-- Tab bar for switching between main file and attachments -->
        <div v-if="doc.attachments?.length" class="shrink-0 border-b border-default px-3 py-1.5 flex items-center gap-1 overflow-x-auto bg-elevated/30">
          <UButton
            v-if="isPdf && fileUrl"
            size="xs"
            :variant="activePdfUrl === fileUrl ? 'solid' : 'ghost'"
            label="Asosiy hujjat"
            icon="i-lucide-file-text"
            @click="viewMainFile"
          />
          <UButton
            v-for="att in doc.attachments"
            :key="att.id"
            size="xs"
            :variant="activePdfUrl?.includes(att.id) ? 'solid' : 'ghost'"
            :label="att.original_filename"
            icon="i-lucide-paperclip"
            @click="viewAttachment(att.id, att.original_filename)"
          />
        </div>
        <ClientOnly>
          <DocumentPdfViewer
            :key="activePdfUrl"
            :pdf-url="activePdfUrl"
            class="flex-1"
          />
          <template #fallback>
            <div class="flex items-center justify-center h-full">
              <div class="animate-pulse flex items-center gap-2 text-muted">
                <UIcon name="i-lucide-loader-2" class="animate-spin" />
                PDF yuklanmoqda...
              </div>
            </div>
          </template>
        </ClientOnly>
      </div>

      <!-- Right: Document details -->
      <div class="flex-1 overflow-y-auto">
        <div class="p-6 space-y-6 max-w-2xl" :class="{ 'mx-auto': !isPdf || !fileUrl }">

          <!-- File download for non-PDF files -->
          <div v-if="fileUrl && !isPdf" class="flex items-center gap-3 p-4 rounded-xl bg-elevated/50 border border-default">
            <div class="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
              <UIcon name="i-lucide-file" class="text-primary text-lg" />
            </div>
            <div class="flex-1">
              <p class="text-sm font-medium text-highlighted">Biriktirilgan fayl</p>
              <p class="text-xs text-muted">Faylni yuklab olish mumkin</p>
            </div>
            <UBadge
              v-if="doc.ocr_status"
              :label="OCR_STATUS_LABELS[doc.ocr_status]"
              :icon="OCR_STATUS_ICONS[doc.ocr_status]"
              :color="OCR_STATUS_COLORS[doc.ocr_status]"
              variant="subtle"
              size="sm"
              :ui="{ leadingIcon: doc.ocr_status === 'processing' ? 'animate-spin' : '' }"
              class="shrink-0"
            />
            <UButton
              icon="i-lucide-download"
              label="Yuklab olish"
              variant="soft"
              size="sm"
              @click="downloadFile"
            />
          </div>

          <!-- No file -->
          <div v-if="!fileUrl" class="flex items-center gap-3 p-4 rounded-xl bg-elevated/50 border border-default">
            <div class="w-10 h-10 rounded-lg bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center shrink-0">
              <UIcon name="i-lucide-file-x" class="text-muted text-lg" />
            </div>
            <div>
              <p class="text-sm font-medium text-muted">Fayl biriktirilmagan</p>
            </div>
          </div>

          <!-- Common fields -->
          <UCard>
            <template #header>
              <div class="flex items-center gap-2">
                <UIcon name="i-lucide-file-text" class="text-primary" />
                <span class="font-semibold">Asosiy ma'lumotlar</span>
                <UBadge
                  v-if="doc.document_view && doc.document_view !== 'unknown'"
                  :label="DOCUMENT_VIEW_LABELS[doc.document_view]"
                  :color="documentViewColor"
                  variant="subtle"
                  size="sm"
                  class="ml-auto"
                />
              </div>
            </template>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <p class="text-sm text-muted mb-1">Hujjat raqami</p>
                <p class="text-highlighted font-semibold">{{ doc.document_number }}</p>
              </div>
              <div>
                <p class="text-sm text-muted mb-1">Sana</p>
                <p class="text-highlighted font-semibold">{{ formatDate(doc.date) }}</p>
              </div>
              <div>
                <p class="text-sm text-muted mb-1">Imzo qo'ygan shaxs</p>
                <p class="text-highlighted font-semibold">{{ doc.person_name || doc.signer || '-' }}</p>
                <p v-if="doc.person_position" class="text-xs text-muted">{{ doc.person_position }}</p>
              </div>
              <div>
                <p class="text-sm text-muted mb-1">{{ LABELS.pages_total }}</p>
                <p class="text-highlighted font-semibold">{{ doc.pages || '-' }}</p>
              </div>
              <div v-if="lookupArchiveFolder(doc.archive_folder_id)">
                <p class="text-sm text-muted mb-1">{{ LABELS.archive_folder }}</p>
                <p class="text-highlighted font-semibold">{{ lookupArchiveFolder(doc.archive_folder_id) }}</p>
              </div>
            </div>

            <div v-if="doc.short_desc" class="mt-4 pt-4 border-t border-default">
              <p class="text-sm text-muted mb-1">{{ LABELS.short_desc }}</p>
              <p class="text-highlighted font-semibold">{{ doc.short_desc }}</p>
            </div>
          </UCard>

          <!-- Hujjat tasnifi (Phase 3 universal fields). Yuboruvchi is hidden for
               Chiquvchi (outgoing) and Ichki (internal); Tili is hidden for
               Chiquvchi only — both match the form's visibility rules. -->
          <UCard
            v-if="doc.document_type_name || doc.document_form || (doc.sender && doc.document_view !== 'outgoing' && doc.document_view !== 'internal') || (doc.language && doc.document_view !== 'outgoing') || doc.related_document_number || doc.related_document_date"
          >
            <template #header>
              <div class="flex items-center gap-2">
                <UIcon name="i-lucide-list-tree" class="text-primary" />
                <span class="font-semibold">Hujjat tasnifi</span>
              </div>
            </template>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div v-if="doc.document_type_name">
                <p class="text-sm text-muted mb-1">{{ LABELS.document_type }}</p>
                <p class="text-highlighted font-semibold">{{ doc.document_type_name }}</p>
              </div>
              <div v-if="doc.document_form">
                <p class="text-sm text-muted mb-1">{{ LABELS.document_form }}</p>
                <p class="text-highlighted font-semibold">{{ doc.document_form }}</p>
              </div>
              <div v-if="doc.sender && doc.document_view !== 'outgoing' && doc.document_view !== 'internal'">
                <p class="text-sm text-muted mb-1">{{ LABELS.sender }}</p>
                <p class="text-highlighted font-semibold">{{ doc.sender }}</p>
              </div>
              <div v-if="doc.language && doc.document_view !== 'outgoing'">
                <p class="text-sm text-muted mb-1">{{ LABELS.language }}</p>
                <p class="text-highlighted font-semibold">{{ doc.language }}</p>
              </div>
              <div v-if="doc.related_document_number">
                <p class="text-sm text-muted mb-1">{{ LABELS.related_document_number }}</p>
                <p class="text-highlighted font-semibold">{{ doc.related_document_number }}</p>
              </div>
              <div v-if="doc.related_document_date">
                <p class="text-sm text-muted mb-1">{{ LABELS.related_document_date }}</p>
                <p class="text-highlighted font-semibold">{{ formatDate(doc.related_document_date) }}</p>
              </div>
            </div>
          </UCard>

          <!-- Conditional: Kiruvchi hujjat (incoming) -->
          <UCard
            v-if="doc.document_view === 'incoming' && (doc.outgoing_number || doc.outgoing_date || doc.note)"
          >
            <template #header>
              <div class="flex items-center gap-2">
                <UIcon name="i-lucide-inbox" class="text-primary" />
                <span class="font-semibold">{{ DOCUMENT_VIEW_LABELS.incoming }}</span>
              </div>
            </template>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div v-if="doc.outgoing_number">
                <p class="text-sm text-muted mb-1">{{ LABELS.outgoing_number }}</p>
                <p class="text-highlighted font-semibold">{{ doc.outgoing_number }}</p>
              </div>
              <div v-if="doc.outgoing_date">
                <p class="text-sm text-muted mb-1">{{ LABELS.outgoing_date }}</p>
                <p class="text-highlighted font-semibold">{{ formatDate(doc.outgoing_date) }}</p>
              </div>
            </div>
            <div v-if="doc.note" class="mt-4 pt-4 border-t border-default">
              <p class="text-sm text-muted mb-1">{{ LABELS.note }}</p>
              <p class="text-highlighted font-semibold whitespace-pre-wrap">{{ doc.note }}</p>
            </div>
          </UCard>

          <!-- Conditional: Chiquvchi hujjat (outgoing) — Yuborilgan sana is dropped. -->
          <UCard v-else-if="doc.document_view === 'outgoing' && doc.recipient_organization">
            <template #header>
              <div class="flex items-center gap-2">
                <UIcon name="i-lucide-send" class="text-primary" />
                <span class="font-semibold">{{ DOCUMENT_VIEW_LABELS.outgoing }}</span>
              </div>
            </template>
            <div>
              <p class="text-sm text-muted mb-1">{{ LABELS.recipient_organization }}</p>
              <p class="text-highlighted font-semibold">{{ doc.recipient_organization }}</p>
            </div>
          </UCard>

          <!-- Conditional: Murojaat (appeal) -->
          <UCard v-else-if="doc.document_view === 'appeal'">
            <template #header>
              <div class="flex items-center gap-2">
                <UIcon name="i-lucide-megaphone" class="text-primary" />
                <span class="font-semibold">{{ DOCUMENT_VIEW_LABELS.appeal }}</span>
              </div>
            </template>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div v-if="lookupRegionName(doc.region_id)">
                <p class="text-sm text-muted mb-1">Hudud</p>
                <p class="text-highlighted font-semibold">{{ lookupRegionName(doc.region_id) }}</p>
              </div>
              <div v-if="lookupRegionName(doc.country_id)">
                <p class="text-sm text-muted mb-1">Davlat</p>
                <p class="text-highlighted font-semibold">{{ lookupRegionName(doc.country_id) }}</p>
              </div>
              <div v-if="lookupReceptionPlace(doc.reception_place_id)" class="sm:col-span-2">
                <p class="text-sm text-muted mb-1">{{ LABELS.reception_place }}</p>
                <p class="text-highlighted font-semibold">{{ lookupReceptionPlace(doc.reception_place_id) }}</p>
              </div>
              <div v-if="lookupAppealType(doc.appeal_type_id)">
                <p class="text-sm text-muted mb-1">{{ LABELS.appeal_type }}</p>
                <p class="text-highlighted font-semibold">{{ lookupAppealType(doc.appeal_type_id) }}</p>
              </div>
              <div v-if="doc.person_type">
                <p class="text-sm text-muted mb-1">{{ LABELS.person_type }}</p>
                <p class="text-highlighted font-semibold">{{ doc.person_type }}</p>
              </div>
              <div v-if="doc.outgoing_number">
                <p class="text-sm text-muted mb-1">{{ LABELS.outgoing_number }}</p>
                <p class="text-highlighted font-semibold">{{ doc.outgoing_number }}</p>
              </div>
              <div v-if="doc.outgoing_date">
                <p class="text-sm text-muted mb-1">{{ LABELS.outgoing_date }}</p>
                <p class="text-highlighted font-semibold">{{ formatDate(doc.outgoing_date) }}</p>
              </div>
              <div v-if="doc.signed_by" class="sm:col-span-2">
                <p class="text-sm text-muted mb-1">{{ signedByLabel }}</p>
                <p class="text-highlighted font-semibold">{{ doc.signed_by }}</p>
              </div>
            </div>

            <div v-if="doc.note" class="mt-4 pt-4 border-t border-default">
              <p class="text-sm text-muted mb-1">{{ LABELS.note }}</p>
              <p class="text-highlighted font-semibold whitespace-pre-wrap">{{ doc.note }}</p>
            </div>
          </UCard>

          <!-- Dynamic fields -->
          <UCard v-if="fields?.length && doc.field_values.length">
            <template #header>
              <div class="flex items-center gap-2">
                <UIcon name="i-lucide-layers" class="text-primary" />
                <span class="font-semibold">Qo'shimcha maydonlar</span>
              </div>
            </template>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div v-for="field in fields" :key="field.id">
                <p class="text-sm text-muted mb-1">{{ field.label }}</p>
                <p class="text-highlighted font-semibold">{{ getFieldValue(field.id) }}</p>
              </div>
            </div>
          </UCard>

          <!-- Attachments (Ilovalar) -->
          <UCard v-if="doc.attachments?.length">
            <template #header>
              <div class="flex items-center gap-2">
                <UIcon name="i-lucide-paperclip" class="text-primary" />
                <span class="text-lg font-bold">Ilovalar</span>
                <UBadge :label="`${doc.attachments.length}`" variant="subtle" size="sm" />
              </div>
            </template>

            <div class="space-y-2">
              <div
                v-for="att in doc.attachments"
                :key="att.id"
                class="flex items-center gap-3 p-3 rounded-lg border border-default hover:bg-elevated/50 transition-colors cursor-pointer"
                :class="{ 'ring-1 ring-primary bg-primary/5': activePdfUrl?.includes(att.id) }"
                @click="viewAttachment(att.id, att.original_filename)"
              >
                <UIcon name="i-lucide-file-text" class="text-primary shrink-0 text-lg" />
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-highlighted truncate">{{ att.original_filename }}</p>
                </div>
                <UBadge
                  v-if="att.ocr_status"
                  :label="OCR_STATUS_LABELS[att.ocr_status]"
                  :icon="OCR_STATUS_ICONS[att.ocr_status]"
                  :color="OCR_STATUS_COLORS[att.ocr_status]"
                  variant="subtle"
                  size="xs"
                  :ui="{ leadingIcon: att.ocr_status === 'processing' ? 'animate-spin' : '' }"
                  class="shrink-0"
                />
                <UButton
                  icon="i-lucide-download"
                  variant="ghost"
                  size="xs"
                  @click.stop="downloadAttachmentFile(att.id)"
                />
              </div>
            </div>
          </UCard>
        </div>
      </div>
    </div>
  </PagePanel>

  <UModal v-model:open="deleteOpen" title="Hujjatni o'chirish" description="Bu amalni qaytarib bo'lmaydi.">
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton variant="ghost" label="Bekor qilish" @click="deleteOpen = false" />
        <UButton color="error" label="O'chirish" icon="i-lucide-trash-2" @click="handleDelete" />
      </div>
    </template>
  </UModal>
</template>
