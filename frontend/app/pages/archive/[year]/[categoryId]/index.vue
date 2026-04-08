<script setup lang="ts">
import type { CategoryFieldResponse, CategoryResponse, DocumentResponse, PaginatedResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const route = useRoute()
const year = computed(() => Number(route.params.year))
const categoryId = computed(() => route.params.categoryId as string)

const { apiFetch } = useApi()
const { listDocuments, deleteDocument } = useDocuments()
const toast = useToast()

const search = ref('')
const page = ref(1)
const deleteOpen = ref(false)
const deleteTarget = ref<DocumentResponse | null>(null)

// Fetch category info
const { data: catData } = await useAsyncData(
  `cat-${categoryId.value}`,
  async () => {
    const cats = await apiFetch<{ items: CategoryResponse[] }>(`/api/years/${year.value}/categories`)
    return cats.items.find(c => c.id === categoryId.value) || null
  }
)

// Fetch documents
const { data: docsData, status, refresh } = await useAsyncData(
  `docs-${categoryId.value}`,
  () => listDocuments({
    year_id: year.value,
    category_id: categoryId.value,
    search: search.value || undefined,
    page: page.value,
  }),
  { watch: [search, page] }
)

const documents = computed(() => docsData.value?.items || [])
const total = computed(() => docsData.value?.total || 0)

const columns = [
  { accessorKey: 'document_number', header: 'Raqam' },
  { accessorKey: 'title', header: 'Sarlavha' },
  { accessorKey: 'date', header: 'Sana' },
  { accessorKey: 'signer', header: 'Imzo' },
  { id: 'actions', header: '' },
]

function confirmDelete(doc: DocumentResponse) {
  deleteTarget.value = doc
  deleteOpen.value = true
}

async function handleDelete() {
  if (!deleteTarget.value) return
  try {
    await deleteDocument(deleteTarget.value.id)
    toast.add({ title: 'Muvaffaqiyat', description: 'Hujjat o\'chirildi', color: 'success', icon: 'i-lucide-check-circle' })
    deleteOpen.value = false
    refresh()
  } catch {
    toast.add({ title: 'Xatolik', description: 'Hujjatni o\'chirib bo\'lmadi', color: 'error', icon: 'i-lucide-alert-circle' })
  }
}
</script>

<template>
  <PagePanel :title="catData?.name || 'Hujjatlar'">
    <template #headerLeft>
      <UButton icon="i-lucide-arrow-left" variant="ghost" :to="`/archive/${year}`" />
    </template>
    <template #headerRight>
      <UButton
        icon="i-lucide-plus"
        label="Yangi hujjat"
        :to="`/archive/${year}/${categoryId}/create`"
      />
    </template>
    <template #toolbar>
      <UInput
        v-model="search"
        icon="i-lucide-search"
        placeholder="Qidirish..."
        class="w-64"
      />
      <div class="ml-auto flex items-center gap-2">
        <UBadge :label="`${total} hujjat`" variant="subtle" />
      </div>
    </template>

    <UTable
      :data="documents"
      :columns="columns"
      :loading="status === 'pending'"
      class="w-full"
    >
      <template #document_number-cell="{ row }">
        <NuxtLink :to="`/archive/${year}/${categoryId}/${row.id}`" class="font-mono text-primary hover:underline">
          {{ row.document_number }}
        </NuxtLink>
      </template>
      <template #title-cell="{ row }">
        <NuxtLink :to="`/archive/${year}/${categoryId}/${row.id}`" class="hover:underline">
          {{ row.title }}
        </NuxtLink>
      </template>
      <template #actions-cell="{ row }">
        <UDropdownMenu :items="[
          [
            { label: 'Ko\'rish', icon: 'i-lucide-eye', onSelect: () => navigateTo(`/archive/${year}/${categoryId}/${row.id}`) },
            { label: 'Tahrirlash', icon: 'i-lucide-pencil', onSelect: () => navigateTo(`/archive/${year}/${categoryId}/${row.id}/edit`) },
          ],
          [
            { label: 'O\'chirish', icon: 'i-lucide-trash-2', color: 'error', onSelect: () => confirmDelete(row) },
          ],
        ]">
          <UButton icon="i-lucide-ellipsis-vertical" variant="ghost" size="xs" />
        </UDropdownMenu>
      </template>
    </UTable>

    <div v-if="total > 20" class="flex justify-center p-4">
      <UPagination v-model:page="page" :total="total" :items-per-page="20" />
    </div>

    <div v-if="!documents.length && status !== 'pending'" class="flex items-center justify-center p-12">
      <EmptyState icon="i-lucide-file-x" title="Hujjatlar topilmadi" description="Bu kategoriyada hujjatlar mavjud emas" />
    </div>
  </PagePanel>

  <!-- Delete confirmation -->
  <UModal v-model:open="deleteOpen" title="Hujjatni o'chirish" description="Haqiqatan ham bu hujjatni o'chirmoqchimisiz? Bu amalni qaytarib bo'lmaydi.">
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton variant="ghost" label="Bekor qilish" @click="deleteOpen = false" />
        <UButton color="error" label="O'chirish" icon="i-lucide-trash-2" @click="handleDelete" />
      </div>
    </template>
  </UModal>
</template>
