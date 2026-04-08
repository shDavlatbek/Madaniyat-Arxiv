<script setup lang="ts">
definePageMeta({ layout: false })

if (import.meta.client) {
  navigateTo('/archive', { replace: true })
}
</script>

<template>
  <div />
</template>
