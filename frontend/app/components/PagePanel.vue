<script setup lang="ts">
defineProps<{
  title?: string
  icon?: string
}>()
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Header area -->
    <div v-if="$slots.header || title" class="shrink-0 border-b border-default bg-elevated/30">
      <div v-if="title || $slots.headerLeft || $slots.headerRight" class="flex items-center gap-3 px-5 py-3.5">
        <div class="flex items-center gap-3">
          <slot name="headerLeft" />
          <UIcon v-if="icon" :name="icon" class="text-primary text-xl" />
          <h1 v-if="title" class="text-lg font-bold text-highlighted">{{ title }}</h1>
        </div>
        <div class="ml-auto flex items-center gap-2">
          <slot name="headerRight" />
        </div>
      </div>
      <slot name="header" />
    </div>

    <!-- Toolbar -->
    <div v-if="$slots.toolbar" class="shrink-0 border-b border-default px-5 py-2.5 flex items-center gap-2 bg-elevated/20">
      <slot name="toolbar" />
    </div>

    <!-- Body -->
    <div class="flex-1 overflow-y-auto">
      <slot />
    </div>
  </div>
</template>
