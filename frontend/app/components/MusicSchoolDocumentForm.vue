<script setup lang="ts">
import { z } from 'zod'
import type { MusicSchoolResponse, MusicSchoolDocumentResponse } from '~/types'

const props = defineProps<{
  initialData?: MusicSchoolDocumentResponse | null
  saving?: boolean
}>()

const emit = defineEmits<{
  submit: [payload: Record<string, any>, file: File | null]
}>()

const { isAdmin, isMusicSchool, musicSchoolId } = useAuth()
const { listSchools, listSpecialties } = useMusicSchool()
const toast = useToast()

const loadingSpecialties = ref(false)

// Form schema definition
const schema = z.object({
  student_full_name: z.string().min(1, 'O‘quvchi F.I.Sh. kiritilishi shart'),
  passport_series: z.string().max(10).optional().or(z.literal('')),
  passport_number: z.string().max(20).optional().or(z.literal('')),
  pinfl: z.string().max(14).optional().or(z.literal('')),
  music_school_id: z.string().min(1, 'Musiqa maktabini tanlash shart'),
  specialty_id: z.string().min(1, 'Mutaxassislikni tanlash shart'),
  graduation_year: z.coerce.number().min(1900, 'Noto‘g‘ri yil kiritildi'),
  diploma_serial: z.string().min(1, 'Diplom seriyasi kiritilishi shart'),
  diploma_number: z.string().min(1, 'Diplom raqami kiritilishi shart'),
  given_date: z.string().min(1, 'Berilgan sana kiritilishi shart'),
  description: z.string().optional().or(z.literal('')),
})

// Form State
const state = reactive({
  student_full_name: props.initialData?.student_full_name || '',
  music_school_id: props.initialData?.music_school_id || (isMusicSchool.value ? musicSchoolId.value || '' : ''),
  specialty_id: props.initialData?.specialty_id || '',
  graduation_year: props.initialData?.graduation_year || new Date().getFullYear(),
  diploma_serial: props.initialData?.diploma_serial || '',
  diploma_number: props.initialData?.diploma_number || '',
  given_date: props.initialData?.given_date || '',
  description: props.initialData?.description || '',
  passport_series: props.initialData?.passport_series || '',
  passport_number: props.initialData?.passport_number || '',
  pinfl: props.initialData?.pinfl || '',
})

// Specialties list state
const schoolSpecialties = ref<any[]>([])
const schoolSpecialtyOptions = computed(() =>
  schoolSpecialties.value.map(s => ({ label: s.name, value: s.id }))
)

// Fetch specialties for selected school
async function fetchSchoolSpecialties() {
  if (!state.music_school_id) {
    schoolSpecialties.value = []
    return
  }
  loadingSpecialties.value = true
  try {
    schoolSpecialties.value = await listSpecialties(state.music_school_id)
  } catch (err) {
    console.error('Mutaxassisliklarni yuklashda xatolik:', err)
  } finally {
    loadingSpecialties.value = false
  }
}

watch(() => state.music_school_id, () => {
  // Clear specialty if school changes (unless it matches the initial load)
  if (props.initialData && state.music_school_id === props.initialData.music_school_id) {
    state.specialty_id = props.initialData.specialty_id
  } else {
    state.specialty_id = ''
  }
  fetchSchoolSpecialties()
}, { immediate: true })

// Schools list
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

// File state
const selectedFile = ref<File | null>(null)
const isDragging = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

function onFileChange(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files?.length) {
    selectedFile.value = target.files[0]
  }
}

function onDrop(event: DragEvent) {
  isDragging.value = false
  const file = event.dataTransfer?.files?.[0]
  if (file && file.type === 'application/pdf') {
    selectedFile.value = file
  } else if (file) {
    toast.add({
      title: 'Xatolik',
      description: 'Faqat PDF formatdagi fayllarni yuklash mumkin',
      color: 'error',
      icon: 'i-lucide-alert-circle',
    })
  }
}

function removeFile() {
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

function formatFileSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`
}

// Form Submission
function handleSubmit() {
  const payload = {
    student_full_name: state.student_full_name.trim(),
    music_school_id: state.music_school_id,
    specialty_id: state.specialty_id,
    graduation_year: Number(state.graduation_year),
    diploma_serial: state.diploma_serial.trim().toUpperCase(),
    diploma_number: state.diploma_number.trim(),
    given_date: state.given_date,
    description: state.description.trim() || null,
    passport_series: state.passport_series.trim().toUpperCase() || null,
    passport_number: state.passport_number.trim() || null,
    pinfl: state.pinfl.trim() || null,
  }
  emit('submit', payload, selectedFile.value)
}

onMounted(() => {
  fetchSchools()
})
</script>

<template>
  <UForm
    :schema="schema"
    :state="state"
    class="space-y-6"
    @submit="handleSubmit"
  >
    <div class="flex flex-col lg:flex-row gap-6">
      <!-- Left Column: Fields -->
      <div class="flex-1 space-y-6">
        <UCard :ui="{ body: 'space-y-5' }">
          <template #header>
            <div class="flex items-center gap-2">
              <UIcon name="i-lucide-user" class="text-primary" />
              <span class="font-bold text-highlighted text-sm">O‘quvchi va maktab ma‘lumotlari</span>
            </div>
          </template>

          <UFormField label="O‘quvchining to‘liq F.I.Sh." name="student_full_name" required>
            <UInput
              v-model="state.student_full_name"
              placeholder="Masalan: Karimov Saidislom Alisher o‘g‘li"
              icon="i-lucide-user"
              size="lg"
              class="w-full"
            />
          </UFormField>

          <!-- Passport details & PINFL -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
            <UFormField label="Pasport seriyasi" name="passport_series">
              <UInput
                v-model="state.passport_series"
                placeholder="KA"
                icon="i-lucide-hash"
                size="lg"
                class="w-full font-mono uppercase"
                maxlength="10"
                @update:model-value="val => state.passport_series = val.toUpperCase()"
              />
            </UFormField>

            <UFormField label="Pasport raqami" name="passport_number">
              <UInput
                v-model="state.passport_number"
                placeholder="1234567"
                icon="i-lucide-hash"
                size="lg"
                class="w-full font-mono"
                maxlength="20"
              />
            </UFormField>
          </div>

          <UFormField label="JShShIR (PINFL)" name="pinfl">
              <UInput
                v-model="state.pinfl"
                placeholder="14 ta raqam"
                icon="i-lucide-fingerprint"
                size="lg"
                class="w-full font-mono"
                maxlength="14"
              />
            </UFormField>

          <!-- School select for admin -->
          <UFormField v-if="isAdmin" label="Musiqa maktabi" name="music_school_id" required>
            <USelectMenu
              v-model="state.music_school_id"
              :items="schoolOptions"
              value-key="value"
              placeholder="Musiqa maktabini tanlang"
              class="w-full"
              size="lg"
              :search-input="{ placeholder: 'Maktabni qidirish...' }"
            />
          </UFormField>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
            <UFormField label="Cholg‘u / Mutaxassislik" name="specialty_id" required>
              <USelectMenu
                v-model="state.specialty_id"
                :items="schoolSpecialtyOptions"
                value-key="value"
                placeholder="Mutaxassislikni tanlang"
                class="w-full"
                size="lg"
                :loading="loadingSpecialties"
                :disabled="!state.music_school_id"
                :search-input="{ placeholder: 'Mutaxassislikni qidirish...' }"
              />
            </UFormField>

            <UFormField label="Bitirgan yili" name="graduation_year" required>
              <UInput
                v-model="state.graduation_year"
                type="number"
                icon="i-lucide-calendar"
                size="lg"
                class="w-full"
              />
            </UFormField>
          </div>
        </UCard>

        <!-- Diploma Serial, Number & Dates -->
        <UCard :ui="{ body: 'space-y-5' }">
          <template #header>
            <div class="flex items-center gap-2">
              <UIcon name="i-lucide-file-text" class="text-primary" />
              <span class="font-bold text-highlighted text-sm">Diplom hujjat ma‘lumotlari</span>
            </div>
          </template>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
            <UFormField label="Diplom seriyasi (katta harfda)" name="diploma_serial" required>
              <UInput
                v-model="state.diploma_serial"
                placeholder="Masalan: D"
                icon="i-lucide-hash"
                size="lg"
                maxlength="5"
                class="uppercase"
                @update:model-value="val => state.diploma_serial = val.toUpperCase()"
              />
            </UFormField>

            <UFormField label="Diplom raqami" name="diploma_number" required>
              <UInput
                v-model="state.diploma_number"
                placeholder="Masalan: 012345"
                icon="i-lucide-hash"
                size="lg"
              />
            </UFormField>
          </div>

          <UFormField label="Berilgan sana" name="given_date" required>
            <DatePicker v-model="state.given_date" size="lg" />
          </UFormField>

          <UFormField label="Eslatma / Izoh" name="description">
            <UTextarea
              v-model="state.description"
              placeholder="Diplom bo‘yicha qo‘shimcha izohlar"
              :rows="3"
              class="w-full"
            />
          </UFormField>
        </UCard>

        <!-- Actions -->
        <div class="flex justify-end gap-3">
          <UButton
            variant="outline"
            label="Bekor qilish"
            size="lg"
            to="/music-school-archive"
          />
          <UButton
            type="submit"
            :label="initialData ? 'Saqlash' : 'Qo‘shish'"
            icon="i-lucide-save"
            size="lg"
            :loading="saving"
          />
        </div>
      </div>

      <!-- Right Column: Dropzone File Upload -->
      <div class="w-full lg:w-80 xl:w-96 shrink-0 space-y-6">
        <UCard>
          <template #header>
            <div class="flex items-center gap-2">
              <UIcon name="i-lucide-paperclip" class="text-primary" />
              <span class="font-bold text-highlighted text-sm">Fayl yuklash</span>
            </div>
          </template>

          <div class="space-y-4">
            <!-- Indicator if PDF exists already -->
            <div
              v-if="initialData?.file_path && !selectedFile"
              class="flex items-center gap-3 p-3 rounded-xl bg-primary-50 dark:bg-primary-950/50 border border-primary-200 dark:border-primary-900"
            >
              <div class="w-10 h-10 rounded-lg bg-primary-100 dark:bg-primary-900 flex items-center justify-center shrink-0">
                <UIcon name="i-lucide-file-check-2" class="w-5 h-5 text-primary-600 dark:text-primary-400" />
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-xs font-semibold text-highlighted">Skaner PDF yuklangan</p>
                <p class="text-[10px] text-muted leading-tight mt-0.5">Yangi PDF tanlasangiz, mavjud fayl o‘rniga yoziladi</p>
              </div>
            </div>

            <!-- Dropzone -->
            <label
              for="doc-file-input"
              class="relative flex flex-col items-center justify-center w-full min-h-52 border-2 border-dashed rounded-xl cursor-pointer transition-all duration-200"
              :class="[
                selectedFile
                  ? 'border-primary-400 bg-primary-50/30 dark:bg-primary-950/20'
                  : isDragging
                    ? 'border-primary-500 bg-primary-50 dark:bg-primary-950/50 scale-[1.01]'
                    : 'border-default hover:border-primary-400 hover:bg-elevated/40',
              ]"
              @dragover.prevent="isDragging = true"
              @dragleave.prevent="isDragging = false"
              @drop.prevent="onDrop"
            >
              <!-- Selected state -->
              <div v-if="selectedFile" class="flex flex-col items-center gap-3 px-4 py-4">
                <div class="w-12 h-12 rounded-xl bg-primary-100 dark:bg-primary-900 flex items-center justify-center shrink-0">
                  <UIcon name="i-lucide-file-text" class="w-6 h-6 text-primary-600 dark:text-primary-400" />
                </div>
                <div class="text-center min-w-0">
                  <p class="text-sm font-semibold text-highlighted truncate max-w-52">{{ selectedFile.name }}</p>
                  <p class="text-xs text-muted mt-0.5">{{ formatFileSize(selectedFile.size) }}</p>
                </div>
              </div>

              <!-- Unselected state -->
              <div v-else class="flex flex-col items-center gap-2 py-8 px-4">
                <div class="w-12 h-12 rounded-full bg-elevated flex items-center justify-center mb-1">
                  <UIcon name="i-lucide-upload-cloud" class="w-6 h-6 text-muted" />
                </div>
                <p class="text-xs font-semibold text-highlighted text-center">
                  Faylni tashlang yoki
                  <span class="text-primary-600 dark:text-primary-400">tallang</span>
                </p>
                <p class="text-[10px] text-muted text-center">Faqat PDF formatidagi diplom skaneri</p>
              </div>

              <input
                id="doc-file-input"
                ref="fileInput"
                type="file"
                class="hidden"
                accept=".pdf"
                @change="onFileChange"
              />
            </label>

            <!-- Clear button -->
            <div v-if="selectedFile" class="flex justify-center">
              <UButton
                variant="ghost"
                size="xs"
                color="error"
                icon="i-lucide-trash-2"
                label="Faylni olib tashlash"
                @click.prevent="removeFile"
              />
            </div>
          </div>
        </UCard>
      </div>
    </div>
  </UForm>
</template>
