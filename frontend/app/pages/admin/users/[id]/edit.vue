<script setup lang="ts">
import { z } from 'zod'
import type { UserResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const route = useRoute()
const userId = computed(() => route.params.id as string)
const { apiFetch } = useApi()
const toast = useToast()
const loading = ref(false)

const { data: user } = await useAsyncData(`user-${userId.value}`, () =>
  apiFetch<UserResponse>(`/api/users/${userId.value}`)
)

const schema = z.object({
  name: z.string().min(1),
  email: z.string().email().optional().or(z.literal('')),
  role: z.string(),
  is_active: z.boolean(),
})

const state = reactive({
  name: user.value?.name || '',
  email: user.value?.email || '',
  role: user.value?.role || 'user',
  is_active: user.value?.is_active ?? true,
})

const newPassword = ref('')
const roleOptions = ['admin', 'user', 'viewer']

async function handleSubmit() {
  loading.value = true
  try {
    await apiFetch(`/api/users/${userId.value}`, { method: 'PUT', body: state })
    toast.add({ title: 'Muvaffaqiyat', description: 'Foydalanuvchi yangilandi', color: 'success', icon: 'i-lucide-check-circle' })
    navigateTo('/admin/users')
  } catch (error: any) {
    toast.add({ title: 'Xatolik', description: error?.data?.detail || 'Yangilab bo\'lmadi', color: 'error', icon: 'i-lucide-alert-circle' })
  } finally {
    loading.value = false
  }
}

async function changePassword() {
  if (!newPassword.value || newPassword.value.length < 4) {
    toast.add({ title: 'Xatolik', description: 'Parol kamida 4 belgi bo\'lishi kerak', color: 'error', icon: 'i-lucide-alert-circle' })
    return
  }
  try {
    await apiFetch(`/api/users/${userId.value}/password`, { method: 'PUT', body: { new_password: newPassword.value } })
    toast.add({ title: 'Muvaffaqiyat', description: 'Parol o\'zgartirildi', color: 'success', icon: 'i-lucide-check-circle' })
    newPassword.value = ''
  } catch {
    toast.add({ title: 'Xatolik', description: 'Parolni o\'zgartirib bo\'lmadi', color: 'error', icon: 'i-lucide-alert-circle' })
  }
}
</script>

<template>
  <PagePanel :title="`Tahrirlash: ${user?.username}`" icon="i-lucide-user-pen">
    <template #headerLeft>
      <UButton icon="i-lucide-arrow-left" variant="ghost" to="/admin/users" />
    </template>
    <div class="max-w-2xl mx-auto p-6 sm:p-8 space-y-6">
      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-lucide-id-card" class="text-primary" />
            <span class="font-semibold">Asosiy ma'lumotlar</span>
          </div>
        </template>
        <UForm :schema="schema" :state="state" class="space-y-5" @submit="handleSubmit">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
            <UFormField label="Ism" name="name" required>
              <UInput v-model="state.name" icon="i-lucide-id-card" size="lg" />
            </UFormField>
            <UFormField label="Email" name="email">
              <UInput v-model="state.email" type="email" icon="i-lucide-mail" size="lg" />
            </UFormField>
            <UFormField label="Rol" name="role">
              <USelect v-model="state.role" :items="roleOptions" size="lg" />
            </UFormField>
            <UFormField label="Holat" name="is_active">
              <div class="flex items-center gap-2 pt-1">
                <USwitch v-model="state.is_active" />
                <span class="text-sm text-muted">{{ state.is_active ? 'Faol' : 'Nofaol' }}</span>
              </div>
            </UFormField>
          </div>
          <div class="flex justify-end pt-4 border-t border-default">
            <UButton type="submit" label="Saqlash" icon="i-lucide-save" :loading="loading" />
          </div>
        </UForm>
      </UCard>

      <UCard>
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon name="i-lucide-key" class="text-primary" />
            <span class="font-semibold">Parolni o'zgartirish</span>
          </div>
        </template>
        <div class="flex gap-3">
          <UInput v-model="newPassword" type="password" placeholder="Yangi parol" class="flex-1" size="lg" />
          <UButton label="O'zgartirish" icon="i-lucide-key" @click="changePassword" />
        </div>
      </UCard>
    </div>
  </PagePanel>
</template>
