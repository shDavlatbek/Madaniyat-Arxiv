<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const route = useRoute()
const { getDocument, updateDocument, uploadFile } = useMusicSchool()
const toast = useToast()
const saving = ref(false)

const id = computed(() => route.params.id as string)

const { data: doc, error } = await useAsyncData(`music-school-doc-edit-${id.value}`, () =>
  getDocument(id.value)
)

if (error.value) {
  toast.add({
    title: 'Xatolik',
    description: 'Hujjat topilmadi yoki yuklashda xatolik yuz berdi',
    color: 'error',
    icon: 'i-lucide-alert-circle',
  })
}

async function handleSubmit(payload: Record<string, any>, file: File | null) {
  saving.value = true
  try {
    await updateDocument(id.value, payload)
    toast.add({
      title: 'Muvaffaqiyat',
      description: 'Hujjat ma’lumotlari tahrirlandi',
      color: 'success',
      icon: 'i-lucide-check-circle',
    })

    if (file) {
      toast.add({
        title: 'Yuklash boshlandi',
        description: 'Yangi PDF fayl yuklanmoqda...',
        color: 'neutral',
        icon: 'i-lucide-loader-2',
      })
      await uploadFile(id.value, file)
      toast.add({
        title: 'Fayl yuklandi',
        description: 'Fayl muvaffaqiyatli saqlandi va OCR navbatiga qo‘shildi',
        color: 'success',
        icon: 'i-lucide-check-circle',
      })
    }

    navigateTo('/music-school-archive')
  } catch (err: any) {
    toast.add({
      title: 'Xatolik',
      description: err?.data?.detail || 'Hujjatni saqlashda xatolik yuz berdi',
      color: 'error',
      icon: 'i-lucide-alert-circle',
    })
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <PagePanel title="Diplom hujjattini tahrirlash" icon="i-lucide-music-4">
    <template #headerLeft>
      <UButton
        icon="i-lucide-arrow-left"
        variant="ghost"
        to="/music-school-archive"
      />
    </template>

    <div class="p-6 max-w-7xl mx-auto">
      <div v-if="!doc" class="flex flex-col items-center justify-center p-12 text-center text-muted gap-4">
        <UIcon name="i-lucide-loader-2" class="text-4xl text-primary animate-spin" />
        <p>Hujjat yuklanmoqda...</p>
      </div>

      <MusicSchoolDocumentForm
        v-else
        :initial-data="doc"
        :saving="saving"
        @submit="handleSubmit"
      />
    </div>
  </PagePanel>
</template>
