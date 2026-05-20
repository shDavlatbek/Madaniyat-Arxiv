export interface UserResponse {
  id: string
  username: string
  name: string
  email: string | null
  role: string
  is_active: boolean
  department_id: string | null
  department_name: string | null
  music_school_id: string | null
  music_school_name: string | null
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
  // Phase 6 — OCR lifecycle (worker-managed; read-only on the FE)
  ocr_status: OcrStatus
  ocr_completed_at: string | null
  field_values: DocumentFieldValueResponse[]
  attachments: AttachmentResponse[]
  created_at: string
  updated_at: string
}

export type OcrStatus = 'pending' | 'processing' | 'done' | 'failed' | 'skipped'

// ─── Phase 7 — Advanced search ───────────────────────────────────────────

export type SearchSort = 'relevance' | 'date_desc' | 'date_asc'

export interface SearchFilters {
  year_value?: number[]
  category_id?: string[]
  document_view?: string[]
  document_type_id?: string[]
  archive_folder_id?: string[]
  person_id?: string[]
  date_from?: string
  date_to?: string
}

export interface SearchRequest {
  q?: string
  filters?: SearchFilters
  facets?: string[]
  page?: number
  page_size?: number
  sort?: SearchSort
}

export interface SearchHighlight {
  title?: string[] | null
  short_desc?: string[] | null
  extracted_text?: string[] | null
  signer?: string[] | null
  person_name?: string[] | null
  note?: string[] | null
  attachments?: string[] | null
}

export interface SearchHit {
  id: string
  score: number | null
  title: string | null
  document_number: string | null
  short_desc: string | null
  signer: string | null
  archive_number: string | null
  date: string | null
  year_id: number | null
  year_value: number | null
  category_id: string | null
  category_name: string | null
  person_id: string | null
  person_name: string | null
  archive_folder_id: string | null
  archive_folder_title: string | null
  document_type_id: string | null
  document_type_name: string | null
  document_view: string | null
  highlights: SearchHighlight
}

export interface FacetBucket {
  value: string
  count: number
}

export interface SearchResponse {
  items: SearchHit[]
  total: number
  page: number
  page_size: number
  took_ms: number
  facets: Record<string, FacetBucket[]>
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
  ocr_status: OcrStatus
  ocr_completed_at: string | null
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
  index_code: string | null
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
  department_id: string | null
  department_name: string | null
  department_index_code: string | null
  article_number: string | null
  note: string | null
  retention_period_id: string | null
  retention_period_name: string | null
  start_date: string | null
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


export interface MusicSchoolResponse {
  id: string
  name: string
  code: string | null
  created_at: string
  updated_at: string
}

export interface MusicSchoolDocumentResponse {
  id: string
  student_full_name: string
  music_school_id: string
  music_school_name: string | null
  specialty_id: string
  specialty: string | null
  graduation_year: number
  diploma_serial: string
  diploma_number: string
  given_date: string
  description: string | null
  file_path: string | null
  ocr_status: OcrStatus
  ocr_completed_at: string | null
  created_by: string | null
  created_at: string
  updated_at: string
}

export interface MusicSchoolSpecialtyResponse {
  id: string
  music_school_id: string
  name: string
  created_at: string
  updated_at: string
}

export interface MusicSchoolSearchFilters {
  music_school_id?: string[]
  graduation_year?: number[]
  specialty?: string[]
  date_from?: string
  date_to?: string
}

export interface MusicSchoolSearchRequest {
  q?: string
  filters?: MusicSchoolSearchFilters
  facets?: string[]
  page?: number
  page_size?: number
  sort?: SearchSort
}

export interface MusicSchoolSearchHighlight {
  student_full_name?: string[] | null
  specialty?: string[] | null
  description?: string[] | null
  extracted_text?: string[] | null
}

export interface MusicSchoolSearchHit {
  id: string
  score: number | null
  student_full_name: string | null
  music_school_id: string | null
  music_school_name: string | null
  specialty: string | null
  graduation_year: number | null
  diploma_serial: string | null
  diploma_number: string | null
  given_date: string | null
  description: string | null
  file_path: string | null
  ocr_status: OcrStatus | null
  highlights: MusicSchoolSearchHighlight
}

export interface MusicSchoolSearchResponse {
  items: MusicSchoolSearchHit[]
  total: number
  page: number
  page_size: number
  took_ms: number
  facets: Record<string, FacetBucket[]>
}

