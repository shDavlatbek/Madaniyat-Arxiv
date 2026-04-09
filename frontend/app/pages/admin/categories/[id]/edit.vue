<script setup lang="ts">
import { z } from 'zod'
import type { CategoryResponse, YearResponse } from '~/types'

definePageMeta({ layout: 'dashboard' })

const route = useRoute()
const catId = computed(() => route.params.id as string)
const { apiFetch } = useApi()
const toast = useToast()
const loading = ref(false)

const { data: category } = await useAsyncData(`cat-edit-${catId.value}`, () => {
  return apiFetch<{ items: CategoryResponse[] }>('/api/categories').then(
    res => res.items.find(c => c.id === catId.value) || null,
  )
})

const { data: yearsData } = await useAsyncData('years-for-cat', () =>
  apiFetch<{ items: YearResponse[] }>('/api/years?active_only=false'),
)
const years = computed(() => yearsData.value?.items || [])
const yearItems = computed(() => years.value.map(y => ({ label: String(y.value), value: y.id })))
const schema = z.object({
  name: z.string().min(1, 'Nom kiritilishi shart'),
  description: z.string().optional(),
  sort_order: z.coerce.number(),
  year_id: z.number({ required_error: 'Yil tanlanishi shart' }),
})

const state = reactive({
  name: category.value?.name || '',
  description: category.value?.description || '',
  sort_order: category.value?.sort_order || 0,
  year_id: category.value?.year_id || undefined as number | undefined,
})

// Track dirty state
const initialState = JSON.stringify(state)
const isDirty = computed(() => JSON.stringify(state) !== initialState)

async function handleSubmit() {
  loading.value = true
  try {
    await apiFetch(`/api/categories/${catId.value}`, { method: 'PUT', body: state })
    toast.add({
      title: 'Muvaffaqiyat',
      description: 'Nomenklatura yangilandi',
      color: 'success',
      icon: 'i-lucide-check-circle',
    })
    navigateTo('/admin/categories')
  }
  catch (error: any) {
    toast.add({
      title: 'Xatolik',
      description: error?.data?.detail || 'Yangilab bo\'lmadi',
      color: 'error',
      icon: 'i-lucide-alert-circle',
    })
  }
  finally {
    loading.value = false
  }
}

function formatDate(date?: string | null) {
  if (!date) return '—'
  return new Date(date).toLocaleDateString('uz-UZ', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}
</script>

<template>
  <PagePanel :title="`Tahrirlash: ${category?.name || ''}`" icon="i-lucide-folder-pen">
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
      <div class="flex items-start justify-between gap-4">
        <div class="flex items-start gap-4 min-w-0">
          <div class="flex items-center justify-center w-14 h-14 rounded-2xl bg-primary-50 dark:bg-primary-950 ring-1 ring-primary-200 dark:ring-primary-900 shrink-0">
            <UIcon name="i-lucide-folder-pen" class="w-7 h-7 text-primary-600 dark:text-primary-400" />
          </div>
          <div class="min-w-0">
            <h1 class="text-2xl font-semibold text-highlighted truncate">
              {{ category?.name || 'Nomenklatura' }}
            </h1>
            <p class="text-sm text-muted mt-1">
              Nomenklatura ma'lumotlarini yangilang va saqlang.
            </p>
          </div>
        </div>

        <UBadge
          v-if="isDirty"
          label="O'zgartirildi"
          variant="subtle"
          color="warning"
          icon="i-lucide-circle-dot"
          size="sm"
          class="shrink-0"
        />
      </div>

      <!-- Meta info strip -->
      <div
        v-if="category"
        class="flex flex-wrap items-center gap-x-6 gap-y-2 px-4 py-3 rounded-xl bg-elevated/40 border border-default text-xs"
      >
        <div class="flex items-center gap-2">
          <UIcon name="i-lucide-fingerprint" class="w-3.5 h-3.5 text-muted" />
          <span class="text-muted">ID:</span>
          <span class="font-mono text-highlighted">{{ catId.slice(0, 8) }}</span>
        </div>
        <div v-if="category.created_at" class="flex items-center gap-2">
          <UIcon name="i-lucide-calendar-plus" class="w-3.5 h-3.5 text-muted" />
          <span class="text-muted">Yaratilgan:</span>
          <span class="text-highlighted">{{ formatDate(category.created_at) }}</span>
        </div>
        <div v-if="category.updated_at" class="flex items-center gap-2">
          <UIcon name="i-lucide-calendar-clock" class="w-3.5 h-3.5 text-muted" />
          <span class="text-muted">Yangilangan:</span>
          <span class="text-highlighted">{{ formatDate(category.updated_at) }}</span>
        </div>
      </div>

      <UForm
        :schema="schema"
        :state="state"
        class="space-y-6"
        @submit="handleSubmit"
      >
        <!-- Main info card -->
        <UCard :ui="{ header: 'border-b border-default', body: 'space-y-5' }">
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
                icon="i-lucide-folder"
                placeholder="Buyruqlar"
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
        <div class="flex items-center justify-between gap-3 p-4 rounded-xl bg-elevated/50 border border-default backdrop-blur sticky bottom-4 z-10">
          <p v-if="isDirty" class="text-xs text-muted hidden sm:flex items-center gap-1.5">
            <UIcon name="i-lucide-info" class="w-3.5 h-3.5" />
            Saqlanmagan o'zgarishlar mavjud
          </p>
          <span v-else class="hidden sm:block" />

          <div class="flex items-center gap-3 ml-auto">
            <UButton
              variant="ghost"
              color="neutral"
              label="Bekor qilish"
              to="/admin/categories"
              :disabled="loading"
            />
            <UButton
              type="submit"
              label="O'zgarishlarni saqlash"
              icon="i-lucide-save"
              :loading="loading"
              :disabled="!isDirty"
            />
          </div>
        </div>
      </UForm>
    </div>
  </PagePanel>
</template>