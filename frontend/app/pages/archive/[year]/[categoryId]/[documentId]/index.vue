<script setup lang="ts">
import type { CategoryFieldResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const route = useRoute()
const year = computed(() => Number(route.params.year))
const categoryId = computed(() => route.params.categoryId as string)
const documentId = computed(() => route.params.documentId as string)

const { getDocument, deleteDocument } = useDocuments()
const { apiFetch } = useApi()
const toast = useToast()
const config = useRuntimeConfig()
const deleteOpen = ref(false)

const { data: doc } = await useAsyncData(`doc-${documentId.value}`, () => getDocument(documentId.value))
const { data: fields } = await useAsyncData(`fields-${categoryId.value}`, () =>
  apiFetch<CategoryFieldResponse[]>(`/api/categories/${categoryId.value}/fields`)
)

function getFieldValue(fieldId: string) {
  return doc.value?.field_values.find(fv => fv.category_field_id === fieldId)?.value || '-'
}

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
    navigateTo(`/archive/${year.value}`)
  } catch {
    toast.add({ title: 'Xatolik', description: 'O\'chirib bo\'lmadi', color: 'error', icon: 'i-lucide-alert-circle' })
  }
}
</script>

<template>
  <PagePanel :title="doc?.title || 'Hujjat'" icon="i-lucide-file-text">
    <template #headerLeft>
      <UButton icon="i-lucide-arrow-left" variant="ghost" :to="`/archive/${year}`" />
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
          :to="`/archive/${year}/${categoryId}/${documentId}/edit`"
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
              </div>
            </template>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <p class="text-highlighted font-semibold mb-1">Hujjat raqami</p>
                <p class="text-sm">{{ doc.document_number }}</p>
              </div>
              <div>
                <p class="text-highlighted font-semibold mb-1">Sana</p>
                <p class="text-sm">{{ doc.date ? doc.date.split('-').reverse().join('.') : '-' }}</p>
              </div>
              <div>
                <p class="text-highlighted font-semibold mb-1">Imzo qo'ygan shaxs</p>
                <p class="text-sm">{{ doc.person_name || doc.signer || '-' }}</p>
                <p v-if="doc.person_position" class="text-xs text-muted">{{ doc.person_position }}</p>
              </div>
              <div>
                <p class="text-highlighted font-semibold mb-1">Sahifalar</p>
                <p class="text-sm">{{ doc.pages || '-' }}</p>
              </div>
              <div>
                <p class="text-highlighted font-semibold mb-1">Arxiv tartib raqami</p>
                <p class="text-sm">{{ doc.archive_number || '-' }}</p>
              </div>
            </div>

            <div v-if="doc.short_desc" class="mt-4 pt-4 border-t border-default">
              <p class="text-highlighted font-semibold mb-1">Qisqacha tavsif</p>
              <p class="text-sm">{{ doc.short_desc }}</p>
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
                <p class="text-highlighted font-semibold mb-1">{{ field.label }}</p>
                <p class="text-sm">{{ getFieldValue(field.id) }}</p>
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
