<script setup lang="ts">
import type { DepartmentResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const { apiFetch } = useApi()
const { create, update, remove, activate, deactivate } = useDepartments()
const toast = useToast()

const { data: departmentsData, status, refresh } = await useAsyncData('admin-departments', () =>
  apiFetch<{ items: DepartmentResponse[] }>('/api/departments'),
)
const departments = computed(() => departmentsData.value?.items || [])

const breadcrumbItems = [
  { label: 'Arxivist', icon: 'i-lucide-archive', to: '/archive' },
  { label: LABELS.departments, icon: 'i-lucide-building-2' },
]

// Create / edit modal
const modalOpen = ref(false)
const editing = ref<DepartmentResponse | null>(null)
const state = reactive({ name: '', index_code: '', description: '' })
const saving = ref(false)

function openCreate() {
  editing.value = null
  state.name = ''
  state.index_code = ''
  state.description = ''
  modalOpen.value = true
}

function openEdit(department: DepartmentResponse) {
  editing.value = department
  state.name = department.name
  state.index_code = department.index_code || ''
  state.description = department.description || ''
  modalOpen.value = true
}

async function handleSave() {
  if (!state.name.trim()) return
  saving.value = true
  try {
    const payload = {
      name: state.name.trim(),
      index_code: state.index_code.trim() || null,
      description: state.description.trim() || null,
    }
    if (editing.value) {
      await update(editing.value.id, payload)
      toast.add({ title: 'Muvaffaqiyat', description: "Bo'lim yangilandi", color: 'success', icon: 'i-lucide-check-circle' })
    } else {
      await create(payload)
      toast.add({ title: 'Muvaffaqiyat', description: "Bo'lim qo'shildi", color: 'success', icon: 'i-lucide-check-circle' })
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
const deleteTarget = ref<DepartmentResponse | null>(null)

function openDelete(department: DepartmentResponse) {
  deleteTarget.value = department
  deleteOpen.value = true
}

async function handleDelete() {
  if (!deleteTarget.value) return
  try {
    await remove(deleteTarget.value.id)
    toast.add({ title: 'Muvaffaqiyat', description: "Bo'lim o'chirildi", color: 'success', icon: 'i-lucide-check-circle' })
    deleteOpen.value = false
    refresh()
  } catch (error: any) {
    toast.add({ title: 'Xatolik', description: error?.data?.detail || "O'chirib bo'lmadi", color: 'error', icon: 'i-lucide-alert-circle' })
  }
}

async function toggleActive(department: DepartmentResponse) {
  try {
    if (department.is_active) {
      await deactivate(department.id)
      toast.add({ title: 'Bajarildi', description: "Bo'lim nofaol qilindi", color: 'success', icon: 'i-lucide-check-circle' })
    } else {
      await activate(department.id)
      toast.add({ title: 'Bajarildi', description: "Bo'lim faollashtirildi", color: 'success', icon: 'i-lucide-check-circle' })
    }
    refresh()
  } catch (error: any) {
    toast.add({ title: 'Xatolik', description: error?.data?.detail || 'Xatolik yuz berdi', color: 'error', icon: 'i-lucide-alert-circle' })
  }
}
</script>

<template>
  <PagePanel :title="LABELS.departments" icon="i-lucide-building-2">
    <template #headerRight>
      <UBadge :label="`${departments.length} ${LABELS.department.toLowerCase()}`" variant="subtle" class="mr-2" />
      <UButton icon="i-lucide-plus" :label="LABELS.add_department" @click="openCreate" />
    </template>

    <div class="p-5">
      <UBreadcrumb :items="breadcrumbItems" class="mb-5" />

      <div
        v-if="departments.length"
        class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
      >
        <div
          v-for="department in departments"
          :key="department.id"
          class="group relative flex flex-col rounded-xl border border-default bg-elevated/30 p-4 transition-colors hover:border-primary/40"
          :class="{ 'opacity-60': !department.is_active }"
        >
          <div class="flex items-start gap-2">
            <UIcon name="i-lucide-building-2" class="mt-0.5 shrink-0 text-primary" />
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-2">
                <h3 class="font-semibold leading-snug text-highlighted truncate">{{ department.name }}</h3>
                <UBadge v-if="department.index_code" :label="department.index_code" variant="subtle" size="xs" />
              </div>
              <p v-if="department.description" class="mt-1 text-sm text-muted line-clamp-2">
                {{ department.description }}
              </p>
            </div>
          </div>

          <div class="mt-4 flex items-center justify-between">
            <UBadge
              :label="department.is_active ? LABELS.active : LABELS.inactive"
              :color="department.is_active ? 'success' : 'neutral'"
              variant="subtle"
              size="sm"
            />
            <div class="flex items-center gap-1">
              <UTooltip :text="LABELS.add_user_to_department">
                <UButton
                  icon="i-lucide-user-plus"
                  variant="ghost"
                  size="xs"
                  :to="`/admin/users/create?department_id=${department.id}`"
                />
              </UTooltip>
              <UTooltip :text="department.is_active ? LABELS.inactive : LABELS.active">
                <UButton
                  :icon="department.is_active ? 'i-lucide-toggle-right' : 'i-lucide-toggle-left'"
                  variant="ghost"
                  size="xs"
                  @click="toggleActive(department)"
                />
              </UTooltip>
              <UTooltip :text="LABELS.edit_department">
                <UButton icon="i-lucide-pencil" variant="ghost" size="xs" @click="openEdit(department)" />
              </UTooltip>
              <UTooltip :text="LABELS.delete_department">
                <UButton icon="i-lucide-trash-2" variant="ghost" size="xs" color="error" @click="openDelete(department)" />
              </UTooltip>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="status !== 'pending'" class="flex items-center justify-center p-12">
        <EmptyState
          icon="i-lucide-building-2"
          :title="`${LABELS.departments} topilmadi`"
          description="Hali bo'limlar qo'shilmagan"
        />
      </div>
    </div>
  </PagePanel>

  <!-- Create / edit modal -->
  <UModal v-model:open="modalOpen" :title="editing ? LABELS.edit_department : LABELS.add_department">
    <template #body>
      <div class="space-y-5">
        <UFormField :label="LABELS.department_name" required>
          <UInput
            v-model="state.name"
            placeholder="Bo'lim nomi"
            icon="i-lucide-building-2"
            size="lg"
            class="w-full"
            @keydown.enter="handleSave"
          />
        </UFormField>
        <UFormField :label="LABELS.department_index_code" help="Masalan: 01">
          <UInput
            v-model="state.index_code"
            placeholder="01"
            icon="i-lucide-hash"
            size="lg"
            class="w-full"
          />
        </UFormField>
        <UFormField :label="LABELS.department_description">
          <UTextarea
            v-model="state.description"
            placeholder="Ixtiyoriy tavsif"
            :rows="3"
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
          :disabled="!state.name.trim()"
          @click="handleSave"
        />
      </div>
    </template>
  </UModal>

  <!-- Delete confirmation -->
  <UModal
    v-model:open="deleteOpen"
    :title="LABELS.delete_department"
    :description="deleteTarget ? `«${deleteTarget.name}» bo'limi o'chiriladi. Bu amalni qaytarib bo'lmaydi.` : ''"
  >
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton variant="ghost" label="Bekor qilish" @click="deleteOpen = false" />
        <UButton color="error" label="O'chirish" icon="i-lucide-trash-2" @click="handleDelete" />
      </div>
    </template>
  </UModal>
</template>
