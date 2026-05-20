<script setup lang="ts">
import type { MusicSchoolResponse, MusicSchoolSpecialtyResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const { isAdmin, isMusicSchool, musicSchoolId } = useAuth()
const {
  listSchools,
  listSpecialties,
  createSpecialty,
  deleteSpecialty,
  importSpecialties,
} = useMusicSchool()
const toast = useToast()

// --- State Variables ---
const specialties = ref<MusicSchoolSpecialtyResponse[]>([])
const loading = ref(false)
const saving = ref(false)
const searchQ = ref('')
const newSpecialtyName = ref('')

// Tenancy / School Selection
const schools = ref<MusicSchoolResponse[]>([])
const selectedSchoolId = ref<string>('')
const activeSchool = ref<MusicSchoolResponse | null>(null)

// Import Feature State
const importModalOpen = ref(false)
const sourceSchoolId = ref('')
const sourceSpecialties = ref<MusicSchoolSpecialtyResponse[]>([])
const sourceSpecialtiesLoading = ref(false)
const selectedSpecialtyIds = ref<string[]>([])
const importing = ref(false)

const breadcrumbItems = computed(() => {
  return [
    { label: 'Arxivist', icon: 'i-lucide-archive', to: '/archive' },
    { label: 'Musiqa maktabi arxivi', icon: 'i-lucide-music-4', to: '/music-school-archive' },
    { label: 'Mutaxassisliklar', icon: 'i-lucide-settings-2' },
  ]
})

const schoolOptions = computed(() =>
  schools.value.map(s => ({ label: s.name, value: s.id }))
)

const importSchoolOptions = computed(() =>
  schools.value
    .filter(s => s.id !== activeSchoolId.value)
    .map(s => ({ label: s.name, value: s.id }))
)

// Active school resolution
const activeSchoolId = computed(() => {
  if (isMusicSchool.value) {
    return musicSchoolId.value || ''
  }
  return selectedSchoolId.value
})

async function fetchSchools() {
  try {
    const res = await listSchools()
    schools.value = res.items
    
    // Auto-select first school for admin if none selected
    if (isAdmin.value && !selectedSchoolId.value && schools.value.length > 0) {
      selectedSchoolId.value = schools.value[0].id
    }
  } catch (err) {
    console.error('Maktablarni yuklashda xatolik:', err)
  }
}

async function fetchSpecialties() {
  if (!activeSchoolId.value) {
    specialties.value = []
    return
  }
  loading.value = true
  try {
    specialties.value = await listSpecialties(activeSchoolId.value)
    // Resolve active school details
    activeSchool.value = schools.value.find(s => s.id === activeSchoolId.value) || null
  } catch (err: any) {
    toast.add({
      title: 'Xatolik',
      description: err?.data?.detail || 'Mutaxassisliklarni yuklab bo‘lmadi',
      color: 'error',
      icon: 'i-lucide-alert-circle',
    })
  } finally {
    loading.value = false
  }
}

// Add Specialty
async function handleCreate() {
  const name = newSpecialtyName.value.trim()
  if (!name || !activeSchoolId.value) return
  saving.value = true
  try {
    await createSpecialty(activeSchoolId.value, name)
    toast.add({
      title: 'Muvaffaqiyat',
      description: 'Yangi mutaxassislik muvaffaqiyatli qo‘shildi',
      color: 'success',
      icon: 'i-lucide-check-circle',
    })
    newSpecialtyName.value = ''
    fetchSpecialties()
  } catch (err: any) {
    toast.add({
      title: 'Xatolik',
      description: err?.data?.detail || 'Mutaxassislikni qo‘shib bo‘lmadi',
      color: 'error',
      icon: 'i-lucide-alert-circle',
    })
  } finally {
    saving.value = false
  }
}

// Delete Specialty
async function handleDelete(spec: MusicSchoolSpecialtyResponse) {
  if (!activeSchoolId.value) return
  try {
    await deleteSpecialty(activeSchoolId.value, spec.id)
    toast.add({
      title: 'Muvaffaqiyat',
      description: 'Mutaxassislik muvaffaqiyatli o‘chirildi',
      color: 'success',
      icon: 'i-lucide-check-circle',
    })
    fetchSpecialties()
  } catch (err: any) {
    toast.add({
      title: 'Xatolik',
      description: err?.data?.detail || 'Mutaxassislikni o‘chirib bo‘lmadi',
      color: 'error',
      icon: 'i-lucide-alert-circle',
    })
  }
}

// Load specialties for selected source school to import
async function loadSourceSpecialties() {
  if (!sourceSchoolId.value) {
    sourceSpecialties.value = []
    return
  }
  sourceSpecialtiesLoading.value = true
  selectedSpecialtyIds.value = []
  try {
    sourceSpecialties.value = await listSpecialties(sourceSchoolId.value)
  } catch (err: any) {
    toast.add({
      title: 'Xatolik',
      description: 'Manba maktab mutaxassisliklarini yuklab bo‘lmadi',
      color: 'error',
      icon: 'i-lucide-alert-circle',
    })
  } finally {
    sourceSpecialtiesLoading.value = false
  }
}

watch(sourceSchoolId, loadSourceSpecialties)

function openImport() {
  sourceSchoolId.value = ''
  sourceSpecialties.value = []
  selectedSpecialtyIds.value = []
  importModalOpen.value = true
}

// Submit Import
async function handleImport() {
  if (!activeSchoolId.value || !sourceSchoolId.value || !selectedSpecialtyIds.value.length) return
  importing.value = true
  try {
    const res = await importSpecialties(activeSchoolId.value, sourceSchoolId.value, selectedSpecialtyIds.value)
    toast.add({
      title: 'Muvaffaqiyat',
      description: `${res.length} ta mutaxassislik muvaffaqiyatli nusxalandi`,
      color: 'success',
      icon: 'i-lucide-check-circle',
    })
    importModalOpen.value = false
    fetchSpecialties()
  } catch (err: any) {
    toast.add({
      title: 'Xatolik',
      description: err?.data?.detail || 'Mutaxassisliklarni import qilib bo‘lmadi',
      color: 'error',
      icon: 'i-lucide-alert-circle',
    })
  } finally {
    importing.value = false
  }
}

// Filtered specialties for local listing
const filteredSpecialties = computed(() => {
  const q = searchQ.value.trim().toLowerCase()
  if (!q) return specialties.value
  return specialties.value.filter(s => s.name.toLowerCase().includes(q))
})

onMounted(async () => {
  await fetchSchools()
  if (isMusicSchool.value && musicSchoolId.value) {
    fetchSpecialties()
  }
})

watch(selectedSchoolId, () => {
  if (isAdmin.value) {
    fetchSpecialties()
  }
})
</script>

<template>
  <PagePanel title="Mutaxassisliklar va cholg‘ular" icon="i-lucide-settings-2">
    <template #headerRight>
      <UBadge :label="`${filteredSpecialties.length} ta mutaxassislik`" variant="subtle" class="mr-2" />
      <UButton
        v-if="activeSchoolId"
        label="Boshqa maktabdan nusxalash"
        icon="i-lucide-copy"
        variant="outline"
        class="mr-2"
        @click="openImport"
      />
    </template>

    <div class="p-5 space-y-6">
      <UBreadcrumb :items="breadcrumbItems" />

      <!-- Top controls layout: School selection (for admin) and quick add form -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <!-- Tenancy locking or selector -->
        <UCard class="lg:col-span-1">
          <template #header>
            <div class="flex items-center gap-2">
              <UIcon name="i-lucide-school" class="text-primary text-lg" />
              <span class="font-bold text-highlighted">Musiqa maktabi</span>
            </div>
          </template>

          <div class="space-y-4">
            <div v-if="isAdmin" class="space-y-2">
              <p class="text-xs text-muted">Boshqarish uchun maktabni tanlang:</p>
              <USelectMenu
                v-model="selectedSchoolId"
                :items="schoolOptions"
                value-key="value"
                placeholder="Maktabni tanlang"
                class="w-full"
                :search-input="{ placeholder: 'Maktabni qidirish...' }"
              />
            </div>
            
            <div v-else class="space-y-1">
              <p class="text-xs text-muted">Sizning maktabingiz:</p>
              <p class="text-sm font-semibold text-highlighted">
                {{ activeSchool ? activeSchool.name : 'Yuklanmoqda...' }}
              </p>
              <UBadge v-if="activeSchool?.code" :label="activeSchool.code" size="xs" variant="subtle" class="mt-1" />
            </div>
          </div>
        </UCard>

        <!-- Quick Add Specialty Form -->
        <UCard class="lg:col-span-2">
          <template #header>
            <div class="flex items-center gap-2">
              <UIcon name="i-lucide-plus-circle" class="text-primary text-lg" />
              <span class="font-bold text-highlighted">Yangi mutaxassislik qo‘shish</span>
            </div>
          </template>

          <div class="flex gap-3">
            <UInput
              v-model="newSpecialtyName"
              placeholder="Yangi mutaxassislik yoki cholg‘u nomi (masalan: Dutor, Skripka)"
              class="flex-1"
              size="lg"
              icon="i-lucide-music"
              :disabled="!activeSchoolId"
              @keyup.enter="handleCreate"
            />
            <UButton
              label="Qo‘shish"
              icon="i-lucide-plus"
              size="lg"
              :loading="saving"
              :disabled="!newSpecialtyName.trim() || !activeSchoolId"
              @click="handleCreate"
            />
          </div>
        </UCard>
      </div>

      <!-- Main Specialties List section -->
      <UCard>
        <template #header>
          <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <span class="font-bold text-highlighted text-base">Maktab mutaxassisliklari ro‘yxati</span>
            <div class="w-64">
              <UInput
                v-model="searchQ"
                placeholder="Mutaxassislikni qidirish..."
                icon="i-lucide-search"
                size="md"
              />
            </div>
          </div>
        </template>

        <div v-if="loading" class="p-12 text-center text-muted flex items-center justify-center gap-2">
          <UIcon name="i-lucide-loader-2" class="animate-spin text-primary text-xl" />
          Yuklanmoqda...
        </div>

        <div v-else-if="!filteredSpecialties.length" class="p-12 text-center text-muted">
          <EmptyState
            icon="i-lucide-music-3"
            title="Mutaxassisliklar mavjud emas"
            description="Ushbu maktabda hech qanday mutaxassislik qo‘shilmagan. Yuqoridan yangi qo‘shing yoki boshqa maktabdan nusxalang."
          />
        </div>

        <!-- Specialties Grid -->
        <div v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          <div
            v-for="spec in filteredSpecialties"
            :key="spec.id"
            class="group relative flex items-center justify-between rounded-xl border border-default bg-elevated/20 p-4 transition-all duration-150 hover:border-primary/45 hover:bg-elevated/40"
          >
            <div class="flex items-center gap-2 min-w-0">
              <UIcon name="i-lucide-music" class="text-primary shrink-0" />
              <span class="font-semibold text-highlighted truncate text-sm">{{ spec.name }}</span>
            </div>

            <UTooltip text="O‘chirish" class="shrink-0">
              <UButton
                icon="i-lucide-trash-2"
                variant="ghost"
                color="error"
                size="xs"
                class="opacity-0 group-hover:opacity-100 transition-opacity"
                @click="handleDelete(spec)"
              />
            </UTooltip>
          </div>
        </div>
      </UCard>
    </div>

    <!-- Import modal -->
    <UModal v-model:open="importModalOpen" title="Boshqa musiqiy maktabdan nusxalash">
      <template #body>
        <div class="space-y-4">
          <UFormField label="Nusxa olinadigan musiqa maktabi" required>
            <USelectMenu
              v-model="sourceSchoolId"
              :items="importSchoolOptions"
              value-key="value"
              placeholder="Maktabni tanlang"
              class="w-full"
              :search-input="{ placeholder: 'Maktabni qidirish...' }"
            />
          </UFormField>

          <div v-if="sourceSchoolId" class="border border-default rounded-xl overflow-hidden bg-elevated/5">
            <div class="p-3 border-b border-default bg-elevated/10 flex justify-between items-center">
              <span class="text-sm font-semibold text-highlighted">Mutaxassisliklarni tanlang</span>
              <span class="text-xs text-muted">{{ selectedSpecialtyIds.length }} ta tanlandi</span>
            </div>

            <div v-if="sourceSpecialtiesLoading" class="p-8 text-center text-muted flex items-center justify-center gap-2">
              <UIcon name="i-lucide-loader-2" class="animate-spin text-primary" />
              Yuklanmoqda...
            </div>

            <div v-else-if="!sourceSpecialties.length" class="p-8 text-center text-muted text-sm">
              Tanlangan maktabda mutaxassisliklar topilmadi.
            </div>

            <div v-else class="max-h-60 overflow-y-auto divide-y divide-default p-2 space-y-1">
              <div
                v-for="spec in sourceSpecialties"
                :key="spec.id"
                class="flex items-center gap-2 p-2 rounded-lg hover:bg-elevated/5"
              >
                <input
                  :id="spec.id"
                  v-model="selectedSpecialtyIds"
                  type="checkbox"
                  :value="spec.id"
                  class="rounded border-default text-primary focus:ring-primary w-4 h-4"
                />
                <label :for="spec.id" class="text-sm text-highlighted font-medium cursor-pointer flex-1 select-none">
                  {{ spec.name }}
                </label>
              </div>
            </div>
          </div>
        </div>
      </template>

      <template #footer>
        <div class="flex justify-end gap-2">
          <UButton variant="ghost" label="Bekor qilish" @click="importModalOpen = false" />
          <UButton
            label="Nusxalash"
            icon="i-lucide-copy"
            :loading="importing"
            :disabled="!sourceSchoolId || !selectedSpecialtyIds.length"
            @click="handleImport"
          />
        </div>
      </template>
    </UModal>
  </PagePanel>
</template>
