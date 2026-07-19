/**
 * Single source of truth for Uzbek UI labels.
 *
 * Code identifiers stay English (`department`, `archive_folder`, `document_view`, …);
 * the visible Uzbek strings live here so they cannot drift between the sidebar,
 * table headers, and form labels. Extend per phase — see tasks/plan.md.
 */
export const LABELS = {
  // Department (Bo'lim) — Phase 1
  department: "Bo'lim",
  departments: "Bo'limlar",
  department_name_short: 'Nomi',
  department_description: 'Tavsifi',
  department_status: 'Holati',
  add_department: "Bo'lim qo'shish",
  edit_department: "Bo'limni tahrirlash",
  delete_department: "Bo'limni o'chirish",
  add_user_to_department: "Xodim qo'shish",
  active: 'Faol',
  inactive: 'Nofaol',

  // Archive folder (Yig'ma jild) — Phase 2 + 7-field redesign
  archive_folder: "Yig'ma jild",
  archive_folders: "Yig'ma jildlar",
  index_code: "Yig'ma jild indeksi",
  title: "Yig'ma jild sarlavhasi",
  department_name: "Bo'lim nomi",
  department_index_code: "Bo'lim indeksi",
  article_number: 'Modda raqami',
  list_number: "Ro'yxat raqami",
  retention_period: 'Saqlash muddati',
  archive_folder_note: 'Eslatma',
  total_sheets: 'Umumiy varaqlar soni',
  start_date: 'Boshlanish sanasi',
  end_date: 'Tugash sanasi',
  document_count: 'Hujjatlar soni',
  add_archive_folder: "Yig'ma jild qo'shish",
  edit_archive_folder: "Yig'ma jildni tahrirlash",
  delete_archive_folder: "Yig'ma jildni o'chirish",

  // Document overhaul (Hujjat ko'rinishi) — Phase 3
  document_view: "Hujjat ko'rinishi",
  document_type: 'Hujjat turi',
  document_form: 'Hujjat shakli',
  sender: 'Yuboruvchi',
  language: 'Tili',
  short_desc: 'Hujjatning qisqacha mazmuni',
  pages_total: 'Umumiy varaqlar soni',
  file_upload: 'Fayllar yuklash',
  related_document_number: 'Aloqador hujjat raqami',
  related_document_date: 'Aloqador hujjat sanasi',
  received_date: 'Qabul qilingan sana',
  origin_organization: 'Kelib chiqqan tashkilot',
  sent_date: 'Yuborilgan sana',
  recipient_organization: 'Qabul qiluvchi',
  applicant_full_name: 'Murojaatchi F.I.Sh.',
  applicant_phone: 'Murojaatchi telefoni',

  // Murojaat (appeal) — reference form fields
  region: 'Hududni tanlang',
  country: 'Davlatni tanlang',
  reception_place: 'Qabul qilingan joy',
  appeal_type: 'Murojaat turi',
  outgoing_number: 'Chiqish raqami',
  outgoing_date: 'Chiqish sanasi',
  person_type: 'Yuridik yoki Jismoniy shaxs',
  signed_by: 'Kim tomonidan imzolangan (F.I.O)',
  signed_by_legal: 'Kim tomonidan yuborilgan',
  note: 'Eslatma',

  // Musiqa maktabi arxivi
  music_school: 'Musiqa maktabi',
  music_schools: 'Musiqa maktablari',
  specialty: "Mutaxassislik (cholg'u)",
  graduation_year: 'Bitirgan yili',
  diploma_serial: 'Diplom seriyasi',
  diploma_number: 'Diplom raqami',
  given_date: 'Berilgan sana',
  student_full_name: "O'quvchi F.I.Sh.",
} as const

/** Hudud — the synthetic "Xorijiy davlat" option in the region select. */
export const ABROAD_REGION_VALUE = '__abroad__'
export const ABROAD_REGION_LABEL = 'Xorijiy davlat'

/** Hujjat shakli — document-form option list (data/Hujjat shakli.json). */
export const DOCUMENT_FORM_OPTIONS = [
  'Elektron hujjat',
  "Qog'oz hujjatning nusxasi",
] as const

/** Yuridik yoki Jismoniy shaxs — person-type option list. */
export const PERSON_TYPE_OPTIONS = [
  'Yuridik shaxs',
  'Jismoniy shaxs',
] as const

/** Hujjat ko'rinishi — document view option labels, keyed by enum value. */
export const DOCUMENT_VIEW_LABELS = {
  incoming: 'Kiruvchi hujjat',
  outgoing: 'Chiquvchi hujjat',
  internal: 'Ichki hujjat',
  appeal: 'Murojaat',
  unknown: "Noma'lum",
} as const

/**
 * OCR pipeline lifecycle — label / color / icon paired so badges stay
 * consistent across the app. Color names map to Nuxt UI palette tokens.
 */
export const OCR_STATUS_LABELS = {
  pending: 'OCR kutmoqda',
  processing: 'OCR jarayonda',
  done: 'OCR tayyor',
  failed: 'OCR muvaffaqiyatsiz',
  skipped: "OCR o'tkazib yuborildi",
} as const

export const OCR_STATUS_COLORS = {
  pending: 'neutral',
  processing: 'warning',
  done: 'success',
  failed: 'error',
  skipped: 'neutral',
} as const

export const OCR_STATUS_ICONS = {
  pending: 'i-lucide-clock',
  processing: 'i-lucide-loader-2',
  done: 'i-lucide-check-circle',
  failed: 'i-lucide-alert-circle',
  skipped: 'i-lucide-minus-circle',
} as const

export type LabelKey = keyof typeof LABELS

export function label(key: LabelKey): string {
  return LABELS[key]
}
