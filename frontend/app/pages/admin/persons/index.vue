<script setup lang="ts">
import { z } from 'zod'
import type { PersonResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const { apiFetch } = useApi()
const { createPerson, updatePerson, deletePerson } = usePersons()
const toast = useToast()

const { data: personsData, status, refresh } = await useAsyncData('admin-persons', () =>
  apiFetch<{ items: PersonResponse[] }>('/api/persons')
)
const persons = computed(() => personsData.value?.items || [])

const columns = [
  { accessorKey: 'full_name', header: 'F.I.O.' },
  { id: 'current_position', header: 'Lavozimi' },
  { id: 'tenures_count', header: 'Davrlar' },
  { id: 'actions', header: '' },
]

// Modal state
const modalOpen = ref(false)
const editingPerson = ref<PersonResponse | null>(null)

const schema = z.object({
  full_name: z.string().min(1, 'F.I.O. kiritilishi shart'),
})

const state = reactive({
  full_name: '',
  tenures: [] as Array<{ position: string; start_date: string; end_date: string }>,
})

function openCreate() {
  editingPerson.value = null
  state.full_name = ''
  state.tenures = [{ position: '', start_date: '', end_date: '' }]
  modalOpen.value = true
}

function openEdit(person: PersonResponse) {
  editingPerson.value = person
  state.full_name = person.full_name
  state.tenures = person.tenures.map(t => ({
    position: t.position,
    start_date: t.start_date,
    end_date: t.end_date || '',
  }))
  if (!state.tenures.length) {
    state.tenures = [{ position: '', start_date: '', end_date: '' }]
  }
  modalOpen.value = true
}

function addTenure() {
  state.tenures.push({ position: '', start_date: '', end_date: '' })
}

function removeTenure(index: number) {
  state.tenures.splice(index, 1)
}

function getCurrentPosition(person: PersonResponse) {
  const today = new Date().toISOString().split('T')[0]
  const active = person.tenures.find(t =>
    t.start_date <= today && (!t.end_date || t.end_date >= today)
  )
  if (!active) return '-'
  const period = `${formatDate(active.start_date)} — ${active.end_date ? formatDate(active.end_date) : 'hozirgacha'}`
  return `${active.position} (${period})`
}

async function handleSave() {
  const validTenures = state.tenures
    .filter(t => t.position && t.start_date)
    .map(t => ({
      position: t.position,
      start_date: t.start_date,
      end_date: t.end_date || null,
    }))

  try {
    if (editingPerson.value) {
      await updatePerson(editingPerson.value.id, {
        full_name: state.full_name,
        tenures: validTenures,
      })
      toast.add({ title: 'Muvaffaqiyat', description: 'Shaxs yangilandi', color: 'success', icon: 'i-lucide-check-circle' })
    } else {
      await createPerson({
        full_name: state.full_name,
        tenures: validTenures,
      })
      toast.add({ title: 'Muvaffaqiyat', description: 'Shaxs qo\'shildi', color: 'success', icon: 'i-lucide-check-circle' })
    }
    modalOpen.value = false
    refresh()
  } catch (error: any) {
    toast.add({ title: 'Xatolik', description: error?.data?.detail || 'Xatolik yuz berdi', color: 'error', icon: 'i-lucide-alert-circle' })
  }
}

const deleteOpen = ref(false)
const deleteTarget = ref<PersonResponse | null>(null)

async function handleDelete() {
  if (!deleteTarget.value) return
  try {
    await deletePerson(deleteTarget.value.id)
    toast.add({ title: 'Muvaffaqiyat', description: 'Shaxs o\'chirildi', color: 'success', icon: 'i-lucide-check-circle' })
    deleteOpen.value = false
    refresh()
  } catch {
    toast.add({ title: 'Xatolik', description: 'O\'chirib bo\'lmadi', color: 'error', icon: 'i-lucide-alert-circle' })
  }
}

function formatDate(date: string) {
  if (!date) return ''
  const parts = date.split('-')
  if (parts.length !== 3) return date
  return `${parts[2]}.${parts[1]}.${parts[0]}`
}
</script>

<template>
  <PagePanel title="Shaxslar" icon="i-lucide-user-check">
    <template #headerRight>
      <UBadge :label="`${persons.length} shaxs`" variant="subtle" class="mr-2" />
      <UButton icon="i-lucide-plus" label="Yangi shaxs" @click="openCreate" />
    </template>

    <UTable :data="persons" :columns="columns" :loading="status === 'pending'">
      <template #full_name-cell="{ row }">
        <div class="flex items-center gap-2">
          <UIcon name="i-lucide-user" class="text-primary shrink-0" />
          <span class="font-semibold text-highlighted">{{ row.original.full_name }}</span>
        </div>
      </template>
      <template #current_position-cell="{ row }">
        <span class="text-sm">{{ getCurrentPosition(row.original) }}</span>
      </template>
      <template #tenures_count-cell="{ row }">
        <UBadge :label="`${row.original.tenures.length} davr`" variant="subtle" />
      </template>
      <template #actions-cell="{ row }">
        <div class="flex gap-1 justify-end">
          <UButton icon="i-lucide-pencil" variant="ghost" size="xs" @click="openEdit(row.original)" />
          <UButton icon="i-lucide-trash-2" variant="ghost" size="xs" color="error" @click="deleteTarget = row.original; deleteOpen = true" />
        </div>
      </template>
    </UTable>

    <div v-if="!persons.length && status !== 'pending'" class="flex items-center justify-center p-12">
      <EmptyState icon="i-lucide-user-x" title="Shaxslar topilmadi" description="Hali shaxslar qo'shilmagan" />
    </div>
  </PagePanel>

  <!-- Add/Edit modal -->
  <UModal v-model:open="modalOpen" :title="editingPerson ? 'Shaxsni tahrirlash' : 'Yangi shaxs'">
    <template #body>
      <div class="space-y-5">
        <UFormField label="F.I.O." required>
          <UInput v-model="state.full_name" placeholder="To'liq ism" icon="i-lucide-user" size="lg" class="w-full" />
        </UFormField>

        <div>
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-sm font-semibold text-highlighted">Lavozim davrlari</h3>
            <UButton icon="i-lucide-plus" size="xs" variant="ghost" label="Davr qo'shish" @click="addTenure" />
          </div>

          <div v-for="(tenure, i) in state.tenures" :key="i" class="flex items-start gap-2 mb-3 p-3 rounded-lg border border-default bg-elevated/30">
            <div class="flex-1 space-y-2">
              <UInput v-model="tenure.position" placeholder="Lavozim" size="sm" class="w-full" />
              <div class="flex gap-2">
                <DatePicker v-model="tenure.start_date" placeholder="Boshlanish" size="sm" />
                <DatePicker v-model="tenure.end_date" placeholder="Tugash (ixtiyoriy)" size="sm" />
              </div>
            </div>
            <UButton
              v-if="state.tenures.length > 1"
              icon="i-lucide-x"
              variant="ghost"
              size="xs"
              color="error"
              @click="removeTenure(i)"
            />
          </div>
        </div>
      </div>
    </template>
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton variant="ghost" label="Bekor qilish" @click="modalOpen = false" />
        <UButton :label="editingPerson ? 'Saqlash' : 'Qo\'shish'" icon="i-lucide-save" :disabled="!state.full_name" @click="handleSave" />
      </div>
    </template>
  </UModal>

  <!-- Delete modal -->
  <UModal v-model:open="deleteOpen" title="Shaxsni o'chirish" description="Bu shaxs o'chiriladi. Bog'liq hujjatlarda imzo ma'lumoti yo'qolishi mumkin.">
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton variant="ghost" label="Bekor qilish" @click="deleteOpen = false" />
        <UButton color="error" label="O'chirish" icon="i-lucide-trash-2" @click="handleDelete" />
      </div>
    </template>
  </UModal>
</template>
