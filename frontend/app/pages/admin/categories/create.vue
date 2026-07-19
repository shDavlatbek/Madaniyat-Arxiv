<script setup lang="ts">
import { z } from 'zod'
import type { CategoryResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const { apiFetch } = useApi()
const toast = useToast()
const loading = ref(false)

// A nomenklatura is a unique year number (e.g. 2024).
const schema = z.object({
  year: z.coerce.number({ invalid_type_error: 'Yil raqamini kiriting' })
    .int('Yil butun son bo\'lishi kerak')
    .gte(1900, 'Yil 1900 dan katta bo\'lishi kerak')
    .lte(2100, 'Yil 2100 dan kichik bo\'lishi kerak'),
})

const state = reactive({ year: new Date().getFullYear() })

async function handleSubmit() {
  loading.value = true
  try {
    await apiFetch<CategoryResponse>('/api/categories', {
      method: 'POST',
      body: { name: String(state.year) },
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
          <UFormField label="Nomenklatura (yil)" name="year" required help="Yil raqami — takrorlanmaydi (masalan: 2024)">
            <UInput v-model="state.year" type="number" placeholder="2024" icon="i-lucide-calendar" size="lg" class="w-full" autofocus />
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
