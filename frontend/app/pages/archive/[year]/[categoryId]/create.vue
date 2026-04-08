<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const route = useRoute()
const year = computed(() => Number(route.params.year))
const categoryId = computed(() => route.params.categoryId as string)

const { createDocument } = useDocuments()
const toast = useToast()

async function handleSubmit(data: Record<string, any>) {
  try {
    await createDocument({
      ...data,
      year_id: year.value,
      category_id: categoryId.value,
    })
    toast.add({ title: 'Muvaffaqiyat', description: 'Hujjat yaratildi', color: 'success', icon: 'i-lucide-check-circle' })
    navigateTo(`/archive/${year.value}/${categoryId.value}`)
  } catch (error: any) {
    toast.add({ title: 'Xatolik', description: error?.data?.detail || 'Hujjat yaratib bo\'lmadi', color: 'error', icon: 'i-lucide-alert-circle' })
  }
}
</script>

<template>
  <UDashboardPanel>
    <template #header>
      <UDashboardNavbar title="Yangi hujjat">
        <template #left>
          <UButton icon="i-lucide-arrow-left" variant="ghost" @click="$router.back()" />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="max-w-4xl mx-auto p-4 sm:p-6">
        <DocumentForm :category-id="categoryId" @submit="handleSubmit" />
      </div>
    </template>
  </UDashboardPanel>
</template>
