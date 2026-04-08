<script setup lang="ts">
import type { CategoryResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const { apiFetch } = useApi()
const toast = useToast()

const { data: catsData, status, refresh } = await useAsyncData('admin-categories', () =>
  apiFetch<{ items: CategoryResponse[] }>('/api/categories')
)

const categories = computed(() => catsData.value?.items || [])

const columns = [
  { key: 'name', label: 'Nomi' },
  { key: 'code', label: 'Kod' },
  { key: 'fields_count', label: 'Maydonlar' },
  { key: 'actions', label: '' },
]

const deleteOpen = ref(false)
const deleteTarget = ref<CategoryResponse | null>(null)

async function handleDelete() {
  if (!deleteTarget.value) return
  try {
    await apiFetch(`/api/categories/${deleteTarget.value.id}`, { method: 'DELETE' })
    toast.add({ title: 'Muvaffaqiyat', description: 'Kategoriya o\'chirildi', color: 'success', icon: 'i-lucide-check-circle' })
    deleteOpen.value = false
    refresh()
  } catch {
    toast.add({ title: 'Xatolik', description: 'O\'chirib bo\'lmadi', color: 'error', icon: 'i-lucide-alert-circle' })
  }
}
</script>

<template>
  <UDashboardPanel>
    <template #header>
      <UDashboardNavbar title="Kategoriyalar">
        <template #right>
          <UButton icon="i-lucide-plus" label="Yangi kategoriya" to="/admin/categories/create" />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <UTable :data="categories" :columns="columns" :loading="status === 'pending'">
        <template #name-cell="{ row }">
          <span class="font-semibold">{{ row.name }}</span>
        </template>
        <template #fields_count-cell="{ row }">
          <UBadge :label="`${row.fields?.length || 0} maydon`" variant="subtle" />
        </template>
        <template #actions-cell="{ row }">
          <UDropdownMenu :items="[
            [
              { label: 'Tahrirlash', icon: 'i-lucide-pencil', onSelect: () => navigateTo(`/admin/categories/${row.id}/edit`) },
              { label: 'Maydonlar', icon: 'i-lucide-layers', onSelect: () => navigateTo(`/admin/categories/${row.id}/fields`) },
            ],
            [
              { label: 'O\'chirish', icon: 'i-lucide-trash-2', color: 'error', onSelect: () => { deleteTarget = row; deleteOpen = true } },
            ],
          ]">
            <UButton icon="i-lucide-ellipsis-vertical" variant="ghost" size="xs" />
          </UDropdownMenu>
        </template>
      </UTable>
    </template>
  </UDashboardPanel>

  <UModal v-model:open="deleteOpen" title="Kategoriyani o'chirish" description="Barcha bog'liq maydonlar ham o'chiriladi.">
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton variant="ghost" label="Bekor qilish" @click="deleteOpen = false" />
        <UButton color="error" label="O'chirish" icon="i-lucide-trash-2" @click="handleDelete" />
      </div>
    </template>
  </UModal>
</template>
