<script setup lang="ts">
import { CalendarDate, type DateValue } from '@internationalized/date'
const props = defineProps<{
  placeholder?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  minDate?: string
  maxDate?: string
}>()

const minValue = computed(() => {
  if (!props.minDate) return undefined
  const p = props.minDate.split('-')
  return p.length === 3 ? new CalendarDate(Number(p[0]), Number(p[1]), Number(p[2])) : undefined
})

const maxValue = computed(() => {
  if (!props.maxDate) return undefined
  const p = props.maxDate.split('-')
  return p.length === 3 ? new CalendarDate(Number(p[0]), Number(p[1]), Number(p[2])) : undefined
})

const model = defineModel<string>()
const inputDate = useTemplateRef('inputDate')

// Convert string "YYYY-MM-DD" ↔ CalendarDate
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
      return
    }
    const y = String(val.year).padStart(4, '0')
    const m = String(val.month).padStart(2, '0')
    const d = String(val.day).padStart(2, '0')
    model.value = `${y}-${m}-${d}`
  },
})

function formatDate(val: DateValue | undefined) {
  if (!val) return ''
  const d = String(val.day).padStart(2, '0')
  const m = String(val.month).padStart(2, '0')
  const y = String(val.year).padStart(4, '0')
  return `${d}.${m}.${y}`
}
</script>

<template>
  <UInputDate ref="inputDate" v-model="calendarValue" :size="size" :format="formatDate" :min-value="minValue" :max-value="maxValue">
    <template #trailing>
      <UPopover :reference="(inputDate as any)?.inputsRef?.[3]?.$el">
        <UButton
          color="neutral"
          variant="link"
          :size="size || 'sm'"
          icon="i-lucide-calendar"
          aria-label="Sana tanlash"
          class="px-0"
        />

        <template #content>
          <UCalendar v-model="calendarValue" :min-value="minValue" :max-value="maxValue" class="p-2" />
        </template>
      </UPopover>
    </template>
  </UInputDate>
</template>
