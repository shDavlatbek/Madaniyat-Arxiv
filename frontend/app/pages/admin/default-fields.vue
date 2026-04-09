<script setup lang="ts">
import { z } from 'zod'
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

const fieldTypes = ['text', 'number', 'date', 'textarea', 'select', 'file']

const schema = z.object({
  label: z.string().min(1),
  field_type: z.string(),
  is_required: z.boolean(),
  sort_order: z.coerce.number(),
  placeholder: z.string().optional(),
})

const state = reactive({
  label: '',
  field_type: 'text',
  is_required: false,
  sort_order: 0,
  placeholder: '',
  options: '' as string,
})

function openCreate() {
  editingField.value = null
  Object.assign(state, { label: '', field_type: 'text', is_required: false, sort_order: 0, placeholder: '', options: '' })
  modalOpen.value = true
}

function openEdit(field: DefaultFieldResponse) {
  editingField.value = field
  Object.assign(state, {
    label: field.label,
    field_type: field.field_type,
    is_required: field.is_required,
    sort_order: field.sort_order,
    placeholder: field.placeholder || '',
    options: field.options?.join(', ') || '',
  })
  modalOpen.value = true
}

async function handleSave() {
  const body: Record<string, any> = {
    ...state,
    options: state.field_type === 'select' && state.options
      ? state.options.split(',').map(s => s.trim()).filter(Boolean)
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
    modalOpen.value = false
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
        <UBadge :label="row.original.field_type" variant="subtle" />
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

  <!-- Add/Edit modal -->
  <UModal v-model:open="modalOpen" :title="editingField ? 'Shablon maydonni tahrirlash' : 'Yangi shablon maydon'">
    <template #body>
      <UForm :schema="schema" :state="state" class="space-y-4" @submit="handleSave">
        <UFormField label="Label" name="label" required>
          <UInput v-model="state.label" placeholder="Ro'yxat raqami" />
        </UFormField>
        <UFormField label="Tur" name="field_type">
          <USelect v-model="state.field_type" :items="fieldTypes" />
        </UFormField>
        <UFormField v-if="state.field_type === 'select'" label="Variantlar (vergul bilan)" name="options">
          <UInput v-model="state.options" placeholder="variant1, variant2, variant3" />
        </UFormField>
        <UFormField label="Placeholder" name="placeholder">
          <UInput v-model="state.placeholder" />
        </UFormField>
        <div class="flex gap-4">
          <UFormField label="Majburiy" name="is_required">
            <USwitch v-model="state.is_required" />
          </UFormField>
          <UFormField label="Tartib raqami" name="sort_order">
            <UInput v-model="state.sort_order" type="number" class="w-24" />
          </UFormField>
        </div>
        <div class="flex justify-end gap-2">
          <UButton variant="ghost" label="Bekor qilish" @click="modalOpen = false" />
          <UButton type="submit" :label="editingField ? 'Saqlash' : 'Qo\'shish'" icon="i-lucide-save" />
        </div>
      </UForm>
    </template>
  </UModal>

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
