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
  department_name: 'Nomi',
  department_description: 'Tavsifi',
  department_status: 'Holati',
  add_department: "Bo'lim qo'shish",
  edit_department: "Bo'limni tahrirlash",
  delete_department: "Bo'limni o'chirish",
  add_user_to_department: "Xodim qo'shish",
  active: 'Faol',
  inactive: 'Nofaol',

  // Archive folder (Yig'ma jild) — Phase 2
  archive_folder: "Yig'ma jild",
  archive_folders: "Yig'ma jildlar",
  index_code: "Yig'ma jild indeksi",
  title: 'Sarlavha',
  retention_period: 'Saqlash muddati',
  start_date: 'Boshlanish sanasi',
  end_date: 'Tugash sanasi',
  document_count: 'Hujjatlar soni',
  add_archive_folder: "Yig'ma jild qo'shish",
  edit_archive_folder: "Yig'ma jildni tahrirlash",
  delete_archive_folder: "Yig'ma jildni o'chirish",
} as const

/** Saqlash muddati — retention period option labels, keyed by enum value. */
export const RETENTION_PERIOD_LABELS = {
  '3_years': '3 yil',
  '5_years': '5 yil',
  '10_years': '10 yil',
  '25_years': '25 yil',
  '50_years': '50 yil',
  '75_years': '75 yil',
  permanent: 'Doimiy',
  epk: 'EPK',
} as const

export type LabelKey = keyof typeof LABELS

export function label(key: LabelKey): string {
  return LABELS[key]
}
