<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })

const { createDocument, uploadFile } = useMusicSchool()
const toast = useToast()
const saving = ref(false)

async function handleSubmit(payload: Record<string, any>, file: File | null) {
  saving.value = true
  try {
    const doc = await createDocument(payload)
    toast.add({
      title: 'Muvaffaqiyat',
      description: 'Hujjat kartochkasi yaratildi',
      color: 'success',
      icon: 'i-lucide-check-circle',
    })

    if (file && doc?.id) {
      toast.add({
        title: 'Yuklash boshlandi',
        description: 'PDF fayl yuklanmoqda va OCR navbatiga qo‘yilmoqda...',
        color: 'neutral',
        icon: 'i-lucide-loader-2',
      })
      await uploadFile(doc.id, file)
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
  <PagePanel title="Yangi diplom qo‘shish" icon="i-lucide-music-4">
    <template #headerLeft>
      <UButton
        icon="i-lucide-arrow-left"
        variant="ghost"
        to="/music-school-archive"
      />
    </template>

    <div class="p-6 max-w-7xl mx-auto">
      <MusicSchoolDocumentForm
        :saving="saving"
        @submit="handleSubmit"
      />
    </div>
  </PagePanel>
</template>
