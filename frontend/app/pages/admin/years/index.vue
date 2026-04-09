<script setup lang="ts">
import { z } from 'zod'
import type { YearResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const { apiFetch } = useApi()
const toast = useToast()

const { data: yearsData, status, refresh } = await useAsyncData('admin-years', () =>
  apiFetch<{ items: YearResponse[] }>('/api/years?active_only=false')
)

const years = computed(() => yearsData.value?.items || [])

const columns = [
  { accessorKey: 'value', header: 'Yil' },
  { accessorKey: 'is_active', header: 'Holat' },
  { id: 'actions', header: '' },
]

// Create/Edit modal
const modalOpen = ref(false)
const editingYear = ref<YearResponse | null>(null)
const schema = z.object({ value: z.coerce.number().min(1900).max(2100), is_active: z.boolean() })
const state = reactive({ value: new Date().getFullYear(), is_active: true })
const importFromYearId = ref<number | undefined>(undefined)

const yearItems = computed(() => years.value.map(y => ({ label: `${y.value} yildan`, value: y.id })))

function openCreate() {
  editingYear.value = null
  state.value = new Date().getFullYear()
  state.is_active = true
  importFromYearId.value = undefined
  modalOpen.value = true
}

function openEdit(year: YearResponse) {
  editingYear.value = year
  state.value = year.value
  state.is_active = year.is_active
  modalOpen.value = true
}

async function handleSave() {
  try {
    if (editingYear.value) {
      await apiFetch(`/api/years/${editingYear.value.id}`, { method: 'PUT', body: state })
      toast.add({ title: 'Muvaffaqiyat', description: 'Yil yangilandi', color: 'success', icon: 'i-lucide-check-circle' })
    } else {
      await apiFetch('/api/years', {
        method: 'POST',
        body: { ...state, import_from_year_id: importFromYearId.value || null },
      })
      toast.add({ title: 'Muvaffaqiyat', description: 'Yil yaratildi', color: 'success', icon: 'i-lucide-check-circle' })
    }
    modalOpen.value = false
    refresh()
  } catch (error: any) {
    toast.add({ title: 'Xatolik', description: error?.data?.detail || 'Xatolik yuz berdi', color: 'error', icon: 'i-lucide-alert-circle' })
  }
}

const deleteOpen = ref(false)
const deleteTarget = ref<YearResponse | null>(null)

async function handleDelete() {
  if (!deleteTarget.value) return
  try {
    await apiFetch(`/api/years/${deleteTarget.value.id}`, { method: 'DELETE' })
    toast.add({ title: 'Muvaffaqiyat', description: 'Yil o\'chirildi', color: 'success', icon: 'i-lucide-check-circle' })
    deleteOpen.value = false
    refresh()
  } catch {
    toast.add({ title: 'Xatolik', description: 'O\'chirib bo\'lmadi', color: 'error', icon: 'i-lucide-alert-circle' })
  }
}
</script>

<template>
  <PagePanel title="Yillar" icon="i-lucide-calendar">
    <template #headerRight>
      <UBadge :label="`${years.length} yil`" variant="subtle" class="mr-2" />
      <UButton icon="i-lucide-plus" label="Yangi yil" @click="openCreate" />
    </template>
    <UTable :data="years" :columns="columns" :loading="status === 'pending'" @select="(row: any) => openEdit(row.original)">
      <template #value-cell="{ row }">
        <span class="font-semibold text-highlighted text-base">{{ row.original.value }}</span>
      </template>
      <template #is_active-cell="{ row }">
        <UBadge :label="row.original.is_active ? 'Faol' : 'Nofaol'" :color="row.original.is_active ? 'success' : 'error'" variant="subtle" />
      </template>
      <template #actions-cell="{ row }">
        <div class="flex gap-1 justify-end">
          <UButton icon="i-lucide-pencil" variant="ghost" size="xs" @click.stop="openEdit(row.original)" />
          <UButton icon="i-lucide-trash-2" variant="ghost" size="xs" color="error" @click.stop="deleteTarget = row.original; deleteOpen = true" />
        </div>
      </template>
    </UTable>

    <div v-if="!years.length && status !== 'pending'" class="flex items-center justify-center p-12">
      <EmptyState icon="i-lucide-calendar-x" title="Yillar topilmadi" description="Hozircha yillar qo'shilmagan" />
    </div>
  </PagePanel>

  <!-- Create/Edit modal -->
  <UModal v-model:open="modalOpen" :title="editingYear ? 'Yilni tahrirlash' : 'Yangi yil'">
    <template #body>
      <UForm :schema="schema" :state="state" class="space-y-5" @submit="handleSave">
        <UFormField label="Yil" name="value" required>
          <UInput v-model="state.value" type="number" icon="i-lucide-calendar" size="lg" />
        </UFormField>
        <UFormField label="Holat" name="is_active">
          <div class="flex items-center gap-2">
            <USwitch v-model="state.is_active" />
            <span class="text-sm text-muted">{{ state.is_active ? 'Faol' : 'Nofaol' }}</span>
          </div>
        </UFormField>
        <!-- Import categories from another year (only on create) -->
        <UFormField v-if="!editingYear && years.length" label="Nomenklaturalarni import qilish" help="Mavjud yildan nomenklaturalarni nusxalash">
          <USelect
            v-model="importFromYearId"
            :items="yearItems"
            placeholder="Import qilmaslik"
            icon="i-lucide-copy"
            size="lg"
          />
        </UFormField>
        <div class="flex justify-end gap-3 pt-2">
          <UButton variant="outline" label="Bekor qilish" @click="modalOpen = false" />
          <UButton type="submit" :label="editingYear ? 'Saqlash' : 'Yaratish'" icon="i-lucide-save" />
        </div>
      </UForm>
    </template>
  </UModal>

  <!-- Delete modal -->
  <UModal v-model:open="deleteOpen" title="Yilni o'chirish" description="Bu amalni qaytarib bo'lmaydi.">
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton variant="ghost" label="Bekor qilish" @click="deleteOpen = false" />
        <UButton color="error" label="O'chirish" icon="i-lucide-trash-2" @click="handleDelete" />
      </div>
    </template>
  </UModal>
</template>
