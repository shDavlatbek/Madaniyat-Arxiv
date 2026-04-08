<script setup lang="ts">
defineProps<{
  title?: string
}>()
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Header area -->
    <div v-if="$slots.header || title" class="shrink-0 border-b border-default">
      <div v-if="title || $slots.headerLeft || $slots.headerRight" class="flex items-center gap-2 px-4 py-3">
        <div class="flex items-center gap-2">
          <slot name="headerLeft" />
          <h1 v-if="title" class="text-lg font-semibold text-highlighted">{{ title }}</h1>
        </div>
        <div class="ml-auto flex items-center gap-2">
          <slot name="headerRight" />
        </div>
      </div>
      <slot name="header" />
    </div>

    <!-- Toolbar -->
    <div v-if="$slots.toolbar" class="shrink-0 border-b border-default px-4 py-2 flex items-center gap-2">
      <slot name="toolbar" />
    </div>

    <!-- Body -->
    <div class="flex-1 overflow-y-auto">
      <slot />
    </div>
  </div>
</template>
