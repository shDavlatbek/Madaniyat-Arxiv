<script setup lang="ts">
import { z } from 'zod'
import type { CategoryResponse, YearResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const { apiFetch } = useApi()
const toast = useToast()
const loading = ref(false)

const { data: yearsData } = await useAsyncData('years-for-cat', () =>
  apiFetch<{ items: YearResponse[] }>('/api/years?active_only=false'),
)
const years = computed(() => yearsData.value?.items || [])
const yearItems = computed(() => years.value.map(y => ({ label: String(y.value), value: y.id })))

const schema = z.object({
  name: z.string().min(1, 'Nom kiritilishi shart'),
  description: z.string().optional(),
  sort_order: z.coerce.number().default(0),
  year_id: z.number({ required_error: 'Yil tanlanishi shart' }),
})

const state = reactive({
  name: '',
  description: '',
  sort_order: 0,
  year_id: undefined as number | undefined,
})

// === Temp fields (staged before category creation) ===
interface TempField {
  label: string
  field_type: string
  is_required: boolean
  sort_order: number
  placeholder: string
  options: string
}

const tempFields = ref<TempField[]>([])
const fieldModalOpen = ref(false)
const editingFieldIndex = ref<number | null>(null)
const fieldModalData = ref<{ label: string; field_type: string; is_required: boolean; options: string } | undefined>()

function openFieldCreate() {
  editingFieldIndex.value = null
  fieldModalData.value = undefined
  fieldModalOpen.value = true
}

function openFieldEdit(index: number) {
  editingFieldIndex.value = index
  const f = tempFields.value[index]!
  fieldModalData.value = { label: f.label, field_type: f.field_type, is_required: f.is_required, options: f.options }
  fieldModalOpen.value = true
}

function onFieldSave(data: { label: string; field_type: string; is_required: boolean; options: string }) {
  const field: TempField = { ...data, sort_order: 0, placeholder: '' }
  if (editingFieldIndex.value !== null) {
    tempFields.value[editingFieldIndex.value] = field
  } else {
    tempFields.value.push(field)
  }
}

function removeField(index: number) {
  tempFields.value.splice(index, 1)
}

// === Submit: create category, then add fields ===
async function handleSubmit() {
  loading.value = true
  try {
    const category = await apiFetch<CategoryResponse>('/api/categories', { method: 'POST', body: state })

    // Add each temp field to the created category
    for (const f of tempFields.value) {
      const body: Record<string, any> = {
        label: f.label,
        field_type: f.field_type,
        is_required: f.is_required,
        sort_order: f.sort_order,
        placeholder: f.placeholder || null,
        options: f.field_type === 'select' && f.options
          ? f.options.split(',').map(s => s.trim()).filter(Boolean)
          : null,
      }
      try {
        await apiFetch(`/api/categories/${category.id}/fields`, { method: 'POST', body })
      } catch {
        toast.add({ title: 'Ogohlantirish', description: `"${f.label}" maydonini qo'shib bo'lmadi`, color: 'warning', icon: 'i-lucide-alert-triangle' })
      }
    }

    toast.add({ title: 'Muvaffaqiyat', description: 'Nomenklatura yaratildi', color: 'success', icon: 'i-lucide-check-circle' })
    navigateTo('/admin/categories')
  } catch (error: any) {
    toast.add({ title: 'Xatolik', description: error?.data?.detail || 'Yaratib bo\'lmadi', color: 'error', icon: 'i-lucide-alert-circle' })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <PagePanel title="Yangi nomenklatura" icon="i-lucide-folder-plus">
    <template #headerLeft>
      <UButton icon="i-lucide-arrow-left" variant="ghost" color="neutral" to="/admin/categories" />
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
                  <UInput v-model="state.name" placeholder="Buyruqlar" icon="i-lucide-folder" size="lg" class="w-full" />
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
              <UButton type="submit" label="Nomenklaturani yaratish" icon="i-lucide-save" :loading="loading" />
            </div>
          </div>

          <!-- Right: Fields (temp, staged) -->
          <div class="w-full lg:w-96 xl:w-md shrink-0">
            <UCard :ui="{ header: 'border-b border-default' }">
              <template #header>
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-2">
                    <UIcon name="i-lucide-layers" class="w-4 h-4 text-muted" />
                    <h2 class="text-sm font-semibold text-highlighted">Qo'shimcha maydonlar</h2>
                    <UBadge v-if="tempFields.length" :label="String(tempFields.length)" variant="subtle" size="xs" />
                  </div>
                  <UButton icon="i-lucide-plus" size="xs" variant="ghost" label="Qo'shish" @click="openFieldCreate" />
                </div>
              </template>

              <div v-if="tempFields.length" class="space-y-2">
                <div
                  v-for="(field, i) in tempFields"
                  :key="i"
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
                    <UButton icon="i-lucide-pencil" variant="ghost" size="xs" @click="openFieldEdit(i)" />
                    <UButton icon="i-lucide-x" variant="ghost" size="xs" color="error" @click="removeField(i)" />
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

  <FieldModal v-model:open="fieldModalOpen" :editing="editingFieldIndex !== null" :initial-data="fieldModalData" @save="onFieldSave" />
</template>
