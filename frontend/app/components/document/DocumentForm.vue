<script setup lang="ts">
import { z } from 'zod'
import type { CategoryFieldResponse, DocumentResponse } from '~/types'
import { buildFieldSchema } from '~/utils/buildFieldSchema'

const props = defineProps<{
  categoryId: string
  initialData?: DocumentResponse | null
}>()

const emit = defineEmits<{
  submit: [data: Record<string, any>]
}>()

const { apiFetch } = useApi()
const loading = ref(false)

// Fetch category fields
const { data: fields } = await useAsyncData(
  `fields-${props.categoryId}`,
  () => apiFetch<CategoryFieldResponse[]>(`/api/categories/${props.categoryId}/fields`)
)

// Build base schema
const baseSchema = z.object({
  title: z.string().min(1, 'Sarlavha kiritilishi shart'),
  document_number: z.string().min(1, 'Hujjat raqami kiritilishi shart'),
  date: z.string().min(1, 'Sana kiritilishi shart'),
  short_desc: z.string().optional(),
  target: z.string().optional(),
  pages: z.coerce.number().optional(),
  signer: z.string().optional(),
})

// State
const state = reactive<Record<string, any>>({
  title: props.initialData?.title || '',
  document_number: props.initialData?.document_number || '',
  date: props.initialData?.date || '',
  short_desc: props.initialData?.short_desc || '',
  target: props.initialData?.target || '',
  pages: props.initialData?.pages || undefined,
  signer: props.initialData?.signer || '',
})

// Dynamic field state
const dynamicFields = reactive<Record<string, any>>({})

// Initialize dynamic field values from existing document
if (props.initialData?.field_values && fields.value) {
  for (const fv of props.initialData.field_values) {
    const fieldDef = fields.value.find(f => f.id === fv.category_field_id)
    if (fieldDef) {
      dynamicFields[fieldDef.name] = fv.value
    }
  }
}

async function handleSubmit() {
  loading.value = true
  try {
    emit('submit', {
      ...state,
      dynamic_fields: { ...dynamicFields },
    })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <UForm :schema="baseSchema" :state="state" class="space-y-4" @submit="handleSubmit">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <UFormField label="Sarlavha" name="title" required>
        <UInput v-model="state.title" icon="i-lucide-file-text" placeholder="Hujjat sarlavhasi" />
      </UFormField>

      <UFormField label="Hujjat raqami" name="document_number" required>
        <UInput v-model="state.document_number" icon="i-lucide-hash" placeholder="123 yoki 123-A" />
      </UFormField>

      <UFormField label="Sana" name="date" required>
        <UInput v-model="state.date" type="date" icon="i-lucide-calendar" />
      </UFormField>

      <UFormField label="Imzo qo'ygan shaxs" name="signer">
        <UInput v-model="state.signer" icon="i-lucide-pen-tool" placeholder="F.I.O." />
      </UFormField>

      <UFormField label="Kimga" name="target">
        <UInput v-model="state.target" icon="i-lucide-send" placeholder="Kimga qaratilgan" />
      </UFormField>

      <UFormField label="Sahifalar soni" name="pages">
        <UInput v-model="state.pages" type="number" icon="i-lucide-book-open" />
      </UFormField>
    </div>

    <UFormField label="Qisqacha tavsif" name="short_desc">
      <UTextarea v-model="state.short_desc" :rows="3" placeholder="Hujjat haqida qisqacha..." />
    </UFormField>

    <!-- Dynamic fields -->
    <div v-if="fields?.length" class="border-t border-default pt-4 mt-4">
      <h3 class="text-sm font-semibold text-muted mb-3 flex items-center gap-2">
        <UIcon name="i-lucide-layers" />
        Qo'shimcha maydonlar
      </h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <DocumentFieldRenderer
          v-for="field in fields"
          :key="field.id"
          :field="field"
          v-model="dynamicFields[field.name]"
        />
      </div>
    </div>

    <div class="flex justify-end gap-2 pt-4">
      <UButton variant="ghost" label="Bekor qilish" @click="$router.back()" />
      <UButton type="submit" :label="initialData ? 'Saqlash' : 'Yaratish'" icon="i-lucide-save" :loading="loading" />
    </div>
  </UForm>
</template>
