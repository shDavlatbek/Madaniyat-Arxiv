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

const fieldTypes = [
  { label: 'Tekst', value: 'text' },
  { label: 'Raqam', value: 'number' },
  { label: 'Sana', value: 'date' },
  { label: 'Katta tekst', value: 'textarea' },
  { label: 'Tanlov', value: 'select' },
  { label: 'Fayl', value: 'file' },
]

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

  <!-- Add/Edit modal -->
  <UModal v-model:open="modalOpen" :title="editingField ? 'Shablon maydonni tahrirlash' : 'Yangi shablon maydon qo\'shish'">
    <template #body>
      <div class="space-y-5">
        <UFormField label="Nomi" required>
          <UInput v-model="state.label" placeholder="masalan: Ro'yxat raqami" size="lg" class="w-full" />
        </UFormField>
        <div class="grid grid-cols-3 gap-4 items-end">
          <UFormField label="Maydon turi">
            <USelect v-model="state.field_type" :items="fieldTypes" size="lg" class="w-full" />
          </UFormField>
          <UFormField label="Majburiy">
            <USwitch v-model="state.is_required" />
          </UFormField>
          <UFormField label="Tartib raqami">
            <UInput v-model="state.sort_order" type="number" size="lg" class="w-full" />
          </UFormField>
        </div>
        <UFormField v-if="state.field_type === 'select'" label="Tanlov variantlari" help="Vergul bilan ajrating">
          <UInput v-model="state.options" placeholder="variant1, variant2, variant3" size="lg" class="w-full" />
        </UFormField>
      </div>
    </template>
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton variant="ghost" label="Bekor qilish" @click="modalOpen = false" />
        <UButton :label="editingField ? 'Saqlash' : 'Qo\'shish'" icon="i-lucide-save" :disabled="!state.label" @click="handleSave" />
      </div>
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
