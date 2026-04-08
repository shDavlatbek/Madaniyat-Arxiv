<template>
  <div ref="rootEl" class="relative flex flex-col border border-default overflow-hidden" :class="isFullscreen ? 'h-screen bg-white' : 'h-full'">
    <!-- Toolbar -->
    <div class="flex items-center justify-between py-2 px-3 shrink-0 z-10 bg-elevated/80 backdrop-blur border-b border-default">
      <!-- Left: page info -->
      <div class="flex items-center gap-2">
        <UIcon name="i-lucide-file-text" class="text-muted" />
        <span class="text-xs font-medium text-muted">
          {{ pages.length }} sahifa
        </span>
      </div>

      <!-- Center: Zoom controls -->
      <div class="flex items-center gap-1">
        <UButton variant="ghost" size="xs" icon="i-lucide-minus" color="neutral" :disabled="scale <= 0.25" @click="zoomOut" />
        <span class="text-xs font-medium w-12 text-center select-none text-muted">
          {{ Math.round(scale * 100) }}%
        </span>
        <UButton variant="ghost" size="xs" icon="i-lucide-plus" color="neutral" :disabled="scale >= 3" @click="zoomIn" />
        <UButton variant="ghost" size="xs" icon="i-lucide-maximize-2" color="neutral" @click="fitWidth" />
      </div>

      <!-- Right: Fullscreen + Download -->
      <div class="flex items-center gap-1">
        <UButton
          v-if="downloadUrl"
          variant="ghost"
          size="xs"
          icon="i-lucide-download"
          color="neutral"
          tag="a"
          :href="downloadUrl"
          target="_blank"
        />
        <UButton
          variant="ghost"
          size="xs"
          :icon="isFullscreen ? 'i-lucide-minimize-2' : 'i-lucide-maximize'"
          color="neutral"
          @click="toggleFullscreen"
        />
      </div>
    </div>

    <!-- Scrollable PDF area -->
    <div ref="scrollContainer" class="flex-1 overflow-auto bg-neutral-100 dark:bg-neutral-900">
      <div class="flex flex-col items-center gap-3 py-4 px-3 min-h-full">
        <div v-if="loading" class="flex items-center justify-center h-64 w-full">
          <div class="font-medium animate-pulse flex items-center gap-2 text-muted">
            <UIcon name="i-lucide-loader-2" class="animate-spin" />
            PDF yuklanmoqda...
          </div>
        </div>

        <div v-if="error" class="flex flex-col items-center justify-center h-64 w-full gap-3">
          <UIcon name="i-lucide-file-warning" class="text-3xl text-muted" />
          <p class="text-sm text-muted">PDF faylni yuklashda xatolik</p>
        </div>

        <!-- Pages -->
        <div
          v-for="page in pages"
          :key="page.num"
          :ref="el => setPageRef(el, page.num)"
          :data-page="page.num"
          class="relative overflow-hidden shadow-md ring-1 ring-default"
          :style="{ width: pageWidth + 'px', height: pageHeight + 'px' }"
        >
          <!-- Page number badge -->
          <!-- <div class="absolute top-2 left-2 z-10 bg-black/50 text-white text-[10px] font-medium px-1.5 py-0.5 rounded">
            {{ page.num }}
          </div> -->
          <canvas :ref="el => setCanvasRef(el, page.num)" class="block bg-white w-full h-full" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  pdfUrl: string
  downloadUrl?: string
}>()

const loading = ref(true)
const error = ref(false)
const pages = ref<{ num: number }[]>([])
const scale = ref(0.6)
const scrollContainer = ref<HTMLElement | null>(null)
const rootEl = ref<HTMLElement | null>(null)
const pageWidth = ref(300)
const pageHeight = ref(400)
const isFullscreen = ref(false)

let pdfDocRaw: any = null
let pdfjsLib: any = null
const canvasRefs: Record<number, HTMLCanvasElement> = {}
const pageRefs: Record<number, HTMLElement> = {}
const renderedPages = new Set<number>()
const renderingPages = new Set<number>()
let observer: IntersectionObserver | null = null
let pageAspect = 0.707

const setCanvasRef = (el: any, pageNum: number) => {
  if (el) canvasRefs[pageNum] = el as HTMLCanvasElement
}
const setPageRef = (el: any, pageNum: number) => {
  if (el) pageRefs[pageNum] = el as HTMLElement
}

// Fullscreen
const toggleFullscreen = async () => {
  if (!rootEl.value) return
  if (!document.fullscreenElement) {
    try { await rootEl.value.requestFullscreen() } catch {}
  } else {
    await document.exitFullscreen()
  }
}

const onFullscreenChange = () => {
  isFullscreen.value = !!document.fullscreenElement
  nextTick(() => setupObserver())
}

// Zoom
const zoomIn = () => applyZoom(Math.min(scale.value + 0.25, 3))
const zoomOut = () => applyZoom(Math.max(scale.value - 0.25, 0.25))
const fitWidth = () => {
  if (!scrollContainer.value) return
  const containerW = scrollContainer.value.clientWidth - 32
  const targetScale = containerW / 595
  applyZoom(Math.round(targetScale * 4) / 4)
}

const applyZoom = async (newScale: number) => {
  scale.value = newScale
  updatePageDimensions(pageAspect)
  renderedPages.clear()
  renderingPages.clear()

  for (const key of Object.keys(canvasRefs)) {
    const canvas = canvasRefs[parseInt(key)]
    if (canvas) {
      const ctx = canvas.getContext('2d')
      if (ctx) ctx.clearRect(0, 0, canvas.width, canvas.height)
    }
  }

  await nextTick()
  setupObserver()
}

const updatePageDimensions = (aspect: number) => {
  pageAspect = aspect
  const w = Math.round(595 * scale.value)
  pageWidth.value = w
  pageHeight.value = Math.round(w / aspect)
}

// PDF loading
const initPdfJs = async () => {
  if (!pdfjsLib) {
    pdfjsLib = await import('pdfjs-dist')
    const workerUrl = await import('pdfjs-dist/build/pdf.worker.min.mjs?url')
    pdfjsLib.GlobalWorkerOptions.workerSrc = workerUrl.default
  }
}

let blobUrl: string | null = null

const loadPdf = async () => {
  if (!props.pdfUrl) return
  loading.value = true
  error.value = false
  pages.value = []
  renderedPages.clear()
  renderingPages.clear()

  // Clean up previous blob URL
  if (blobUrl) {
    URL.revokeObjectURL(blobUrl)
    blobUrl = null
  }

  try {
    await initPdfJs()

    // Fetch PDF with auth token
    const token = useCookie('auth_token')
    const response = await fetch(props.pdfUrl, {
      headers: token.value ? { Authorization: `Bearer ${token.value}` } : {},
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const blob = await response.blob()
    blobUrl = URL.createObjectURL(blob)

    const loadingTask = pdfjsLib.getDocument(blobUrl)
    pdfDocRaw = await loadingTask.promise

    const firstPage = await pdfDocRaw.getPage(1)
    const vp = firstPage.getViewport({ scale: 1 })
    const aspect = vp.width / vp.height
    updatePageDimensions(aspect)

    pages.value = Array.from({ length: pdfDocRaw.numPages }, (_, i) => ({ num: i + 1 }))
    loading.value = false

    await nextTick()
    fitWidth()
    setupObserver()
  } catch (err) {
    console.error('PDF load error:', err)
    loading.value = false
    error.value = true
  }
}

const setupObserver = () => {
  if (observer) observer.disconnect()

  observer = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      const pageNum = parseInt((entry.target as HTMLElement).dataset.page || '0')
      if (entry.isIntersecting && pageNum > 0) {
        renderPage(pageNum)
      }
    }
  }, {
    root: scrollContainer.value,
    rootMargin: '300px 0px',
  })

  for (const pageObj of pages.value) {
    const el = pageRefs[pageObj.num]
    if (el) observer.observe(el)
  }
}

const renderPage = async (pageNum: number) => {
  if (renderedPages.has(pageNum) || renderingPages.has(pageNum) || !pdfDocRaw) return
  renderingPages.add(pageNum)

  try {
    const page = await pdfDocRaw.getPage(pageNum)
    const viewport = page.getViewport({ scale: scale.value })
    const canvas = canvasRefs[pageNum]
    if (!canvas) { renderingPages.delete(pageNum); return }

    const context = canvas.getContext('2d')
    if (!context) { renderingPages.delete(pageNum); return }

    canvas.width = viewport.width
    canvas.height = viewport.height

    await page.render({ canvasContext: context, viewport }).promise
    renderedPages.add(pageNum)
  } catch (e) {
    console.error(`Page ${pageNum} render error:`, e)
  } finally {
    renderingPages.delete(pageNum)
  }
}

onMounted(() => {
  loadPdf()
  document.addEventListener('fullscreenchange', onFullscreenChange)
})

watch(() => props.pdfUrl, () => loadPdf())

onUnmounted(() => {
  if (observer) observer.disconnect()
  document.removeEventListener('fullscreenchange', onFullscreenChange)
  if (blobUrl) URL.revokeObjectURL(blobUrl)
})
</script>
