<script setup lang="ts">
import type { ArchiveFolderResponse, DepartmentResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const { apiFetch } = useApi()
const { create, update, remove } = useArchiveFolders()
const { listRetentionPeriods } = useReferences()
const { list: listDepartments } = useDepartments()
const toast = useToast()

// Reference data
const { data: retentionData } = await useAsyncData('archive-folders-retention', () => listRetentionPeriods())
const retentionItems = computed(() =>
  (retentionData.value?.items || []).map(r => ({ label: r.name, value: r.id })),
)

const { data: departmentsData } = await useAsyncData('archive-folders-departments', () => listDepartments())
const departments = computed<DepartmentResponse[]>(() => departmentsData.value?.items || [])
const departmentItems = computed(() =>
  departments.value.map(d => ({
    label: d.index_code ? `${d.index_code} — ${d.name}` : d.name,
    value: d.id,
  })),
)

// Folders list
const { data: foldersData, status, refresh } = await useAsyncData(
  'archive-folders',
  () => apiFetch<{ items: ArchiveFolderResponse[] }>('/api/archive-folders'),
)
const folders = computed(() => foldersData.value?.items || [])

function fmtDate(d: string | null): string {
  if (!d) return '—'
  const p = d.split('-')
  return p.length === 3 ? `${p[2]}.${p[1]}.${p[0]}` : d
}

const columns = [
  { id: 'row_number', header: 'T/r' },
  { accessorKey: 'department_name', header: LABELS.department_name },
  { accessorKey: 'department_index_code', header: LABELS.department_index_code },
  { accessorKey: 'index_code', header: LABELS.index_code },
  { accessorKey: 'title', header: LABELS.title },
  { accessorKey: 'article_number', header: LABELS.article_number },
  { accessorKey: 'list_number', header: LABELS.list_number },
  { accessorKey: 'retention_period_name', header: LABELS.retention_period },
  { id: 'dates', header: 'Sanalar' },
  { id: 'sheets', header: LABELS.total_sheets },
  { accessorKey: 'note', header: LABELS.archive_folder_note },
  { id: 'actions', header: '' },
]

// Create / edit modal
const modalOpen = ref(false)
const editing = ref<ArchiveFolderResponse | null>(null)
const saving = ref(false)
const state = reactive({
  department_id: '' as string,
  index_code: '',
  title: '',
  article_number: '',
  list_number: '',
  retention_period_id: '' as string,
  total_sheets: undefined as number | undefined,
  start_date: '',
  end_date: '',
  note: '',
})

// "Bo'lim indeksi" auto-shown under the selected department.
const selectedDepartment = computed(() =>
  departments.value.find(d => d.id === state.department_id) || null,
)

// "Avtomatik summa" — sum of the editing folder's documents' pages.
const autoPagesSum = computed(() => editing.value?.documents_pages_sum ?? 0)

function openCreate() {
  editing.value = null
  state.department_id = ''
  state.index_code = ''
  state.title = ''
  state.article_number = ''
  state.list_number = ''
  state.retention_period_id = ''
  state.total_sheets = undefined
  state.start_date = ''
  state.end_date = ''
  state.note = ''
  modalOpen.value = true
}

function openEdit(folder: ArchiveFolderResponse) {
  editing.value = folder
  state.department_id = folder.department_id || ''
  state.index_code = folder.index_code
  state.title = folder.title
  state.article_number = folder.article_number || ''
  state.list_number = folder.list_number || ''
  state.retention_period_id = folder.retention_period_id || ''
  state.total_sheets = folder.total_sheets ?? undefined
  state.start_date = folder.start_date || ''
  state.end_date = folder.end_date || ''
  state.note = folder.note || ''
  modalOpen.value = true
}

const canSave = computed(() => !!state.index_code.trim() && !!state.title.trim())

async function handleSave() {
  if (!canSave.value) return
  saving.value = true
  try {
    const payload = {
      index_code: state.index_code.trim(),
      title: state.title.trim(),
      department_id: state.department_id || null,
      article_number: state.article_number.trim() || null,
      list_number: state.list_number.trim() || null,
      retention_period_id: state.retention_period_id || null,
      total_sheets: state.total_sheets ?? null,
      start_date: state.start_date || null,
      end_date: state.end_date || null,
      note: state.note.trim() || null,
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
</script>

<template>
  <PagePanel :title="LABELS.archive_folders" icon="i-lucide-folder-archive">
    <template #headerRight>
      <UBadge :label="`${folders.length}`" variant="subtle" class="mr-2" />
      <UButton icon="i-lucide-plus" :label="LABELS.add_archive_folder" @click="openCreate" />
    </template>

    <UTable :data="folders" :columns="columns" :loading="status === 'pending'">
      <template #row_number-cell="{ row }">
        <span class="text-muted">{{ row.index + 1 }}</span>
      </template>
      <template #department_name-cell="{ row }">
        <span v-if="row.original.department_name">{{ row.original.department_name }}</span>
        <span v-else class="text-muted">—</span>
      </template>
      <template #department_index_code-cell="{ row }">
        <span v-if="row.original.department_index_code" class="font-mono text-sm">{{ row.original.department_index_code }}</span>
        <span v-else class="text-muted">—</span>
      </template>
      <template #index_code-cell="{ row }">
        <span class="font-semibold text-highlighted">{{ row.original.index_code }}</span>
      </template>
      <template #article_number-cell="{ row }">
        <span v-if="row.original.article_number" class="font-mono text-sm">{{ row.original.article_number }}</span>
        <span v-else class="text-muted">—</span>
      </template>
      <template #list_number-cell="{ row }">
        <span v-if="row.original.list_number" class="font-mono text-sm">{{ row.original.list_number }}</span>
        <span v-else class="text-muted">—</span>
      </template>
      <template #dates-cell="{ row }">
        <span v-if="row.original.start_date || row.original.end_date" class="text-sm whitespace-nowrap">
          {{ fmtDate(row.original.start_date) }} – {{ fmtDate(row.original.end_date) }}
        </span>
        <span v-else class="text-muted">—</span>
      </template>
      <template #sheets-cell="{ row }">
        <div class="flex items-center gap-1.5 whitespace-nowrap">
          <span class="font-semibold text-highlighted">{{ row.original.total_sheets ?? '—' }}</span>
          <span v-if="row.original.documents_pages_sum" class="text-xs text-muted">({{ row.original.documents_pages_sum }})</span>
        </div>
      </template>
      <template #retention_period_name-cell="{ row }">
        <UBadge v-if="row.original.retention_period_name" :label="row.original.retention_period_name" variant="subtle" />
        <span v-else class="text-muted">—</span>
      </template>
      <template #note-cell="{ row }">
        <span v-if="row.original.note" class="text-sm line-clamp-1">{{ row.original.note }}</span>
        <span v-else class="text-muted">—</span>
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
        <UFormField :label="LABELS.department_name">
          <USelectMenu
            v-model="state.department_id"
            value-key="value"
            :items="departmentItems"
            :search-input="{ placeholder: 'Qidirish...' }"
            :placeholder="`${LABELS.department_name}ni tanlang`"
            icon="i-lucide-building"
            size="lg"
            class="w-full"
          />
          <template #help>
            <span v-if="selectedDepartment">
              {{ LABELS.department_index_code }}:
              <span class="font-mono text-highlighted">{{ selectedDepartment.index_code || '—' }}</span>
            </span>
          </template>
        </UFormField>
        <UFormField :label="LABELS.index_code" required>
          <UInput v-model="state.index_code" placeholder="01-15" icon="i-lucide-hash" size="lg" class="w-full" />
        </UFormField>
        <UFormField :label="LABELS.title" required>
          <UInput v-model="state.title" :placeholder="LABELS.title" size="lg" class="w-full" />
        </UFormField>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <UFormField :label="LABELS.article_number">
            <UInput v-model="state.article_number" :placeholder="LABELS.article_number" icon="i-lucide-list-ordered" size="lg" class="w-full" />
          </UFormField>
          <UFormField :label="LABELS.list_number">
            <UInput v-model="state.list_number" :placeholder="LABELS.list_number" icon="i-lucide-hash" size="lg" class="w-full" />
          </UFormField>
        </div>
        <UFormField :label="LABELS.retention_period">
          <USelectMenu
            v-model="state.retention_period_id"
            value-key="value"
            :items="retentionItems"
            :search-input="{ placeholder: 'Qidirish...' }"
            placeholder="Saqlash muddatini tanlang"
            icon="i-lucide-clock"
            size="lg"
            class="w-full"
          />
        </UFormField>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <UFormField :label="LABELS.start_date">
            <DatePicker v-model="state.start_date" size="lg" />
          </UFormField>
          <UFormField :label="LABELS.end_date">
            <DatePicker v-model="state.end_date" size="lg" :min-date="state.start_date || undefined" />
          </UFormField>
        </div>
        <UFormField :label="LABELS.total_sheets">
          <UInput v-model="state.total_sheets" type="number" :min="0" icon="i-lucide-layers" size="lg" class="w-full" :placeholder="LABELS.total_sheets" />
          <template #help>
            <span v-if="editing" class="inline-flex items-center gap-2">
              Avtomatik summa (hujjatlar varaqlari): <span class="font-semibold text-highlighted">{{ autoPagesSum }}</span>
              <UButton
                v-if="autoPagesSum"
                label="Qo'llash"
                size="xs"
                variant="link"
                class="p-0"
                @click="state.total_sheets = autoPagesSum"
              />
            </span>
          </template>
        </UFormField>
        <UFormField :label="LABELS.archive_folder_note">
          <UTextarea v-model="state.note" :rows="3" :placeholder="LABELS.archive_folder_note" class="w-full" />
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
