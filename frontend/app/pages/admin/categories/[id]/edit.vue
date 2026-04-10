<script setup lang="ts">
import { z } from 'zod'
import type { CategoryFieldResponse, CategoryResponse, YearResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const route = useRoute()
const catId = computed(() => route.params.id as string)
const { apiFetch } = useApi()
const toast = useToast()
const loading = ref(false)

const { data: category } = await useAsyncData(`cat-edit-${catId.value}`, () =>
  apiFetch<{ items: CategoryResponse[] }>('/api/categories').then(
    res => res.items.find(c => c.id === catId.value) || null,
  ),
)

const { data: yearsData } = await useAsyncData('years-for-cat', () =>
  apiFetch<{ items: YearResponse[] }>('/api/years?active_only=false'),
)
const years = computed(() => yearsData.value?.items || [])
const yearItems = computed(() => years.value.map(y => ({ label: String(y.value), value: y.id })))

const schema = z.object({
  name: z.string().min(1, 'Nom kiritilishi shart'),
  description: z.string().optional(),
  sort_order: z.coerce.number(),
  year_id: z.number({ required_error: 'Yil tanlanishi shart' }),
})

const state = reactive({
  name: category.value?.name || '',
  description: category.value?.description || '',
  sort_order: category.value?.sort_order || 0,
  year_id: category.value?.year_id || undefined as number | undefined,
})

const initialState = JSON.stringify(state)
const isDirty = computed(() => JSON.stringify(state) !== initialState)

async function handleSubmit() {
  loading.value = true
  try {
    await apiFetch(`/api/categories/${catId.value}`, { method: 'PUT', body: state })
    toast.add({ title: 'Muvaffaqiyat', description: 'Nomenklatura yangilandi', color: 'success', icon: 'i-lucide-check-circle' })
    navigateTo('/admin/categories')
  } catch (error: any) {
    toast.add({ title: 'Xatolik', description: error?.data?.detail || 'Yangilab bo\'lmadi', color: 'error', icon: 'i-lucide-alert-circle' })
  } finally {
    loading.value = false
  }
}

// === Fields management ===
const { data: fields, refresh: refreshFields } = await useAsyncData(`cat-fields-${catId.value}`, () =>
  apiFetch<CategoryFieldResponse[]>(`/api/categories/${catId.value}/fields`)
)

const fieldTypes = [
  { label: 'Tekst', value: 'text' },
  { label: 'Raqam', value: 'number' },
  { label: 'Sana', value: 'date' },
  { label: 'Katta tekst', value: 'textarea' },
  { label: 'Tanlov', value: 'select' },
  { label: 'Fayl', value: 'file' },
]
const fieldModalOpen = ref(false)
const editingField = ref<CategoryFieldResponse | null>(null)

const fieldState = reactive({
  label: '',
  field_type: 'text',
  is_required: false,
  sort_order: 0,
  placeholder: '',
  options: '' as string,
})

function openFieldCreate() {
  editingField.value = null
  Object.assign(fieldState, { label: '', field_type: 'text', is_required: false, sort_order: 0, placeholder: '', options: '' })
  fieldModalOpen.value = true
}

function openFieldEdit(field: CategoryFieldResponse) {
  editingField.value = field
  Object.assign(fieldState, {
    label: field.label,
    field_type: field.field_type,
    is_required: field.is_required,
    sort_order: field.sort_order,
    placeholder: field.placeholder || '',
    options: field.options?.join(', ') || '',
  })
  fieldModalOpen.value = true
}

async function handleFieldSave() {
  const body: Record<string, any> = {
    ...fieldState,
    options: fieldState.field_type === 'select' && fieldState.options
      ? fieldState.options.split(',').map(s => s.trim()).filter(Boolean)
      : null,
  }
  try {
    if (editingField.value) {
      await apiFetch(`/api/categories/${catId.value}/fields/${editingField.value.id}`, { method: 'PUT', body })
      toast.add({ title: 'Muvaffaqiyat', description: 'Maydon yangilandi', color: 'success', icon: 'i-lucide-check-circle' })
    } else {
      await apiFetch(`/api/categories/${catId.value}/fields`, { method: 'POST', body })
      toast.add({ title: 'Muvaffaqiyat', description: 'Maydon qo\'shildi', color: 'success', icon: 'i-lucide-check-circle' })
    }
    fieldModalOpen.value = false
    refreshFields()
  } catch (error: any) {
    toast.add({ title: 'Xatolik', description: error?.data?.detail || 'Xatolik yuz berdi', color: 'error', icon: 'i-lucide-alert-circle' })
  }
}

const fieldDeleteOpen = ref(false)
const fieldDeleteTarget = ref<CategoryFieldResponse | null>(null)

async function handleFieldDelete() {
  if (!fieldDeleteTarget.value) return
  try {
    await apiFetch(`/api/categories/${catId.value}/fields/${fieldDeleteTarget.value.id}`, { method: 'DELETE' })
    toast.add({ title: 'Muvaffaqiyat', description: 'Maydon o\'chirildi', color: 'success', icon: 'i-lucide-check-circle' })
    fieldDeleteOpen.value = false
    refreshFields()
  } catch {
    toast.add({ title: 'Xatolik', description: 'O\'chirib bo\'lmadi', color: 'error', icon: 'i-lucide-alert-circle' })
  }
}
</script>

<template>
  <PagePanel :title="`Tahrirlash: ${category?.name || ''}`" icon="i-lucide-folder-pen">
    <template #headerLeft>
      <UButton icon="i-lucide-arrow-left" variant="ghost" color="neutral" to="/admin/categories" />
    </template>
    <template #headerRight>
      <UBadge v-if="isDirty" label="O'zgartirildi" variant="subtle" color="warning" icon="i-lucide-circle-dot" size="sm" />
    </template>

    <div class="p-6">
      <UForm :schema="schema" :state="state" @submit="handleSubmit">
        <div class="flex flex-col lg:flex-row gap-6">
          <!-- Left: Category form -->
          <div class="flex-1 min-w-0 space-y-6">
            <UCard :ui="{ header: 'border-b border-default', body: 'space-y-5' }">
              <template #header>
                <div class="flex items-center gap-2">
                  <UIcon name="i-lucide-info" class="w-4 h-4 text-muted" />
                  <h2 class="text-sm font-semibold text-highlighted">Asosiy ma'lumotlar</h2>
                </div>
              </template>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                <UFormField label="Nomi" name="name" required help="Foydalanuvchilarga ko'rinadigan nom">
                  <UInput v-model="state.name" icon="i-lucide-folder" placeholder="Buyruqlar" size="lg" class="w-full" />
                </UFormField>
                <UFormField label="Yil" name="year_id" required>
                  <USelect v-model="state.year_id" :items="yearItems" placeholder="Yilni tanlang" icon="i-lucide-calendar" size="lg" class="w-full" />
                </UFormField>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                <UFormField label="Tavsif" name="description" help="Ixtiyoriy">
                  <UTextarea v-model="state.description" :rows="3" placeholder="Nomenklatura haqida..." class="w-full" />
                </UFormField>
                <UFormField label="Tartib raqami" name="sort_order" help="Kichik raqam birinchi chiqadi">
                  <UInput v-model="state.sort_order" type="number" icon="i-lucide-arrow-up-down" size="lg" class="w-40" />
                </UFormField>
              </div>
            </UCard>

            <!-- Action bar -->
            <div class="flex items-center justify-end gap-3">
              <UButton variant="ghost" color="neutral" label="Bekor qilish" to="/admin/categories" :disabled="loading" />
              <UButton type="submit" label="Saqlash" icon="i-lucide-save" :loading="loading" :disabled="!isDirty" />
            </div>
          </div>

          <!-- Right: Fields management -->
          <div class="w-full lg:w-96 xl:w-md shrink-0">
            <UCard :ui="{ header: 'border-b border-default' }">
              <template #header>
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-2">
                    <UIcon name="i-lucide-layers" class="w-4 h-4 text-muted" />
                    <h2 class="text-sm font-semibold text-highlighted">Qo'shimcha maydonlar</h2>
                    <UBadge v-if="fields?.length" :label="String(fields.length)" variant="subtle" size="xs" />
                  </div>
                  <UButton icon="i-lucide-plus" size="xs" variant="ghost" label="Qo'shish" @click="openFieldCreate" />
                </div>
              </template>

              <div v-if="fields?.length" class="space-y-2">
                <div
                  v-for="field in fields"
                  :key="field.id"
                  class="flex items-center gap-3 p-3 rounded-lg border border-default"
                >
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-highlighted">{{ field.label }}</p>
                    <div class="flex items-center gap-2 mt-1">
                      <UBadge :label="{ text: 'Tekst', number: 'Raqam', date: 'Sana', textarea: 'Katta tekst', select: 'Tanlov', file: 'Fayl' }[field.field_type] || field.field_type" variant="subtle" size="xs" />
                      <UBadge v-if="field.is_required" label="Majburiy" variant="subtle" color="warning" size="xs" />
                    </div>
                  </div>
                  <div class="flex gap-1 shrink-0">
                    <UButton icon="i-lucide-pencil" variant="ghost" size="xs" @click="openFieldEdit(field)" />
                    <UButton icon="i-lucide-trash-2" variant="ghost" size="xs" color="error" @click="fieldDeleteTarget = field; fieldDeleteOpen = true" />
                  </div>
                </div>
              </div>
              <p v-else class="text-sm text-muted text-center py-6">Maydonlar qo'shilmagan</p>
            </UCard>
          </div>
        </div>
      </UForm>
    </div>
  </PagePanel>

  <!-- Field Add/Edit modal -->
  <UModal v-model:open="fieldModalOpen" :title="editingField ? 'Maydonni tahrirlash' : 'Yangi maydon qo\'shish'">
    <template #body>
      <div class="space-y-5">
        <UFormField label="Nomi" required>
          <UInput v-model="fieldState.label" placeholder="masalan: Ro'yxat raqami" size="lg" class="w-full" />
        </UFormField>
        <div class="grid grid-cols-3 gap-4 items-end">
          <UFormField label="Maydon turi">
            <USelect v-model="fieldState.field_type" :items="fieldTypes" size="lg" class="w-full" />
          </UFormField>
          <UFormField label="Majburiy">
            <USwitch v-model="fieldState.is_required" />
          </UFormField>
          <UFormField label="Tartib raqami">
            <UInput v-model="fieldState.sort_order" type="number" size="lg" class="w-full" />
          </UFormField>
        </div>
        <UFormField v-if="fieldState.field_type === 'select'" label="Tanlov variantlari" help="Vergul bilan ajrating">
          <UInput v-model="fieldState.options" placeholder="variant1, variant2, variant3" size="lg" class="w-full" />
        </UFormField>
      </div>
    </template>
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton variant="ghost" label="Bekor qilish" @click="fieldModalOpen = false" />
        <UButton :label="editingField ? 'Saqlash' : 'Qo\'shish'" icon="i-lucide-save" :disabled="!fieldState.label" @click="handleFieldSave" />
      </div>
    </template>
  </UModal>

  <!-- Field Delete modal -->
  <UModal v-model:open="fieldDeleteOpen" title="Maydonni o'chirish" description="Bu maydon barcha hujjatlardan ham o'chiriladi.">
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton variant="ghost" label="Bekor qilish" @click="fieldDeleteOpen = false" />
        <UButton color="error" label="O'chirish" icon="i-lucide-trash-2" @click="handleFieldDelete" />
      </div>
    </template>
  </UModal>
</template>
