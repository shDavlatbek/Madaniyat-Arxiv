export interface UserResponse {
  id: string
  username: string
  name: string
  email: string | null
  role: string
  is_active: boolean
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

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}
