<script setup lang="ts">
import { z } from 'zod'
import type { YearResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const { apiFetch } = useApi()
const toast = useToast()
const loading = ref(false)

const { data: yearsData } = await useAsyncData('years-for-cat', () =>
  apiFetch<{ items: YearResponse[] }>('/api/years?active_only=false'),
)
const years = computed(() => yearsData.value?.items || [])
const schema = z.object({
  name: z.string().min(1, 'Nom kiritilishi shart'),
  code: z.string().min(1, 'Kod kiritilishi shart'),
  description: z.string().optional(),
  sort_order: z.coerce.number().default(0),
  year_ids: z.array(z.number()).min(1, 'Kamida bitta yil tanlanishi shart'),
})

const state = reactive({
  name: '',
  code: '',
  description: '',
  sort_order: 0,
  year_ids: [] as number[],
})

// Auto-generate code slug from name
watch(() => state.name, (val) => {
  if (!state.code || state.code === slugify(state.name.slice(0, -1))) {
    state.code = slugify(val)
  }
})

function slugify(str: string) {
  return str
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/\s+/g, '-')
}

async function handleSubmit() {
  loading.value = true
  try {
    await apiFetch('/api/categories', { method: 'POST', body: state })
    toast.add({
      title: 'Muvaffaqiyat',
      description: 'Nomenklatura yaratildi',
      color: 'success',
      icon: 'i-lucide-check-circle',
    })
    navigateTo('/admin/categories')
  }
  catch (error: any) {
    toast.add({
      title: 'Xatolik',
      description: error?.data?.detail || 'Yaratib bo\'lmadi',
      color: 'error',
      icon: 'i-lucide-alert-circle',
    })
  }
  finally {
    loading.value = false
  }
}
</script>

<template>
  <PagePanel title="Yangi nomenklatura" icon="i-lucide-folder-plus">
    <template #headerLeft>
      <UButton
        icon="i-lucide-arrow-left"
        variant="ghost"
        color="neutral"
        to="/admin/categories"
      />
    </template>

    <div class="max-w-3xl mx-auto px-4 sm:px-6 py-8 space-y-6">
      <!-- Hero header -->
      <div class="flex items-start gap-4">
        <div class="flex items-center justify-center w-14 h-14 rounded-2xl bg-primary-50 dark:bg-primary-950 ring-1 ring-primary-200 dark:ring-primary-900">
          <UIcon name="i-lucide-folder-plus" class="w-7 h-7 text-primary-600 dark:text-primary-400" />
        </div>
        <div>
          <h1 class="text-2xl font-semibold text-highlighted">
            Yangi nomenklatura yaratish
          </h1>
          <p class="text-sm text-muted mt-1">
            Nomenklatura ma'lumotlarini kiriting va tegishli yilga biriktiring.
          </p>
        </div>
      </div>

      <UForm
        :schema="schema"
        :state="state"
        class="space-y-6"
        @submit="handleSubmit"
      >
        <!-- Main info card -->
        <UCard
          :ui="{ header: 'border-b border-default', body: 'space-y-5' }"
        >
          <template #header>
            <div class="flex items-center gap-2">
              <UIcon name="i-lucide-info" class="w-4 h-4 text-muted" />
              <h2 class="text-sm font-semibold text-highlighted">
                Asosiy ma'lumotlar
              </h2>
            </div>
          </template>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
            <UFormField
              label="Nomi"
              name="name"
              required
              help="Foydalanuvchilarga ko'rinadigan nom"
            >
              <UInput
                v-model="state.name"
                placeholder="Buyruqlar"
                icon="i-lucide-folder"
                size="lg"
                class="w-full"
              />
            </UFormField>

            <UFormField
              label="Kod"
              name="code"
              required
            >
              <UInput
                v-model="state.code"
                placeholder="buyruqlar"
                icon="i-lucide-hash"
                size="lg"
                class="w-full"
              />
            </UFormField>

            <UFormField
              label="Yillar"
              name="year_ids"
              required
              help="Bir yoki bir nechta yil tanlang"
              class="md:col-span-2"
            >
              <div class="flex flex-wrap gap-2">
                <UButton
                  v-for="year in years"
                  :key="year.id"
                  :label="String(year.value)"
                  :variant="state.year_ids.includes(year.id) ? 'solid' : 'outline'"
                  :color="state.year_ids.includes(year.id) ? 'primary' : 'neutral'"
                  size="sm"
                  @click="state.year_ids.includes(year.id) ? state.year_ids = state.year_ids.filter(id => id !== year.id) : state.year_ids.push(year.id)"
                />
              </div>
            </UFormField>
          </div>

          <UFormField
            label="Tavsif"
            name="description"
            help="Ixtiyoriy — nomenklatura maqsadini qisqacha tushuntiring"
          >
            <UTextarea
              v-model="state.description"
              :rows="4"
              placeholder="Nomenklatura haqida qisqacha ma'lumot..."
              class="w-full"
            />
          </UFormField>
        </UCard>

        <!-- Settings card -->
        <UCard :ui="{ header: 'border-b border-default' }">
          <template #header>
            <div class="flex items-center gap-2">
              <UIcon name="i-lucide-settings-2" class="w-4 h-4 text-muted" />
              <h2 class="text-sm font-semibold text-highlighted">
                Sozlamalar
              </h2>
            </div>
          </template>

          <UFormField
            label="Tartib raqami"
            name="sort_order"
            help="Ro'yxatda ko'rinish tartibi — kichik raqam birinchi chiqadi"
          >
            <UInput
              v-model="state.sort_order"
              type="number"
              icon="i-lucide-arrow-up-down"
              class="w-40"
              size="lg"
            />
          </UFormField>
        </UCard>

        <!-- Sticky action bar -->
        <div class="flex items-center justify-end gap-3 p-4 rounded-xl bg-elevated/50 border border-default backdrop-blur sticky bottom-4">
          <UButton
            variant="ghost"
            color="neutral"
            label="Bekor qilish"
            to="/admin/categories"
            :disabled="loading"
          />
          <UButton
            type="submit"
            label="Nomenklaturani yaratish"
            icon="i-lucide-save"
            size="md"
            :loading="loading"
          />
        </div>
      </UForm>
    </div>
  </PagePanel>
</template>