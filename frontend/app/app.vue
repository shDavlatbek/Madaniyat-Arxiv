<script setup lang="ts">
import { en_gb } from '@nuxt/ui/locale'
</script>

<template>
  <UApp :locale="en_gb">
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </UApp>
</template>
