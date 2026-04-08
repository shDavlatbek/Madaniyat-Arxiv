<script setup lang="ts">
import { CalendarDate, type DateValue } from '@internationalized/date'

defineProps<{
  placeholder?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
}>()

const model = defineModel<string>()
const open = ref(false)

const day = ref('')
const month = ref('')
const yr = ref('')

const dayInput = ref<HTMLInputElement | null>(null)
const monthInput = ref<HTMLInputElement | null>(null)
const yearInput = ref<HTMLInputElement | null>(null)

// Sync from model to parts
function parseModel() {
  if (!model.value) {
    day.value = ''
    month.value = ''
    yr.value = ''
    return
  }
  const parts = model.value.split('-')
  if (parts.length === 3) {
    yr.value = parts[0]
    month.value = parts[1]
    day.value = parts[2]
  }
}

// Sync from parts to model
function syncToModel() {
  if (day.value && month.value && yr.value && yr.value.length === 4) {
    const d = day.value.padStart(2, '0')
    const m = month.value.padStart(2, '0')
    model.value = `${yr.value}-${m}-${d}`
  }
}

// Calendar value
const calendarValue = computed<DateValue | undefined>({
  get() {
    if (!model.value) return undefined
    const parts = model.value.split('-')
    if (parts.length !== 3) return undefined
    return new CalendarDate(Number(parts[0]), Number(parts[1]), Number(parts[2]))
  },
  set(val: DateValue | undefined) {
    if (!val) {
      model.value = ''
      day.value = ''
      month.value = ''
      yr.value = ''
    } else {
      const y = String(val.year).padStart(4, '0')
      const m = String(val.month).padStart(2, '0')
      const d = String(val.day).padStart(2, '0')
      model.value = `${y}-${m}-${d}`
      day.value = d
      month.value = m
      yr.value = y
    }
    open.value = false
  },
})

// Handle input with auto-advance
function onDayInput(e: Event) {
  const val = (e.target as HTMLInputElement).value.replace(/\D/g, '').slice(0, 2)
  day.value = val
  if (val.length === 2) monthInput.value?.focus()
  syncToModel()
}

function onMonthInput(e: Event) {
  const val = (e.target as HTMLInputElement).value.replace(/\D/g, '').slice(0, 2)
  month.value = val
  if (val.length === 2) yearInput.value?.focus()
  syncToModel()
}

function onYearInput(e: Event) {
  const val = (e.target as HTMLInputElement).value.replace(/\D/g, '').slice(0, 4)
  yr.value = val
  syncToModel()
}

function onDayKey(e: KeyboardEvent) {
  if (e.key === '/' || e.key === '.' || e.key === '-') {
    e.preventDefault()
    monthInput.value?.focus()
  }
  if (e.key === 'Backspace' && !day.value) {
    e.preventDefault()
  }
}

function onMonthKey(e: KeyboardEvent) {
  if (e.key === '/' || e.key === '.' || e.key === '-') {
    e.preventDefault()
    yearInput.value?.focus()
  }
  if (e.key === 'Backspace' && !month.value) {
    e.preventDefault()
    dayInput.value?.focus()
  }
}

function onYearKey(e: KeyboardEvent) {
  if (e.key === 'Backspace' && !yr.value) {
    e.preventDefault()
    monthInput.value?.focus()
  }
}

// Init
onMounted(() => parseModel())
watch(model, () => parseModel(), { immediate: true })
</script>

<template>
  <div class="flex items-center gap-0 border border-default rounded-lg bg-default hover:border-primary/50 focus-within:ring-2 focus-within:ring-primary/50 focus-within:border-primary transition-colors"
    :class="size === 'lg' ? 'h-10 px-3 text-sm' : size === 'sm' ? 'h-7 px-2 text-xs' : 'h-9 px-2.5 text-sm'"
  >
    <!-- Day -->
    <input
      ref="dayInput"
      :value="day"
      type="text"
      inputmode="numeric"
      placeholder="KK"
      class="w-6 text-center bg-transparent outline-none text-highlighted placeholder:text-muted/40"
      :class="size === 'sm' ? 'text-xs' : 'text-sm'"
      maxlength="2"
      @input="onDayInput"
      @keydown="onDayKey"
    />
    <span class="text-muted/40 select-none" :class="size === 'sm' ? 'text-xs' : 'text-sm'">/</span>
    <!-- Month -->
    <input
      ref="monthInput"
      :value="month"
      type="text"
      inputmode="numeric"
      placeholder="OO"
      class="w-6 text-center bg-transparent outline-none text-highlighted placeholder:text-muted/40"
      :class="size === 'sm' ? 'text-xs' : 'text-sm'"
      maxlength="2"
      @input="onMonthInput"
      @keydown="onMonthKey"
    />
    <span class="text-muted/40 select-none" :class="size === 'sm' ? 'text-xs' : 'text-sm'">/</span>
    <!-- Year -->
    <input
      ref="yearInput"
      :value="yr"
      type="text"
      inputmode="numeric"
      placeholder="YYYY"
      class="w-10 text-center bg-transparent outline-none text-highlighted placeholder:text-muted/40"
      :class="size === 'sm' ? 'text-xs' : 'text-sm'"
      maxlength="4"
      @input="onYearInput"
      @keydown="onYearKey"
    />

    <!-- Calendar button -->
    <UPopover v-model:open="open">
      <button type="button" class="ml-1 text-muted hover:text-primary transition-colors shrink-0 cursor-pointer">
        <UIcon name="i-lucide-calendar" :class="size === 'sm' ? 'text-sm' : 'text-base'" />
      </button>
      <template #content>
        <UCalendar v-model="calendarValue" class="p-2" />
      </template>
    </UPopover>
  </div>
</template>
