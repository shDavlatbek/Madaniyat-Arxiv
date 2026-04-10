<script setup lang="ts">
import type { DefaultFieldResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const { apiFetch } = useApi()
const toast = useToast()

// Fields
const { data: fields, refresh } = await useAsyncData('default-fields', () =>
  apiFetch<{ items: DefaultFieldResponse[] }>('/api/default-fields').then(res => res.items)
)

const columns = [
  { accessorKey: 'label', header: 'Label' },
  { accessorKey: 'field_type', header: 'Tur' },
  { accessorKey: 'is_required', header: 'Majburiy' },
  { accessorKey: 'sort_order', header: 'Tartib' },
  { id: 'actions', header: '' },
]

// Add/Edit modal
const modalOpen = ref(false)
const editingField = ref<DefaultFieldResponse | null>(null)
const fieldModalData = ref<{ label: string; field_type: string; is_required: boolean; options: string } | undefined>()

function openCreate() {
  editingField.value = null
  fieldModalData.value = undefined
  modalOpen.value = true
}

function openEdit(field: DefaultFieldResponse) {
  editingField.value = field
  fieldModalData.value = {
    label: field.label,
    field_type: field.field_type,
    is_required: field.is_required,
    options: field.options?.join(', ') || '',
  }
  modalOpen.value = true
}

async function onFieldSave(data: { label: string; field_type: string; is_required: boolean; options: string }) {
  const body: Record<string, any> = {
    label: data.label,
    field_type: data.field_type,
    is_required: data.is_required,
    sort_order: 0,
    placeholder: null,
    options: data.field_type === 'select' && data.options
      ? data.options.split(',').map(s => s.trim()).filter(Boolean)
      : null,
  }
  try {
    if (editingField.value) {
      await apiFetch(`/api/default-fields/${editingField.value.id}`, { method: 'PUT', body })
      toast.add({ title: 'Muvaffaqiyat', description: 'Shablon maydon yangilandi', color: 'success', icon: 'i-lucide-check-circle' })
    } else {
      await apiFetch('/api/default-fields', { method: 'POST', body })
      toast.add({ title: 'Muvaffaqiyat', description: 'Shablon maydon qo\'shildi', color: 'success', icon: 'i-lucide-check-circle' })
    }
    refresh()
  } catch (error: any) {
    toast.add({ title: 'Xatolik', description: error?.data?.detail || 'Xatolik yuz berdi', color: 'error', icon: 'i-lucide-alert-circle' })
  }
}

const deleteOpen = ref(false)
const deleteTarget = ref<DefaultFieldResponse | null>(null)

async function handleDelete() {
  if (!deleteTarget.value) return
  try {
    await apiFetch(`/api/default-fields/${deleteTarget.value.id}`, { method: 'DELETE' })
    toast.add({ title: 'Muvaffaqiyat', description: 'Shablon maydon o\'chirildi', color: 'success', icon: 'i-lucide-check-circle' })
    deleteOpen.value = false
    refresh()
  } catch {
    toast.add({ title: 'Xatolik', description: 'O\'chirib bo\'lmadi', color: 'error', icon: 'i-lucide-alert-circle' })
  }
}
</script>

<template>
  <PagePanel title="Shablon maydonlar" icon="i-lucide-copy">
    <template #headerRight>
      <UButton icon="i-lucide-plus" label="Yangi shablon" @click="openCreate" />
    </template>
    <UTable :data="fields || []" :columns="columns">
      <template #label-cell="{ row }">
        <span class="font-semibold text-highlighted">{{ row.original.label }}</span>
      </template>
      <template #is_required-cell="{ row }">
        <UBadge :label="row.original.is_required ? 'Ha' : 'Yo\'q'" :color="row.original.is_required ? 'warning' : 'neutral'" variant="subtle" />
      </template>
      <template #field_type-cell="{ row }">
        <UBadge :label="{ text: 'Tekst', number: 'Raqam', date: 'Sana', textarea: 'Katta tekst', select: 'Tanlov', file: 'Fayl' }[row.original.field_type] || row.original.field_type" variant="subtle" />
      </template>
      <template #actions-cell="{ row }">
        <div class="flex gap-1 justify-end">
          <UButton icon="i-lucide-pencil" variant="ghost" size="xs" @click="openEdit(row.original)" />
          <UButton icon="i-lucide-trash-2" variant="ghost" size="xs" color="error" @click="deleteTarget = row.original; deleteOpen = true" />
        </div>
      </template>
    </UTable>

    <div v-if="!fields?.length" class="flex items-center justify-center p-12">
      <EmptyState icon="i-lucide-copy" title="Shablon maydonlar yo'q" description="Hali shablon maydonlar qo'shilmagan" />
    </div>
  </PagePanel>

  <FieldModal v-model:open="modalOpen" :editing="!!editingField" :initial-data="fieldModalData" @save="onFieldSave" />

  <!-- Delete modal -->
  <UModal v-model:open="deleteOpen" title="Shablon maydonni o'chirish" description="Bu shablon maydon o'chiriladi.">
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton variant="ghost" label="Bekor qilish" @click="deleteOpen = false" />
        <UButton color="error" label="O'chirish" icon="i-lucide-trash-2" @click="handleDelete" />
      </div>
    </template>
  </UModal>
</template>
