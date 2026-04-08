<script setup lang="ts">
import type { CategoryFieldResponse } from '~/types'

const props = defineProps<{
  field: CategoryFieldResponse
}>()

const model = defineModel<any>()
</script>

<template>
  <UFormField :label="field.label" :name="field.name" :required="field.is_required">
    <UInput
      v-if="field.field_type === 'text'"
      v-model="model"
      :placeholder="field.placeholder || ''"
    />
    <UInputNumber
      v-else-if="field.field_type === 'number'"
      v-model="model"
      :placeholder="field.placeholder || ''"
    />
    <UInput
      v-else-if="field.field_type === 'date'"
      v-model="model"
      type="date"
    />
    <UTextarea
      v-else-if="field.field_type === 'textarea'"
      v-model="model"
      :placeholder="field.placeholder || ''"
      :rows="3"
    />
    <USelect
      v-else-if="field.field_type === 'select'"
      v-model="model"
      :items="field.options || []"
      :placeholder="field.placeholder || 'Tanlang...'"
    />
    <UInput
      v-else
      v-model="model"
      :placeholder="field.placeholder || ''"
    />
  </UFormField>
</template>
