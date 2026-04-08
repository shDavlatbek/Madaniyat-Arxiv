<script setup lang="ts">
import { z } from 'zod'
import type { CategoryResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const route = useRoute()
const catId = computed(() => route.params.id as string)
const { apiFetch } = useApi()
const toast = useToast()
const loading = ref(false)

const { data: category } = await useAsyncData(`cat-edit-${catId.value}`, () => {
  // Get from all categories list since there's no direct GET /api/categories/:id
  return apiFetch<{ items: CategoryResponse[] }>('/api/categories').then(
    res => res.items.find(c => c.id === catId.value) || null
  )
})

const schema = z.object({
  name: z.string().min(1),
  code: z.string().min(1),
  description: z.string().optional(),
  sort_order: z.coerce.number(),
})

const state = reactive({
  name: category.value?.name || '',
  code: category.value?.code || '',
  description: category.value?.description || '',
  sort_order: category.value?.sort_order || 0,
})

async function handleSubmit() {
  loading.value = true
  try {
    await apiFetch(`/api/categories/${catId.value}`, { method: 'PUT', body: state })
    toast.add({ title: 'Muvaffaqiyat', description: 'Kategoriya yangilandi', color: 'success', icon: 'i-lucide-check-circle' })
    navigateTo('/admin/categories')
  } catch (error: any) {
    toast.add({ title: 'Xatolik', description: error?.data?.detail || 'Yangilab bo\'lmadi', color: 'error', icon: 'i-lucide-alert-circle' })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <UDashboardPanel>
    <template #header>
      <UDashboardNavbar :title="`Tahrirlash: ${category?.name}`">
        <template #left>
          <UButton icon="i-lucide-arrow-left" variant="ghost" to="/admin/categories" />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="max-w-2xl mx-auto p-4 sm:p-6">
        <UForm :schema="schema" :state="state" class="space-y-4" @submit="handleSubmit">
          <UFormField label="Nomi" name="name" required>
            <UInput v-model="state.name" />
          </UFormField>
          <UFormField label="Kod" name="code" required>
            <UInput v-model="state.code" />
          </UFormField>
          <UFormField label="Tavsif" name="description">
            <UTextarea v-model="state.description" :rows="3" />
          </UFormField>
          <UFormField label="Tartib raqami" name="sort_order">
            <UInput v-model="state.sort_order" type="number" />
          </UFormField>
          <div class="flex justify-end gap-2 pt-4">
            <UButton variant="ghost" label="Bekor qilish" to="/admin/categories" />
            <UButton type="submit" label="Saqlash" icon="i-lucide-save" :loading="loading" />
          </div>
        </UForm>
      </div>
    </template>
  </UDashboardPanel>
</template>
