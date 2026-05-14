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
  active: 'Faol',
  inactive: 'Nofaol',
} as const

export type LabelKey = keyof typeof LABELS

export function label(key: LabelKey): string {
  return LABELS[key]
}
