<script setup lang="ts">
import type { UserResponse, PaginatedResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const { apiFetch } = useApi()
const toast = useToast()

const search = ref('')
const page = ref(1)
const deleteOpen = ref(false)
const deleteTarget = ref<UserResponse | null>(null)

const { data, status, refresh } = await useAsyncData('admin-users', () => {
  const params = new URLSearchParams()
  params.set('page', String(page.value))
  if (search.value) params.set('search', search.value)
  return apiFetch<PaginatedResponse<UserResponse>>(`/api/users?${params}`)
}, { watch: [search, page] })

const users = computed(() => data.value?.items || [])
const total = computed(() => data.value?.total || 0)

const columns = [
  { accessorKey: 'username', header: 'Login' },
  { accessorKey: 'name', header: 'Ism' },
  { accessorKey: 'role', header: 'Rol' },
  { accessorKey: 'is_active', header: 'Holat' },
  { id: 'actions', header: '' },
]

function confirmDelete(user: UserResponse) {
  deleteTarget.value = user
  deleteOpen.value = true
}

async function handleDelete() {
  if (!deleteTarget.value) return
  try {
    await apiFetch(`/api/users/${deleteTarget.value.id}`, { method: 'DELETE' })
    toast.add({ title: 'Muvaffaqiyat', description: 'Foydalanuvchi o\'chirildi', color: 'success', icon: 'i-lucide-check-circle' })
    deleteOpen.value = false
    refresh()
  } catch {
    toast.add({ title: 'Xatolik', description: 'O\'chirib bo\'lmadi', color: 'error', icon: 'i-lucide-alert-circle' })
  }
}
</script>

<template>
  <PagePanel title="Foydalanuvchilar">
    <template #headerRight>
      <UButton icon="i-lucide-plus" label="Yangi foydalanuvchi" to="/admin/users/create" />
    </template>
    <template #toolbar>
      <UInput v-model="search" icon="i-lucide-search" placeholder="Qidirish..." class="w-64" />
    </template>
    <UTable :data="users" :columns="columns" :loading="status === 'pending'">
      <template #is_active-cell="{ row }">
        <UBadge :label="row.is_active ? 'Faol' : 'Nofaol'" :color="row.is_active ? 'success' : 'error'" variant="subtle" />
      </template>
      <template #role-cell="{ row }">
        <UBadge :label="row.role" variant="subtle" />
      </template>
      <template #actions-cell="{ row }">
        <UDropdownMenu :items="[
          [{ label: 'Tahrirlash', icon: 'i-lucide-pencil', onSelect: () => navigateTo(`/admin/users/${row.id}/edit`) }],
          [{ label: 'O\'chirish', icon: 'i-lucide-trash-2', color: 'error', onSelect: () => confirmDelete(row) }],
        ]">
          <UButton icon="i-lucide-ellipsis-vertical" variant="ghost" size="xs" />
        </UDropdownMenu>
      </template>
    </UTable>
    <div v-if="total > 20" class="flex justify-center p-4">
      <UPagination v-model:page="page" :total="total" :items-per-page="20" />
    </div>
  </PagePanel>

  <UModal v-model:open="deleteOpen" title="Foydalanuvchini o'chirish" description="Bu amalni qaytarib bo'lmaydi.">
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton variant="ghost" label="Bekor qilish" @click="deleteOpen = false" />
        <UButton color="error" label="O'chirish" icon="i-lucide-trash-2" @click="handleDelete" />
      </div>
    </template>
  </UModal>
</template>
