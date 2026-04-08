<script setup lang="ts">
defineProps<{
  icon?: string
  title?: string
  description?: string
}>()
</script>

<template>
  <div class="flex flex-col items-center justify-center py-12 text-center">
    <UIcon v-if="icon" :name="icon" class="text-4xl text-muted mb-3" />
    <h3 v-if="title" class="text-base font-semibold text-highlighted mb-1">{{ title }}</h3>
    <p v-if="description" class="text-sm text-muted max-w-sm">{{ description }}</p>
  </div>
</template>
