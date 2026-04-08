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
  <div class="relative min-h-screen w-full overflow-hidden">
    <!-- Gray logo background layer (full screen, behind everything) -->
    <div
      class="absolute inset-0 bg-no-repeat pointer-events-none"
      :style="{
        backgroundImage: `url(${logoGray})`,
        backgroundSize: 'contain',
        backgroundPosition: '60%',
        opacity: 0.2,
      }"
    />

    <div class="relative z-10 grid grid-cols-1 lg:grid-cols-2 min-h-screen">
      <!-- Left: Branding card -->
      <div class="hidden lg:flex items-center justify-center min-h-screen p-4">
        <div class="relative w-full rounded-3xl overflow-hidden shadow-none" style="height: calc(100vh - 80px);">
          <!-- Blurred background image -->
          <div
            class="absolute inset-0 bg-no-repeat bg-cover"
            :style="{
              backgroundImage: `url(${background})`,
              backgroundPosition: '60%',
              opacity: 0.9,
              filter: 'blur(2px)',
            }"
          />
          <!-- Optional dark tint for legibility -->
          <div class="absolute inset-0 bg-madaniyat-800/40" />

          <!-- Content -->
          <div class="relative z-10 h-full flex flex-col px-3 py-6 text-center">
            <!-- Top: logo + title row (4/8 split) -->
            <div class="flex-grow grid grid-cols-12 items-center">
              <div class="col-span-4 flex justify-center items-center">
                <img :src="logoNoText" alt="icon" class="pb-2" style="height: 200px;" />
              </div>
              <div class="col-span-8 flex justify-start items-center">
                <h2 class="text-3xl font-extrabold text-white text-left uppercase mb-0 leading-tight">
                  O'zbekiston Respublikasi Madaniyat vazirligi
                </h2>
              </div>
            </div>

            <!-- Bottom: madh logo + label -->
            <div class="mt-auto flex justify-center items-center">
              <img
                :src="logoMadh"
                alt="icon"
                class="pb-2"
                style="filter: brightness(0) invert(1); height: 40px;"
              />
              <h2 class="text-xl font-extrabold text-white uppercase mb-0 ml-2">Madaniy hayot</h2>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Login form -->
      <div class="flex items-center justify-center min-h-screen p-4">
        <div class="w-full max-w-md px-4">
          <h2 class="text-3xl font-extrabold text-highlighted mb-1">Madaniyat vazirligi Arxiv tizimi</h2>
          <p class="text-muted mb-10">O'zbekiston Respublikasi Madaniyat vazirligi Arxiv tizimi</p>

          <UForm :schema="schema" :state="state" class="space-y-5" @submit="handleLogin">
            <UFormField label="Foydalanuvchi nomi" name="username" required>
              <UInput
                v-model="state.username"
                icon="i-lucide-user"
                placeholder="admin"
                size="lg"
                class="w-full"
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
                class="w-full"
              />
            </UFormField>

            <UButton
              type="submit"
              label="Tizimga kirish"
              icon="i-lucide-log-in"
              size="lg"
              block
              :loading="loading"
              class="mt-2 py-3"
            />
          </UForm>
        </div>
      </div>
    </div>
  </div>
</template>