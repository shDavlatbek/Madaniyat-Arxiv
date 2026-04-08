<script setup lang="ts">
import { z } from 'zod'

definePageMeta({ layout: 'dashboard' })

const { apiFetch } = useApi()
const toast = useToast()
const loading = ref(false)

const schema = z.object({
  username: z.string().min(2, 'Kamida 2 belgi'),
  name: z.string().min(1, 'Ism kiritilishi shart'),
  password: z.string().min(4, 'Kamida 4 belgi'),
  role: z.string(),
  email: z.string().email().optional().or(z.literal('')),
  is_active: z.boolean(),
})

const state = reactive({
  username: '',
  name: '',
  password: '',
  role: 'user',
  email: '',
  is_active: true,
})

const roleOptions = ['admin', 'user', 'viewer']

async function handleSubmit() {
  loading.value = true
  try {
    await apiFetch('/api/users', { method: 'POST', body: state })
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
