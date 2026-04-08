<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const route = useRoute()
const year = computed(() => Number(route.params.year))
const categoryId = computed(() => route.params.categoryId as string)
const documentId = computed(() => route.params.documentId as string)

const { getDocument, updateDocument } = useDocuments()
const toast = useToast()

const { data: doc } = await useAsyncData(`doc-edit-${documentId.value}`, () => getDocument(documentId.value))

async function handleSubmit(data: Record<string, any>) {
  try {
    await updateDocument(documentId.value, data)
    toast.add({ title: 'Muvaffaqiyat', description: 'Hujjat yangilandi', color: 'success', icon: 'i-lucide-check-circle' })
    navigateTo(`/archive/${year.value}/${categoryId.value}/${documentId.value}`)
  } catch (error: any) {
    toast.add({ title: 'Xatolik', description: error?.data?.detail || 'Yangilab bo\'lmadi', color: 'error', icon: 'i-lucide-alert-circle' })
  }
}
</script>

<template>
  <UDashboardPanel>
    <template #header>
      <UDashboardNavbar title="Hujjatni tahrirlash">
        <template #left>
          <UButton icon="i-lucide-arrow-left" variant="ghost" @click="$router.back()" />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="max-w-4xl mx-auto p-4 sm:p-6">
        <DocumentForm
          v-if="doc"
          :category-id="categoryId"
          :initial-data="doc"
          @submit="handleSubmit"
        />
      </div>
    </template>
  </UDashboardPanel>
</template>
