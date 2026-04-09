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
const yearItems = computed(() => years.value.map(y => ({ label: String(y.value), value: y.id })))
const schema = z.object({
  name: z.string().min(1, 'Nom kiritilishi shart'),
  description: z.string().optional(),
  sort_order: z.coerce.number().default(0),
  year_id: z.number({ required_error: 'Yil tanlanishi shart' }),
})

const state = reactive({
  name: '',
  description: '',
  sort_order: 0,
  year_id: undefined as number | undefined,
})

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
              label="Yil"
              name="year_id"
              required
            >
              <USelect
                v-model="state.year_id"
                :items="yearItems"
                placeholder="Yilni tanlang"
                icon="i-lucide-calendar"
                size="lg"
                class="w-full"
              />
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