<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { MusicSchoolSpecialtyResponse, MusicSchoolResponse } from '~/types'

const props = defineProps<{
  open: boolean
  schoolId: string
}>()

const emit = defineEmits<{
  (e: 'update:open', val: boolean): void
  (e: 'change'): void
}>()

const isOpen = computed({
  get: () => props.open,
  set: (val) => emit('update:open', val)
})

const { listSpecialties, createSpecialty, deleteSpecialty, importSpecialties, listSchools } = useMusicSchool()
const toast = useToast()

const specialties = ref<MusicSchoolSpecialtyResponse[]>([])
const loading = ref(false)
const saving = ref(false)
const newSpecialtyName = ref('')

// Import feature states
const importModalOpen = ref(false)
const sourceSchoolId = ref('')
const sourceSpecialties = ref<MusicSchoolSpecialtyResponse[]>([])
const sourceSpecialtiesLoading = ref(false)
const selectedSpecialtyIds = ref<string[]>([])
const importing = ref(false)
const allSchools = ref<MusicSchoolResponse[]>([])

const schoolOptions = computed(() =>
  allSchools.value
    .filter(s => s.id !== props.schoolId)
    .map(s => ({ label: s.name, value: s.id }))
)

// Fetch specialties for current school
async function fetchSpecialties() {
  if (!props.schoolId) return
  loading.value = true
  try {
    specialties.value = await listSpecialties(props.schoolId)
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

// Add new specialty
async function handleCreate() {
  const name = newSpecialtyName.value.trim()
  if (!name || !props.schoolId) return
  saving.value = true
  try {
    await createSpecialty(props.schoolId, name)
    toast.add({
      title: 'Muvaffaqiyat',
      description: 'Yangi mutaxassislik muvaffaqiyatli qo‘shildi',
      color: 'success',
      icon: 'i-lucide-check-circle',
    })
    newSpecialtyName.value = ''
    fetchSpecialties()
    emit('change')
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

// Delete specialty
async function handleDelete(spec: MusicSchoolSpecialtyResponse) {
  if (!props.schoolId) return
  try {
    await deleteSpecialty(props.schoolId, spec.id)
    toast.add({
      title: 'Muvaffaqiyat',
      description: 'Mutaxassislik muvaffaqiyatli o‘chirildi',
      color: 'success',
      icon: 'i-lucide-check-circle',
    })
    fetchSpecialties()
    emit('change')
  } catch (err: any) {
    toast.add({
      title: 'Xatolik',
      description: err?.data?.detail || 'Mutaxassislikni o‘chirib bo‘lmadi',
      color: 'error',
      icon: 'i-lucide-alert-circle',
    })
  }
}

// Fetch all schools for importing
async function fetchSchools() {
  try {
    const res = await listSchools()
    allSchools.value = res.items
  } catch (err) {
    console.error('Maktablarni yuklashda xatolik:', err)
  }
}

// Load specialties for selected source school
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
  fetchSchools()
  importModalOpen.value = true
}

// Submit Import
async function handleImport() {
  if (!props.schoolId || !sourceSchoolId.value || !selectedSpecialtyIds.value.length) return
  importing.value = true
  try {
    const res = await importSpecialties(props.schoolId, sourceSchoolId.value, selectedSpecialtyIds.value)
    toast.add({
      title: 'Muvaffaqiyat',
      description: `${res.length} ta mutaxassislik muvaffaqiyatli nusxalandi`,
      color: 'success',
      icon: 'i-lucide-check-circle',
    })
    importModalOpen.value = false
    fetchSpecialties()
    emit('change')
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

watch(() => props.open, (val) => {
  if (val) {
    fetchSpecialties()
  }
})
</script>

<template>
  <UModal v-model:open="isOpen" title="Mutaxassisliklar va cholg‘ularni boshqarish">
    <template #body>
      <div class="space-y-6">
        <!-- Add specialty field -->
        <div class="flex gap-2">
          <UInput
            v-model="newSpecialtyName"
            placeholder="Yangi mutaxassislik nomi (masalan: Fortepiano)"
            class="flex-1"
            size="lg"
            icon="i-lucide-music"
            @keyup.enter="handleCreate"
          />
          <UButton
            label="Qo‘shish"
            icon="i-lucide-plus"
            :loading="saving"
            :disabled="!newSpecialtyName.trim()"
            @click="handleCreate"
          />
        </div>

        <!-- Specialties list -->
        <div class="border border-default rounded-xl overflow-hidden bg-elevated/5">
          <div class="p-3 border-b border-default bg-elevated/10 flex justify-between items-center">
            <span class="text-sm font-semibold text-highlighted">Mavjud mutaxassisliklar</span>
            <UButton
              label="Boshqa maktabdan nusxalash"
              icon="i-lucide-copy"
              variant="outline"
              size="xs"
              @click="openImport"
            />
          </div>

          <div v-if="loading" class="p-8 text-center text-muted flex items-center justify-center gap-2">
            <UIcon name="i-lucide-loader-2" class="animate-spin text-primary" />
            Yuklanmoqda...
          </div>

          <div v-else-if="!specialties.length" class="p-8 text-center text-muted text-sm">
            Mutaxassisliklar qo‘shilmagan. Yuqoridan yangi qo‘shing yoki boshqa maktabdan nusxalang.
          </div>

          <div v-else class="max-h-60 overflow-y-auto divide-y divide-default">
            <div
              v-for="spec in specialties"
              :key="spec.id"
              class="p-3 flex justify-between items-center hover:bg-elevated/5 transition-colors"
            >
              <div class="flex items-center gap-2">
                <UIcon name="i-lucide-music" class="text-primary text-sm" />
                <span class="text-sm text-highlighted font-medium">{{ spec.name }}</span>
              </div>
              <UButton
                icon="i-lucide-trash-2"
                variant="ghost"
                color="error"
                size="xs"
                @click="handleDelete(spec)"
              />
            </div>
          </div>
        </div>
      </div>
    </template>
    
    <template #footer>
      <UButton label="Yopish" variant="ghost" @click="isOpen = false" />
    </template>
  </UModal>

  <!-- Import/Copy Modal -->
  <UModal v-model:open="importModalOpen" title="Boshqa musiqiy maktabdan nusxalash">
    <template #body>
      <div class="space-y-4">
        <UFormField label="Manba musiqa maktabi" required>
          <USelectMenu
            v-model="sourceSchoolId"
            :items="schoolOptions"
            value-key="value"
            placeholder="Nusxa olinadigan maktabni tanlang"
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
            Mutaxassisliklar yuklanmoqda...
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
        <UButton label="Bekor qilish" variant="ghost" @click="importModalOpen = false" />
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
</template>
