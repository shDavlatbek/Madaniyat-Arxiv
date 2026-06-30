<script setup lang="ts">
import {
  LABELS,
  OCR_STATUS_LABELS,
  OCR_STATUS_COLORS,
  OCR_STATUS_ICONS,
} from '~/utils/labels'

definePageMeta({ layout: 'dashboard' })

const route = useRoute()
const { getDocument, deleteDocument, uploadFile } = useMusicSchool()
const toast = useToast()
const config = useRuntimeConfig()

const id = computed(() => route.params.id as string)
const uploadProgress = ref(false)
const deleteOpen = ref(false)

const { data: selectedDoc, refresh: refreshSelectedDoc } = await useAsyncData(
  `music-school-doc-detail-${id.value}`,
  () => getDocument(id.value)
)

// Poll for OCR status changes
const ocrPolling = ref<ReturnType<typeof setInterval> | null>(null)

watchEffect(() => {
  if (!import.meta.client) return
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

// File URL computed
const fileUrl = computed(() => {
  if (!selectedDoc.value?.file_path) return null
  return `${config.public.apiBase}/api/music-school-documents/${selectedDoc.value.id}/file`
})

// File download helper
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

// Delete helper
async function handleDelete() {
  try {
    await deleteDocument(id.value)
    toast.add({
      title: 'Muvaffaqiyat',
      description: 'Hujjat tizimdan o‘chirildi',
      color: 'success',
      icon: 'i-lucide-check-circle',
    })
    deleteOpen.value = false
    navigateTo('/music-school-archive')
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
</script>

<template>
  <PagePanel :title="selectedDoc?.student_full_name || 'Hujjat tafsilotlari'" icon="i-lucide-music-4">
    <template #headerLeft>
      <UButton
        icon="i-lucide-arrow-left"
        variant="ghost"
        to="/music-school-archive"
      />
    </template>
    <template #headerRight>
      <div v-if="selectedDoc" class="flex gap-2">
        <UButton
          icon="i-lucide-pencil"
          variant="soft"
          label="Tahrirlash"
          :to="`/music-school-archive/${selectedDoc.id}/edit`"
        />
        <UButton
          icon="i-lucide-trash-2"
          variant="soft"
          color="error"
          label="O‘chirish"
          @click="deleteOpen = true"
        />
      </div>
    </template>

    <div v-if="selectedDoc" class="flex h-full overflow-hidden">
      <!-- Left Pane: Metadata Details (40% width) -->
      <div class="w-2/5 shrink-0 border-r border-default flex flex-col overflow-y-auto bg-elevated/10 p-5 space-y-5">
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

            <div v-if="selectedDoc.passport_series || selectedDoc.passport_number || selectedDoc.pinfl" class="pt-2 border-t border-default grid grid-cols-2 gap-4">
              <div v-if="selectedDoc.passport_series || selectedDoc.passport_number">
                <p class="text-xs text-muted mb-0.5">Pasport ma'lumoti</p>
                <p class="text-sm font-mono font-semibold text-highlighted">
                  {{ selectedDoc.passport_series || '' }} {{ selectedDoc.passport_number || '' }}
                </p>
              </div>
              <div v-if="selectedDoc.pinfl">
                <p class="text-xs text-muted mb-0.5">JShShIR (PINFL)</p>
                <p class="text-sm font-mono font-semibold text-highlighted">{{ selectedDoc.pinfl }}</p>
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
              <span class="font-semibold text-highlighted">Raqamlashtirilgan matn (Matn)</span>
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
  </PagePanel>

  <!-- Delete confirm modal -->
  <UModal
    v-model:open="deleteOpen"
    title="Diplom hujjatini o‘chirish"
    :description="selectedDoc ? `«${selectedDoc.student_full_name}» o‘quvchisiga tegishli diplom hujjatini butunlay o‘chirib tashlashni tasdiqlaysizmi? Ushbu amalni qaytarib bo‘lmaydi.` : ''"
  >
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton variant="ghost" label="Bekor qilish" @click="deleteOpen = false" />
        <UButton color="error" label="O‘chirish" icon="i-lucide-trash-2" @click="handleDelete" />
      </div>
    </template>
  </UModal>
</template>
