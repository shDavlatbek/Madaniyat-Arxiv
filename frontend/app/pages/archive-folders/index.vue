<script setup lang="ts">
import type { ArchiveFolderResponse, RetentionPeriod, YearResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const { apiFetch } = useApi()
const { create, update, remove } = useArchiveFolders()
const toast = useToast()

// Year filter
const yearFilter = ref<number | undefined>(undefined)

const { data: yearsData } = await useAsyncData('archive-folders-years', () =>
  apiFetch<{ items: YearResponse[] }>('/api/years?active_only=false'),
)
const years = computed(() => yearsData.value?.items || [])
const yearFilterItems = computed(() => [
  { label: 'Barcha yillar', value: undefined as number | undefined },
  ...years.value.map(y => ({ label: `${y.value}`, value: y.id })),
])
const yearSelectItems = computed(() =>
  years.value.map(y => ({ label: `${y.value}`, value: y.id })),
)

// Folders list — refetches when the year filter changes
const { data: foldersData, status, refresh } = await useAsyncData(
  'archive-folders',
  () => {
    const q = yearFilter.value != null ? `?year_id=${yearFilter.value}` : ''
    return apiFetch<{ items: ArchiveFolderResponse[] }>(`/api/archive-folders${q}`)
  },
  { watch: [yearFilter] },
)
const folders = computed(() => foldersData.value?.items || [])

const columns = [
  { id: 'row_number', header: 'T/r' },
  { accessorKey: 'index_code', header: LABELS.index_code },
  { accessorKey: 'title', header: LABELS.title },
  { accessorKey: 'retention_period', header: LABELS.retention_period },
  { accessorKey: 'start_date', header: LABELS.start_date },
  { accessorKey: 'end_date', header: LABELS.end_date },
  { accessorKey: 'document_count', header: LABELS.document_count },
  { id: 'actions', header: '' },
]

const retentionItems = Object.entries(RETENTION_PERIOD_LABELS).map(([value, label]) => ({
  label,
  value: value as RetentionPeriod,
}))

// Create / edit modal
const modalOpen = ref(false)
const editing = ref<ArchiveFolderResponse | null>(null)
const saving = ref(false)
const state = reactive({
  index_code: '',
  title: '',
  retention_period: '' as RetentionPeriod | '',
  start_date: '',
  end_date: '',
  year_id: undefined as number | undefined,
})

function openCreate() {
  editing.value = null
  state.index_code = ''
  state.title = ''
  state.retention_period = ''
  state.start_date = ''
  state.end_date = ''
  state.year_id = yearFilter.value
  modalOpen.value = true
}

function openEdit(folder: ArchiveFolderResponse) {
  editing.value = folder
  state.index_code = folder.index_code
  state.title = folder.title
  state.retention_period = folder.retention_period
  state.start_date = folder.start_date
  state.end_date = folder.end_date || ''
  state.year_id = folder.year_id ?? undefined
  modalOpen.value = true
}

const canSave = computed(() =>
  !!state.index_code.trim() && !!state.title.trim() && !!state.retention_period && !!state.start_date,
)

async function handleSave() {
  if (!canSave.value) return
  saving.value = true
  try {
    const payload = {
      index_code: state.index_code.trim(),
      title: state.title.trim(),
      retention_period: state.retention_period as RetentionPeriod,
      start_date: state.start_date,
      end_date: state.end_date || null,
      year_id: state.year_id ?? null,
    }
    if (editing.value) {
      await update(editing.value.id, payload)
      toast.add({ title: 'Muvaffaqiyat', description: "Yig'ma jild yangilandi", color: 'success', icon: 'i-lucide-check-circle' })
    } else {
      await create(payload)
      toast.add({ title: 'Muvaffaqiyat', description: "Yig'ma jild qo'shildi", color: 'success', icon: 'i-lucide-check-circle' })
    }
    modalOpen.value = false
    refresh()
  } catch (error: any) {
    toast.add({ title: 'Xatolik', description: error?.data?.detail || 'Xatolik yuz berdi', color: 'error', icon: 'i-lucide-alert-circle' })
  } finally {
    saving.value = false
  }
}

// Delete confirmation
const deleteOpen = ref(false)
const deleteTarget = ref<ArchiveFolderResponse | null>(null)

async function handleDelete() {
  if (!deleteTarget.value) return
  try {
    await remove(deleteTarget.value.id)
    toast.add({ title: 'Muvaffaqiyat', description: "Yig'ma jild o'chirildi", color: 'success', icon: 'i-lucide-check-circle' })
    deleteOpen.value = false
    refresh()
  } catch (error: any) {
    toast.add({ title: 'Xatolik', description: error?.data?.detail || "O'chirib bo'lmadi", color: 'error', icon: 'i-lucide-alert-circle' })
  }
}

function formatDate(date: string | null) {
  if (!date) return '—'
  const parts = date.split('-')
  if (parts.length !== 3) return date
  return `${parts[2]}.${parts[1]}.${parts[0]}`
}
</script>

<template>
  <PagePanel :title="LABELS.archive_folders" icon="i-lucide-folder-archive">
    <template #headerRight>
      <UBadge :label="`${folders.length}`" variant="subtle" class="mr-2" />
      <UButton icon="i-lucide-plus" :label="LABELS.add_archive_folder" @click="openCreate" />
    </template>

    <template #toolbar>
      <USelect
        v-model="yearFilter"
        :items="yearFilterItems"
        placeholder="Barcha yillar"
        icon="i-lucide-calendar"
        size="sm"
        class="w-48"
      />
    </template>

    <UTable :data="folders" :columns="columns" :loading="status === 'pending'">
      <template #row_number-cell="{ row }">
        <span class="text-muted">{{ row.index + 1 }}</span>
      </template>
      <template #index_code-cell="{ row }">
        <span class="font-semibold text-highlighted">{{ row.original.index_code }}</span>
      </template>
      <template #retention_period-cell="{ row }">
        <UBadge :label="RETENTION_PERIOD_LABELS[row.original.retention_period]" variant="subtle" />
      </template>
      <template #start_date-cell="{ row }">
        <span class="text-sm">{{ formatDate(row.original.start_date) }}</span>
      </template>
      <template #end_date-cell="{ row }">
        <span class="text-sm">{{ formatDate(row.original.end_date) }}</span>
      </template>
      <template #document_count-cell="{ row }">
        <UBadge :label="`${row.original.document_count}`" color="neutral" variant="subtle" />
      </template>
      <template #actions-cell="{ row }">
        <div class="flex gap-1 justify-end">
          <UButton icon="i-lucide-pencil" variant="ghost" size="xs" @click="openEdit(row.original)" />
          <UButton icon="i-lucide-trash-2" variant="ghost" size="xs" color="error" @click="deleteTarget = row.original; deleteOpen = true" />
        </div>
      </template>
    </UTable>

    <div v-if="!folders.length && status !== 'pending'" class="flex items-center justify-center p-12">
      <EmptyState
        icon="i-lucide-folder-archive"
        :title="`${LABELS.archive_folders} topilmadi`"
        description="Hali yig'ma jildlar qo'shilmagan"
      />
    </div>
  </PagePanel>

  <!-- Create / edit modal -->
  <UModal v-model:open="modalOpen" :title="editing ? LABELS.edit_archive_folder : LABELS.add_archive_folder">
    <template #body>
      <div class="space-y-5">
        <UFormField :label="LABELS.index_code" required>
          <UInput v-model="state.index_code" placeholder="01-15" icon="i-lucide-hash" size="lg" class="w-full" />
        </UFormField>
        <UFormField :label="LABELS.title" required>
          <UInput v-model="state.title" placeholder="Yig'ma jild sarlavhasi" size="lg" class="w-full" />
        </UFormField>
        <UFormField :label="LABELS.retention_period" required>
          <USelect
            v-model="state.retention_period"
            :items="retentionItems"
            placeholder="Saqlash muddatini tanlang"
            icon="i-lucide-clock"
            size="lg"
            class="w-full"
          />
        </UFormField>
        <div class="grid grid-cols-2 gap-3">
          <UFormField :label="LABELS.start_date" required>
            <DatePicker v-model="state.start_date" placeholder="Boshlanish" size="md" />
          </UFormField>
          <UFormField :label="LABELS.end_date">
            <DatePicker v-model="state.end_date" :min-date="state.start_date" placeholder="Tugash (ixtiyoriy)" size="md" />
          </UFormField>
        </div>
        <UFormField label="Yil">
          <USelect
            v-model="state.year_id"
            :items="yearSelectItems"
            placeholder="Yilni tanlang (ixtiyoriy)"
            icon="i-lucide-calendar"
            size="lg"
            class="w-full"
          />
        </UFormField>
      </div>
    </template>
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton variant="ghost" label="Bekor qilish" @click="modalOpen = false" />
        <UButton
          :label="editing ? 'Saqlash' : 'Qo\'shish'"
          icon="i-lucide-save"
          :loading="saving"
          :disabled="!canSave"
          @click="handleSave"
        />
      </div>
    </template>
  </UModal>

  <!-- Delete confirmation -->
  <UModal
    v-model:open="deleteOpen"
    :title="LABELS.delete_archive_folder"
    :description="deleteTarget ? `«${deleteTarget.title}» yig'ma jildi o'chiriladi. Bu amalni qaytarib bo'lmaydi.` : ''"
  >
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton variant="ghost" label="Bekor qilish" @click="deleteOpen = false" />
        <UButton color="error" label="O'chirish" icon="i-lucide-trash-2" @click="handleDelete" />
      </div>
    </template>
  </UModal>
</template>
