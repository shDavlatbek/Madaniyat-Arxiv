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

const allCategories = computed(() => catsData.value?.items || [])
const years = computed(() => yearsData.value?.items || [])
const yearItems = computed(() => years.value.map(y => ({ label: String(y.value), value: y.id })))
function getYearValue(yearId: number | null) {
  if (!yearId) return '-'
  return years.value.find(y => y.id === yearId)?.value || '-'
}

const search = ref('')
const selectedYearId = ref<number | undefined>(undefined)

const categories = computed(() => {
  let result = allCategories.value
  if (selectedYearId.value) {
    result = result.filter(c => c.year_id === selectedYearId.value)
  }
  if (search.value) {
    const q = search.value.toLowerCase()
    result = result.filter(c =>
      c.name.toLowerCase().includes(q) || c.code.toLowerCase().includes(q)
    )
  }
  return result
})

const columns = [
  { accessorKey: 'name', header: 'Nomi' },
  { id: 'year', header: 'Yil' },
  { id: 'fields_count', header: 'Maydonlar' },
  { id: 'actions', header: '' },
]

const deleteOpen = ref(false)
const deleteTarget = ref<CategoryResponse | null>(null)

const copyOpen = ref(false)
const copyTarget = ref<CategoryResponse | null>(null)
const copyYearId = ref<number | undefined>(undefined)

async function handleCopy() {
  if (!copyTarget.value || !copyYearId.value) return
  try {
    await apiFetch(`/api/categories/${copyTarget.value.id}/copy`, { method: 'POST', body: { target_year_id: copyYearId.value } })
    toast.add({ title: 'Muvaffaqiyat', description: 'Nomenklatura nusxalandi', color: 'success', icon: 'i-lucide-check-circle' })
    copyOpen.value = false
    copyYearId.value = undefined
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
    <template #toolbar>
      <USelect
        v-model="selectedYearId"
        :items="yearItems"
        placeholder="Barcha yillar"
        icon="i-lucide-calendar"
        class="w-44"
      />
      <UInput
        v-model="search"
        icon="i-lucide-search"
        placeholder="Qidirish..."
        class="w-64"
      />
      <UButton
        v-if="search || selectedYearId"
        icon="i-lucide-x"
        variant="ghost"
        color="error"
        size="sm"
        label="Tozalash"
        @click="search = ''; selectedYearId = undefined"
      />
    </template>
    <UTable :data="categories" :columns="columns" :loading="status === 'pending'" @select="(row: any) => navigateTo(`/admin/categories/${row.original.id}/edit`)">
      <template #name-cell="{ row }">
        <div class="flex items-center gap-2">
          <UIcon name="i-lucide-folder" class="text-primary shrink-0" />
          <span class="font-semibold text-highlighted">{{ row.original.name }}</span>
        </div>
      </template>
      <template #year-cell="{ row }">
        <span class="font-medium">{{ getYearValue(row.original.year_id) }}</span>
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
              { label: 'Nusxa olish', icon: 'i-lucide-copy', onSelect: () => { copyTarget = row.original; copyYearId = undefined; copyOpen = true } },
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
        <p class="text-sm text-muted">Nomenklaturani qaysi yilga nusxalash kerak?</p>
        <UFormField label="Yil" required>
          <USelect
            v-model="copyYearId"
            :items="yearItems"
            placeholder="Yilni tanlang"
            icon="i-lucide-calendar"
            size="lg"
          />
        </UFormField>
      </div>
    </template>
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton variant="outline" label="Bekor qilish" @click="copyOpen = false" />
        <UButton label="Nusxalash" icon="i-lucide-copy" :disabled="!copyYearId" @click="handleCopy" />
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
