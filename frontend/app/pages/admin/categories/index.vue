<script setup lang="ts">
import type { CategoryResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const { apiFetch } = useApi()
const toast = useToast()

const { data: catsData, status, refresh } = await useAsyncData('admin-categories', () =>
  apiFetch<{ items: CategoryResponse[] }>('/api/categories')
)

const allCategories = computed(() => catsData.value?.items || [])

const search = ref('')
const categories = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return allCategories.value
  return allCategories.value.filter(c => c.name.toLowerCase().includes(q))
})

const columns = [
  { accessorKey: 'name', header: 'Nomenklatura' },
  { id: 'fields_count', header: 'Maydonlar' },
  { id: 'actions', header: '' },
]

const deleteOpen = ref(false)
const deleteTarget = ref<CategoryResponse | null>(null)

async function handleDelete() {
  if (!deleteTarget.value) return
  try {
    await apiFetch(`/api/categories/${deleteTarget.value.id}`, { method: 'DELETE' })
    toast.add({ title: 'Muvaffaqiyat', description: 'Nomenklatura o\'chirildi', color: 'success', icon: 'i-lucide-check-circle' })
    deleteOpen.value = false
    refresh()
  } catch {
    toast.add({ title: 'Xatolik', description: 'O\'chirib bo\'lmadi', color: 'error', icon: 'i-lucide-alert-circle' })
  }
}
</script>

<template>
  <PagePanel title="Nomenklaturalar" icon="i-lucide-folder">
    <template #headerRight>
      <UBadge :label="`${categories.length} nomenklatura`" variant="subtle" class="mr-2" />
      <UButton icon="i-lucide-plus" label="Yangi nomenklatura" to="/admin/categories/create" />
    </template>
    <template #toolbar>
      <UInput
        v-model="search"
        icon="i-lucide-search"
        placeholder="Qidirish..."
        class="w-64"
      />
      <UButton
        v-if="search"
        icon="i-lucide-x"
        variant="ghost"
        color="error"
        size="sm"
        label="Tozalash"
        @click="search = ''"
      />
    </template>
    <UTable :data="categories" :columns="columns" :loading="status === 'pending'">
      <template #name-cell="{ row }">
        <div class="flex items-center gap-2">
          <UIcon name="i-lucide-folder" class="text-primary shrink-0" />
          <NuxtLink :to="`/admin/categories/${row.original.id}/edit`" class="font-semibold text-primary hover:underline">
            {{ row.original.name }}
          </NuxtLink>
        </div>
      </template>
      <template #fields_count-cell="{ row }">
        <UBadge :label="`${row.original.fields?.length || 0} maydon`" variant="subtle" />
      </template>
      <template #actions-cell="{ row }">
        <div class="flex gap-1 justify-end">
          <UDropdownMenu :items="[
            [
              { label: 'Tahrirlash', icon: 'i-lucide-pencil', onSelect: () => navigateTo(`/admin/categories/${row.original.id}/edit`) },
              { label: 'Maydonlar', icon: 'i-lucide-layers', onSelect: () => navigateTo(`/admin/categories/${row.original.id}/fields`) },
            ],
            [
              { label: 'O\'chirish', icon: 'i-lucide-trash-2', color: 'error', onSelect: () => { deleteTarget = row.original; deleteOpen = true } },
            ],
          ]">
            <UButton icon="i-lucide-ellipsis-vertical" variant="ghost" size="xs" />
          </UDropdownMenu>
        </div>
      </template>
    </UTable>

    <div v-if="!categories.length && status !== 'pending'" class="flex items-center justify-center p-12">
      <EmptyState icon="i-lucide-folder-x" title="Nomenklaturalar topilmadi" description="Hozircha nomenklaturalar qo'shilmagan" />
    </div>
  </PagePanel>

  <!-- Delete modal -->
  <UModal v-model:open="deleteOpen" title="Nomenklaturani o'chirish" description="Barcha bog'liq maydonlar ham o'chiriladi.">
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton variant="ghost" label="Bekor qilish" @click="deleteOpen = false" />
        <UButton color="error" label="O'chirish" icon="i-lucide-trash-2" @click="handleDelete" />
      </div>
    </template>
  </UModal>
</template>
