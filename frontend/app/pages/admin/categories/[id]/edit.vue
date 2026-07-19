<script setup lang="ts">
import { z } from 'zod'
import type { CategoryResponse } from '~/types'

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

// A nomenklatura is a unique year number (e.g. 2024).
const schema = z.object({
  year: z.coerce.number({ invalid_type_error: 'Yil raqamini kiriting' })
    .int('Yil butun son bo\'lishi kerak')
    .gte(1900, 'Yil 1900 dan katta bo\'lishi kerak')
    .lte(2100, 'Yil 2100 dan kichik bo\'lishi kerak'),
})

const state = reactive({ year: Number(category.value?.name) || new Date().getFullYear() })

const isDirty = computed(() => String(state.year) !== (category.value?.name || ''))

async function handleSubmit() {
  loading.value = true
  try {
    await apiFetch(`/api/categories/${catId.value}`, { method: 'PUT', body: { name: String(state.year) } })
    toast.add({ title: 'Muvaffaqiyat', description: 'Nomenklatura yangilandi', color: 'success', icon: 'i-lucide-check-circle' })
    navigateTo('/admin/categories')
  } catch (error: any) {
    toast.add({ title: 'Xatolik', description: error?.data?.detail || 'Yangilab bo\'lmadi', color: 'error', icon: 'i-lucide-alert-circle' })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <PagePanel :title="`Tahrirlash: ${category?.name || ''}`" icon="i-lucide-folder-pen">
    <template #headerLeft>
      <UButton icon="i-lucide-arrow-left" variant="ghost" color="neutral" to="/admin/categories" />
    </template>
    <template #headerRight>
      <UButton
        icon="i-lucide-layers"
        variant="ghost"
        label="Maydonlar"
        :to="`/admin/categories/${catId}/fields`"
      />
    </template>

    <div class="p-6 max-w-xl">
      <UForm :schema="schema" :state="state" @submit="handleSubmit">
        <UCard :ui="{ body: 'space-y-5' }">
          <UFormField label="Nomenklatura (yil)" name="year" required help="Yil raqami — takrorlanmaydi (masalan: 2024)">
            <UInput v-model="state.year" type="number" placeholder="2024" icon="i-lucide-calendar" size="lg" class="w-full" />
          </UFormField>

          <div class="flex items-center justify-end gap-3">
            <UButton variant="ghost" color="neutral" label="Bekor qilish" to="/admin/categories" :disabled="loading" />
            <UButton type="submit" label="Saqlash" icon="i-lucide-save" :loading="loading" :disabled="!isDirty" />
          </div>
        </UCard>
      </UForm>
    </div>
  </PagePanel>
</template>
