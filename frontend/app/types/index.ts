export interface UserResponse {
  id: string
  username: string
  name: string
  email: string | null
  role: string
  is_active: boolean
  department_id: string | null
  department_name: string | null
  created_at: string
  updated_at: string
}

export interface YearResponse {
  id: number
  value: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CategoryFieldResponse {
  id: string
  category_id: string
  name: string
  label: string
  field_type: string
  is_required: boolean
  sort_order: number
  options: string[] | null
  placeholder: string | null
  validation: Record<string, any> | null
  created_at: string
}

export interface CategoryResponse {
  id: string
  name: string
  code: string
  description: string | null
  sort_order: number
  year_id: number | null
  fields: CategoryFieldResponse[]
  created_at: string
  updated_at: string
}

export interface DocumentFieldValueResponse {
  category_field_id: string
  value: string | null
}

export type DocumentView = 'incoming' | 'outgoing' | 'internal' | 'appeal' | 'unknown'

export interface DocumentResponse {
  id: string
  year_id: number
  category_id: string
  title: string
  document_number: string
  date: string
  short_desc: string | null
  pages: number | null
  file_path: string | null
  signer: string | null
  archive_number: string | null
  person_id: string | null
  person_name: string | null
  person_position: string | null
  created_by: string | null
  // Phase 3 — document view + universal fields
  document_view: DocumentView
  archive_folder_id: string | null
  document_type_id: string | null
  document_type_name: string | null
  document_form: string | null
  sender: string | null
  language: string | null
  related_document_number: string | null
  related_document_date: string | null
  // Phase 3 — view-specific fields
  received_date: string | null
  origin_organization: string | null
  sent_date: string | null
  recipient_organization: string | null
  applicant_full_name: string | null
  applicant_phone: string | null
  // Murojaat (appeal) — reference FKs + extra fields
  region_id: string | null
  country_id: string | null
  reception_place_id: string | null
  appeal_type_id: string | null
  person_type: string | null
  outgoing_number: string | null
  outgoing_date: string | null
  signed_by: string | null
  note: string | null
  field_values: DocumentFieldValueResponse[]
  attachments: AttachmentResponse[]
  created_at: string
  updated_at: string
}

export interface DefaultFieldResponse {
  id: string
  name: string
  label: string
  field_type: string
  is_required: boolean
  sort_order: number
  options: string[] | null
  placeholder: string | null
  created_at: string
}

export interface AttachmentResponse {
  id: string
  file_path: string
  original_filename: string
  sort_order: number
  created_at: string
}

export interface PersonTenureResponse {
  id: string
  position: string
  start_date: string
  end_date: string | null
  created_at: string
}

export interface PersonResponse {
  id: string
  full_name: string
  tenures: PersonTenureResponse[]
  created_at: string
  updated_at: string
}

export interface DepartmentResponse {
  id: string
  name: string
  description: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface DocumentTypeResponse {
  id: string
  name: string
  created_at: string
  updated_at: string
}

export type RegionType = 'LOCAL' | 'ABROAD'

export interface RegionResponse {
  id: string
  name: string
  type: RegionType
}

export interface ReceptionPlaceResponse {
  id: string
  name: string
}

export interface AppealTypeResponse {
  id: string
  name: string
}

export interface RetentionPeriodResponse {
  id: string
  name: string
}

export interface ArchiveFolderResponse {
  id: string
  index_code: string
  title: string
  retention_period_id: string | null
  retention_period_name: string | null
  start_date: string
  end_date: string | null
  year_id: number | null
  document_count: number
  created_at: string
  updated_at: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}
