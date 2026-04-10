<script setup lang="ts">
const open = defineModel<boolean>('open', { required: true })

const props = defineProps<{
  editing?: boolean
  initialData?: {
    label: string
    field_type: string
    is_required: boolean
    options: string
  }
}>()

const emit = defineEmits<{
  save: [data: { label: string; field_type: string; is_required: boolean; options: string }]
}>()

const fieldTypes = [
  { label: 'Tekst', value: 'text' },
  { label: 'Raqam', value: 'number' },
  { label: 'Sana', value: 'date' },
  { label: 'Katta tekst', value: 'textarea' },
  { label: 'Tanlov', value: 'select' },
  { label: 'Fayl', value: 'file' },
]

const state = reactive({
  label: '',
  field_type: 'text',
  is_required: false,
  options: '',
})

watch(open, (val) => {
  if (val && props.initialData) {
    Object.assign(state, props.initialData)
  } else if (val) {
    Object.assign(state, { label: '', field_type: 'text', is_required: false, options: '' })
  }
})

function handleSave() {
  emit('save', { ...state })
  open.value = false
}
</script>

<template>
  <UModal v-model:open="open" :title="editing ? 'Maydonni tahrirlash' : 'Yangi maydon qo\'shish'">
    <template #body>
      <div class="space-y-5">
        <UFormField label="Nomi" required>
          <UInput v-model="state.label" placeholder="masalan: Ro'yxat raqami" size="lg" class="w-full" />
        </UFormField>
        <div class="grid grid-cols-2 gap-4 items-end">
          <UFormField label="Maydon turi">
            <USelect v-model="state.field_type" :items="fieldTypes" size="lg" class="w-full" />
          </UFormField>
          <UFormField label="Majburiy">
            <USwitch v-model="state.is_required" />
          </UFormField>
        </div>
        <UFormField v-if="state.field_type === 'select'" label="Tanlov variantlari" help="Vergul bilan ajrating">
          <UInput v-model="state.options" placeholder="variant1, variant2, variant3" size="lg" class="w-full" />
        </UFormField>
      </div>
    </template>
    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton variant="ghost" label="Bekor qilish" @click="open = false" />
        <UButton :label="editing ? 'Saqlash' : 'Qo\'shish'" icon="i-lucide-save" :disabled="!state.label" @click="handleSave" />
      </div>
    </template>
  </UModal>
</template>
