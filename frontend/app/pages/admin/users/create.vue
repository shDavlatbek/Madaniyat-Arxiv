<script setup lang="ts">
import { z } from 'zod'
import type { DepartmentResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const route = useRoute()
const { apiFetch } = useApi()
const { list: listDepartments } = useDepartments()
const { listSchools } = useMusicSchool()
const toast = useToast()
const loading = ref(false)

// Departments for the Bo'lim select
const { data: departmentsData } = await useAsyncData('users-create-departments', () =>
  listDepartments({ activeOnly: true }),
)
const departmentItems = computed(() =>
  (departmentsData.value?.items || []).map(d => ({ label: d.name, value: d.id })),
)

// Music schools for the Musiqa maktabi select
const { data: schoolsData } = await useAsyncData('users-create-schools', () =>
  listSchools(),
)
const schoolItems = computed(() =>
  (schoolsData.value?.items || []).map(s => ({ label: s.name, value: s.id })),
)

const schema = z.object({
  username: z.string().min(2, 'Kamida 2 belgi'),
  name: z.string().min(1, 'Ism kiritilishi shart'),
  password: z.string().min(4, 'Kamida 4 belgi'),
  role: z.string(),
  email: z.string().email().optional().or(z.literal('')),
  is_active: z.boolean(),
  department_id: z.string().optional(),
  music_school_id: z.string().optional(),
})

const state = reactive({
  username: '',
  name: '',
  password: '',
  role: 'user',
  email: '',
  is_active: true,
  // Pre-select department when arriving from a Bo'lim card ("Xodim qo'shish")
  department_id: (route.query.department_id as string) || undefined,
  music_school_id: undefined as string | undefined,
})

const roleOptions = ['admin', 'user', 'viewer', 'music_school']

async function handleSubmit() {
  if (state.role === 'music_school' && !state.music_school_id) {
    toast.add({ title: 'Xatolik', description: 'Musiqa maktabini tanlash shart', color: 'error', icon: 'i-lucide-alert-circle' })
    return
  }
  loading.value = true
  try {
    await apiFetch('/api/users', {
      method: 'POST',
      body: { 
        ...state, 
        department_id: state.role !== 'music_school' ? (state.department_id || null) : null,
        music_school_id: state.role === 'music_school' ? (state.music_school_id || null) : null
      },
    })
    toast.add({ title: 'Muvaffaqiyat', description: 'Foydalanuvchi yaratildi', color: 'success', icon: 'i-lucide-check-circle' })
    navigateTo('/admin/users')
  } catch (error: any) {
    toast.add({ title: 'Xatolik', description: error?.data?.detail || 'Yaratib bo\'lmadi', color: 'error', icon: 'i-lucide-alert-circle' })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <PagePanel title="Yangi foydalanuvchi" icon="i-lucide-user-plus">
    <template #headerLeft>
      <UButton icon="i-lucide-arrow-left" variant="ghost" to="/admin/users" />
    </template>
    <div class="max-w-2xl mx-auto p-6 sm:p-8">
      <UCard>
        <UForm :schema="schema" :state="state" class="space-y-5" @submit="handleSubmit">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
            <UFormField label="Login" name="username" required>
              <UInput v-model="state.username" icon="i-lucide-user" placeholder="admin" size="lg" />
            </UFormField>
            <UFormField label="Ism" name="name" required>
              <UInput v-model="state.name" icon="i-lucide-id-card" placeholder="To'liq ism" size="lg" />
            </UFormField>
            <UFormField label="Parol" name="password" required>
              <UInput v-model="state.password" type="password" icon="i-lucide-lock" size="lg" />
            </UFormField>
            <UFormField label="Email" name="email">
              <UInput v-model="state.email" type="email" icon="i-lucide-mail" placeholder="email@example.com" size="lg" />
            </UFormField>
            <UFormField label="Rol" name="role">
              <USelect v-model="state.role" :items="roleOptions" size="lg" />
            </UFormField>
            <UFormField v-if="state.role !== 'music_school'" :label="LABELS.department" name="department_id">
              <USelectMenu
                v-model="state.department_id"
                value-key="value"
                :items="departmentItems"
                :search-input="{ placeholder: 'Qidirish...' }"
                placeholder="Bo'limni tanlang"
                icon="i-lucide-building-2"
                size="lg"
                class="w-full"
              />
            </UFormField>
            <UFormField v-else :label="LABELS.music_school" name="music_school_id" required>
              <USelectMenu
                v-model="state.music_school_id"
                value-key="value"
                :items="schoolItems"
                :search-input="{ placeholder: 'Qidirish...' }"
                placeholder="Musiqa maktabini tanlang"
                icon="i-lucide-school"
                size="lg"
                class="w-full"
              />
            </UFormField>
            <UFormField label="Holat" name="is_active">
              <div class="flex items-center gap-2 pt-1">
                <USwitch v-model="state.is_active" />
                <span class="text-sm text-muted">{{ state.is_active ? 'Faol' : 'Nofaol' }}</span>
              </div>
            </UFormField>
          </div>
          <div class="flex justify-end gap-3 pt-4 border-t border-default">
            <UButton variant="outline" label="Bekor qilish" to="/admin/users" />
            <UButton type="submit" label="Yaratish" icon="i-lucide-save" :loading="loading" />
          </div>
        </UForm>
      </UCard>
    </div>
  </PagePanel>
</template>

