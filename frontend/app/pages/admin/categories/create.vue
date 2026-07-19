<script setup lang="ts">
import { z } from 'zod'
import type { CategoryResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const { apiFetch } = useApi()
const toast = useToast()
const loading = ref(false)

// Nomenklatura is identified only by its name (the Year concept was removed).
const schema = z.object({
  name: z.string().min(1, 'Nomenklatura nomi kiritilishi shart'),
})

const state = reactive({ name: '' })

async function handleSubmit() {
  loading.value = true
  try {
    await apiFetch<CategoryResponse>('/api/categories', {
      method: 'POST',
      body: { name: state.name.trim() },
    })
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

    <div class="p-6 max-w-xl">
      <UForm :schema="schema" :state="state" @submit="handleSubmit">
        <UCard :ui="{ body: 'space-y-5' }">
          <UFormField label="Nomenklatura" name="name" required help="Nomenklatura nomi (masalan: 2024)">
            <UInput v-model="state.name" placeholder="Nomenklatura nomi" icon="i-lucide-folder" size="lg" class="w-full" autofocus />
          </UFormField>

          <div class="flex items-center justify-end gap-3">
            <UButton variant="ghost" color="neutral" label="Bekor qilish" to="/admin/categories" :disabled="loading" />
            <UButton type="submit" label="Yaratish" icon="i-lucide-save" :loading="loading" />
          </div>
        </UCard>
      </UForm>
    </div>
  </PagePanel>
</template>
