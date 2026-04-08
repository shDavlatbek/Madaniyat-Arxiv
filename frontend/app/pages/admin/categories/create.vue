<script setup lang="ts">
import { z } from 'zod'

definePageMeta({ layout: 'dashboard' })

const { apiFetch } = useApi()
const toast = useToast()
const loading = ref(false)

const schema = z.object({
  name: z.string().min(1, 'Nom kiritilishi shart'),
  code: z.string().min(1, 'Kod kiritilishi shart'),
  description: z.string().optional(),
  sort_order: z.coerce.number().default(0),
})

const state = reactive({ name: '', code: '', description: '', sort_order: 0 })

async function handleSubmit() {
  loading.value = true
  try {
    await apiFetch('/api/categories', { method: 'POST', body: state })
    toast.add({ title: 'Muvaffaqiyat', description: 'Kategoriya yaratildi', color: 'success', icon: 'i-lucide-check-circle' })
    navigateTo('/admin/categories')
  } catch (error: any) {
    toast.add({ title: 'Xatolik', description: error?.data?.detail || 'Yaratib bo\'lmadi', color: 'error', icon: 'i-lucide-alert-circle' })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <UDashboardPanel>
    <template #header>
      <UDashboardNavbar title="Yangi kategoriya">
        <template #left>
          <UButton icon="i-lucide-arrow-left" variant="ghost" to="/admin/categories" />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="max-w-2xl mx-auto p-4 sm:p-6">
        <UForm :schema="schema" :state="state" class="space-y-4" @submit="handleSubmit">
          <UFormField label="Nomi" name="name" required>
            <UInput v-model="state.name" placeholder="Buyruqlar" />
          </UFormField>
          <UFormField label="Kod" name="code" required>
            <UInput v-model="state.code" placeholder="buyruqlar" />
          </UFormField>
          <UFormField label="Tavsif" name="description">
            <UTextarea v-model="state.description" :rows="3" />
          </UFormField>
          <UFormField label="Tartib raqami" name="sort_order">
            <UInput v-model="state.sort_order" type="number" />
          </UFormField>
          <div class="flex justify-end gap-2 pt-4">
            <UButton variant="ghost" label="Bekor qilish" to="/admin/categories" />
            <UButton type="submit" label="Yaratish" icon="i-lucide-save" :loading="loading" />
          </div>
        </UForm>
      </div>
    </template>
  </UDashboardPanel>
</template>
