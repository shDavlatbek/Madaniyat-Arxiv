<script setup lang="ts">
import { z } from 'zod'
import logoNoText from '~/assets/images/logos/logo-no-text.svg'
import logoMadh from '~/assets/images/logos/logo-madh.svg'
import logoGray from '~/assets/images/logos/logo-gray.svg'
import background from '~/assets/images/backgrounds/employees-in-office.jpg'

definePageMeta({ layout: 'auth' })

const { login } = useAuth()
const toast = useToast()
const loading = ref(false)

const schema = z.object({
  username: z.string().min(1, 'Foydalanuvchi nomini kiriting'),
  password: z.string().min(1, 'Parolni kiriting'),
})

type LoginForm = z.output<typeof schema>
const state = reactive<Partial<LoginForm>>({ username: '', password: '' })

async function handleLogin() {
  loading.value = true
  try {
    await login(state.username!, state.password!)
    navigateTo('/archive')
  } catch (error: any) {
    toast.add({
      title: 'Xatolik',
      description: error?.data?.detail || "Noto'g'ri foydalanuvchi nomi yoki parol",
      color: 'error',
      icon: 'i-lucide-alert-circle',
    })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex">
    <!-- Left: Branding panel -->
    <div class="hidden lg:flex lg:w-1/2 relative items-center justify-center overflow-hidden">
      <img
        :src="logoGray"
        alt=""
        class="absolute inset-0 w-full h-full object-contain opacity-5"
      />
      <img
        :src="background"
        alt=""
        class="absolute inset-0 w-full h-full object-cover"
      />
      <div class="absolute inset-0 bg-madaniyat-800/70" />

      <div class="relative z-10 flex flex-col items-center justify-center h-full p-8 text-center">
        <div class="flex items-center gap-6 mb-8">
          <img :src="logoNoText" alt="Logo" class="h-36 drop-shadow-lg" />
          <h1 class="text-3xl font-bold text-white text-left uppercase leading-tight">
            O'zbekiston<br />Respublikasi<br />Madaniyat<br />vazirligi
          </h1>
        </div>

        <div class="mt-auto flex items-center gap-2 opacity-80">
          <img :src="logoMadh" alt="" class="h-8 brightness-0 invert" />
          <span class="text-white font-semibold uppercase text-sm">Madaniy hayot</span>
        </div>
      </div>
    </div>

    <!-- Right: Login form -->
    <div class="w-full lg:w-1/2 flex items-center justify-center p-6 sm:p-8 bg-default">
      <div class="w-full max-w-md">
        <div class="flex items-center gap-3 mb-2 lg:hidden">
          <img :src="logoNoText" alt="Logo" class="h-10" />
        </div>
        <h2 class="text-2xl font-bold text-highlighted mb-1">Arxiv tizimi</h2>
        <p class="text-muted mb-8">Madaniyat vazirligi hujjat arxivi tizimiga kirish</p>

        <UForm :schema="schema" :state="state" class="space-y-5" @submit="handleLogin">
          <UFormField label="Foydalanuvchi nomi" name="username" required>
            <UInput
              v-model="state.username"
              icon="i-lucide-user"
              placeholder="admin"
              size="lg"
              autofocus
            />
          </UFormField>

          <UFormField label="Parol" name="password" required>
            <UInput
              v-model="state.password"
              type="password"
              icon="i-lucide-lock"
              placeholder="Parolni kiriting"
              size="lg"
            />
          </UFormField>

          <UButton
            type="submit"
            label="Tizimga kirish"
            icon="i-lucide-log-in"
            size="lg"
            block
            :loading="loading"
            class="mt-2"
          />
        </UForm>
      </div>
    </div>
  </div>
</template>
