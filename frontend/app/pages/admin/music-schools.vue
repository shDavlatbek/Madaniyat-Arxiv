<script setup lang="ts">
import type { MusicSchoolResponse } from '~/types'
import type { LocationRegion, LocationDistrict } from '~/composables/useReferences'

definePageMeta({ layout: 'dashboard' })

const { listSchools, createSchool, updateSchool, deleteSchool } = useMusicSchool()
const { listLocationRegions, listLocationDistricts } = useReferences()
const toast = useToast()

const schools = ref<MusicSchoolResponse[]>([])
const loading = ref(false)
const searchQ = ref('')

// Region and district references fetched from the backend
const regions = ref<LocationRegion[]>([])
const districts = ref<LocationDistrict[]>([])

// Create / edit modal state
const modalOpen = ref(false)
const editing = ref<MusicSchoolResponse | null>(null)
const state = reactive({ name: '', code: '', region: undefined as string | undefined, district: '' })
const saving = ref(false)

// Region options computed from fetched data
const regionOptions = computed(() =>
  regions.value.map(r => ({ label: r.name_uz, value: r.name_uz }))
)

// Active selected region object
const selectedRegionObj = computed(() => {
  return regions.value.find(r => r.name_uz === state.region)
})

// Cascading District options
const districtOptions = computed(() => {
  if (!selectedRegionObj.value) return []
  return districts.value
    .filter(d => d.region_id === selectedRegionObj.value.id)
    .map(d => ({ label: d.name_uz, value: d.name_uz }))
})

// Watch region to reset district if it's no longer valid
watch(
  () => state.region,
  (newReg, oldReg) => {
    if (newReg === undefined) {
      state.district = ''
      return
    }
    const regionObj = regions.value.find(r => r.name_uz === newReg)
    if (!regionObj) {
      state.district = ''
      return
    }
    const validDistricts = districts.value
      .filter(d => d.region_id === regionObj.id)
      .map(d => d.name_uz)
    
    // Only clear if the current district is set but not valid for the new region
    if (state.district && !validDistricts.includes(state.district)) {
      state.district = ''
    }
  }
)

async function fetchSchools() {
  loading.value = true
  try {
    const res = await listSchools(searchQ.value.trim() || undefined)
    schools.value = res.items
  } catch (error: any) {
    toast.add({
      title: 'Xatolik',
      description: error?.data?.detail || 'Maktablar ro‘yxatini yuklab bo‘lmadi',
      color: 'error',
      icon: 'i-lucide-alert-circle',
    })
  } finally {
    loading.value = false
  }
}

async function fetchReferences() {
  try {
    const [regionsRes, districtsRes] = await Promise.all([
      listLocationRegions(),
      listLocationDistricts(),
    ])
    regions.value = regionsRes
    districts.value = districtsRes
  } catch (error) {
    console.error('Hududlar ro‘yxatini yuklashda xatolik:', error)
  }
}

// Debounce search
watch(searchQ, () => {
  fetchSchools()
})

onMounted(() => {
  fetchSchools()
  fetchReferences()
})

const breadcrumbItems = [
  { label: 'Arxivist', icon: 'i-lucide-archive', to: '/archive' },
  { label: 'Musiqa maktablari', icon: 'i-lucide-school' },
]

function openCreate() {
  editing.value = null
  state.name = ''
  state.code = ''
  state.region = undefined
  state.district = ''
  modalOpen.value = true
}

function openEdit(school: MusicSchoolResponse) {
  editing.value = school
  state.name = school.name
  state.code = school.code || ''
  state.region = school.region || undefined
  state.district = school.district || ''
  modalOpen.value = true
}

async function handleSave() {
  if (!state.name.trim()) return
  saving.value = true
  try {
    const payload = {
      name: state.name.trim(),
      code: state.code.trim() || null,
      region: state.region || null,
      district: state.district.trim() || null,
    }
    if (editing.value) {
      await updateSchool(editing.value.id, payload)
      toast.add({
        title: 'Muvaffaqiyat',
        description: 'Musiqa maktabi ma’lumotlari yangilandi',
        color: 'success',
        icon: 'i-lucide-check-circle',
      })
    } else {
      await createSchool(payload)
      toast.add({
        title: 'Muvaffaqiyat',
        description: 'Musiqa maktabi muvaffaqiyatli qo‘shildi',
        color: 'success',
        icon: 'i-lucide-check-circle',
      })
    }
    modalOpen.value = false
    fetchSchools()
  } catch (error: any) {
    toast.add({
      title: 'Xatolik',
      description: error?.data?.detail || 'Saqlashda xatolik yuz berdi',
      color: 'error',
      icon: 'i-lucide-alert-circle',
    })
  } finally {
    saving.value = false
  }
}

// Delete confirmation
const deleteOpen = ref(false)
const deleteTarget = ref<MusicSchoolResponse | null>(null)

function openDelete(school: MusicSchoolResponse) {
  deleteTarget.value = school
  deleteOpen.value = true
}

async function handleDelete() {
  if (!deleteTarget.value) return
  try {
    await deleteSchool(deleteTarget.value.id)
    toast.add({
      title: 'Muvaffaqiyat',
      description: 'Musiqa maktabi tizimdan o‘chirildi',
      color: 'success',
      icon: 'i-lucide-check-circle',
    })
    deleteOpen.value = false
    fetchSchools()
  } catch (error: any) {
    toast.add({
      title: 'Xatolik',
      description: error?.data?.detail || 'Maktabni o‘chirib bo‘lmadi. Hujjatlar bog‘langan bo‘lishi mumkin.',
      color: 'error',
      icon: 'i-lucide-alert-circle',
    })
  }
}
</script>

<template>
  <PagePanel title="Musiqa maktablari" icon="i-lucide-school">
    <template #headerRight>
      <UBadge :label="`${schools.length} maktab`" variant="subtle" class="mr-2" />
      <UButton icon="i-lucide-plus" label="Maktab qo‘shish" @click="openCreate" />
    </template>

    <div class="p-5">
      <UBreadcrumb :items="breadcrumbItems" class="mb-5" />

      <!-- Search bar -->
      <div class="mb-5 max-w-md">
        <UInput
          v-model="searchQ"
          placeholder="Nomi yoki kodi bo‘yicha qidirish..."
          icon="i-lucide-search"
          size="md"
          class="w-full"
        />
      </div>

      <div
        v-if="schools.length"
        class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
      >
        <div
          v-for="school in schools"
          :key="school.id"
          class="group relative flex flex-col rounded-xl border border-default bg-elevated/30 p-4 transition-colors hover:border-primary/45"
        >
          <div class="flex items-start gap-2">
            <UIcon name="i-lucide-school" class="mt-0.5 shrink-0 text-primary" />
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-2 flex-wrap pb-1">
                <h3 class="font-semibold leading-snug text-highlighted truncate">{{ school.name }}</h3>
                <UBadge v-if="school.code" :label="school.code" variant="subtle" size="xs" />
              </div>
              <p class="text-xs text-muted">
                Kodi: {{ school.code || 'Mavjud emas' }}
              </p>
              <!-- Region & District Location Badges -->
              <div v-if="school.region || school.district" class="mt-2.5 flex gap-1.5 flex-wrap">
                <UBadge v-if="school.region" :label="school.region" variant="soft" color="primary" size="xs" icon="i-lucide-map-pin" />
                <UBadge v-if="school.district" :label="school.district" variant="subtle" color="neutral" size="xs" />
              </div>
            </div>
          </div>

          <div class="mt-4 flex items-center justify-end gap-1 border-t border-default/50 pt-2">
            <UTooltip text="Tahrirlash">
              <UButton icon="i-lucide-pencil" variant="ghost" size="xs" @click="openEdit(school)" />
            </UTooltip>
            <UTooltip text="O‘chirish">
              <UButton icon="i-lucide-trash-2" variant="ghost" size="xs" color="error" @click="openDelete(school)" />
            </UTooltip>
          </div>
        </div>
      </div>

      <div v-else-if="!loading" class="flex items-center justify-center p-12">
        <EmptyState
          icon="i-lucide-school"
          title="Musiqa maktablari topilmadi"
          description="Tizimda birorta ham musiqa maktabi mavjud emas yoki qidiruvga mos kelmadi."
        />
      </div>
    </div>
  </PagePanel>

  <!-- Create / edit modal -->
  <UModal v-model:open="modalOpen" :title="editing ? 'Maktabni tahrirlash' : 'Yangi maktab qo‘shish'">
    <template #body>
      <div class="space-y-5">
        <UFormField label="Musiqa maktabi nomi" required>
          <UInput
            v-model="state.name"
            placeholder="Masalan: 1-sonli bolalar musiqa va san’at maktabi"
            icon="i-lucide-school"
            size="lg"
            class="w-full"
            @keydown.enter="handleSave"
          />
        </UFormField>
        
        <UFormField label="Maktab kodi (Identifikator)" help="Ixtiyoriy yagona kod">
          <UInput
            v-model="state.code"
            placeholder="Masalan: MS-01"
            icon="i-lucide-hash"
            size="lg"
            class="w-full"
          />
        </UFormField>

        <!-- Location Fields -->
        <div class="grid grid-cols-2 gap-4">
          <UFormField label="Viloyat / Hudud">
            <USelectMenu
              v-model="state.region"
              :items="regionOptions"
              value-key="value"
              placeholder="Viloyatni tanlang"
              class="w-full"
              size="lg"
            />
          </UFormField>
          <UFormField label="Tuman / Shahar">
            <USelectMenu
              v-model="state.district"
              :items="districtOptions"
              value-key="value"
              placeholder="Tumanni tanlang"
              class="w-full"
              size="lg"
              :disabled="!state.region"
            />
          </UFormField>
        </div>
      </div>
    </template>
    
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton variant="ghost" label="Bekor qilish" @click="modalOpen = false" />
        <UButton
          :label="editing ? 'Saqlash' : 'Qo‘shish'"
          icon="i-lucide-save"
          :loading="saving"
          :disabled="!state.name.trim()"
          @click="handleSave"
        />
      </div>
    </template>
  </UModal>

  <!-- Delete confirmation -->
  <UModal
    v-model:open="deleteOpen"
    title="Maktabni o‘chirish"
    :description="deleteTarget ? `«${deleteTarget.name}» musiqa maktabini o‘chirishni tasdiqlaysizmi? Bu amalni ortga qaytarib bo‘lmaydi.` : ''"
  >
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton variant="ghost" label="Bekor qilish" @click="deleteOpen = false" />
        <UButton color="error" label="O‘chirish" icon="i-lucide-trash-2" @click="handleDelete" />
      </div>
    </template>
  </UModal>
</template>
