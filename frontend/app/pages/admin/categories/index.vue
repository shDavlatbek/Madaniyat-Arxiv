<script setup lang="ts">
import type { CategoryResponse, YearResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const { apiFetch } = useApi()
const toast = useToast()

const { data: catsData, status, refresh } = await useAsyncData('admin-categories', () =>
  apiFetch<{ items: CategoryResponse[] }>('/api/categories')
)
const { data: yearsData } = await useAsyncData('years-for-cats', () =>
  apiFetch<{ items: YearResponse[] }>('/api/years?active_only=false')
)

const categories = computed(() => catsData.value?.items || [])
const years = computed(() => yearsData.value?.items || [])
function getYearValues(yearIds: number[]) {
  if (!yearIds?.length) return '-'
  return yearIds.map(id => years.value.find(y => y.id === id)?.value || id).join(', ')
}

const columns = [
  { accessorKey: 'name', header: 'Nomi' },
  { accessorKey: 'code', header: 'Kod' },
  { id: 'year', header: 'Yil' },
  { id: 'fields_count', header: 'Maydonlar' },
  { id: 'actions', header: '' },
]

const deleteOpen = ref(false)
const deleteTarget = ref<CategoryResponse | null>(null)

const copyOpen = ref(false)
const copyTarget = ref<CategoryResponse | null>(null)
const copyYearIds = ref<number[]>([])

async function handleCopy() {
  if (!copyTarget.value || !copyYearIds.value.length) return
  try {
    await apiFetch(`/api/categories/${copyTarget.value.id}/copy`, { method: 'POST', body: { target_year_ids: copyYearIds.value } })
    toast.add({ title: 'Muvaffaqiyat', description: 'Nomenklatura nusxalandi', color: 'success', icon: 'i-lucide-check-circle' })
    copyOpen.value = false
    copyYearIds.value = []
    refresh()
  } catch (error: any) {
    toast.add({ title: 'Xatolik', description: error?.data?.detail || 'Nusxalab bo\'lmadi', color: 'error', icon: 'i-lucide-alert-circle' })
  }
}

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
    <UTable :data="categories" :columns="columns" :loading="status === 'pending'" @select="(row: any) => navigateTo(`/admin/categories/${row.original.id}/edit`)">
      <template #name-cell="{ row }">
        <div class="flex items-center gap-2">
          <UIcon name="i-lucide-folder" class="text-primary shrink-0" />
          <span class="font-semibold text-highlighted">{{ row.original.name }}</span>
        </div>
      </template>
      <template #code-cell="{ row }">
        <UBadge :label="row.original.code" variant="subtle" color="neutral" />
      </template>
      <template #year-cell="{ row }">
        <span class="font-medium">{{ getYearValues(row.original.year_ids) }}</span>
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
              { label: 'Nusxa olish', icon: 'i-lucide-copy', onSelect: () => { copyTarget = row.original; copyYearIds = []; copyOpen = true } },
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
      <EmptyState icon="i-lucide-folder-x" title="Nomenklaturalar topilmadi" description="Hozircha kategoriyalar qo'shilmagan" />
    </div>
  </PagePanel>

  <!-- Copy modal -->
  <UModal v-model:open="copyOpen" :title="`${copyTarget?.name} - Nusxa olish`">
    <template #body>
      <div class="space-y-4">
        <p class="text-sm text-muted">Nomenklaturani qaysi yillarga nusxalash kerak?</p>
        <UFormField label="Yillar" required>
          <div class="flex flex-wrap gap-2">
            <UButton
              v-for="y in years"
              :key="y.id"
              :label="String(y.value)"
              :variant="copyYearIds.includes(y.id) ? 'solid' : 'outline'"
              :color="copyYearIds.includes(y.id) ? 'primary' : 'neutral'"
              size="sm"
              @click="copyYearIds.includes(y.id) ? copyYearIds = copyYearIds.filter(id => id !== y.id) : copyYearIds.push(y.id)"
            />
          </div>
        </UFormField>
      </div>
    </template>
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton variant="outline" label="Bekor qilish" @click="copyOpen = false" />
        <UButton label="Nusxalash" icon="i-lucide-copy" :disabled="!copyYearIds.length" @click="handleCopy" />
      </div>
    </template>
  </UModal>

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
