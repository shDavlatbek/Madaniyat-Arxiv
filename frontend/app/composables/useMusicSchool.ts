import type {
  MusicSchoolResponse,
  MusicSchoolDocumentResponse,
  MusicSchoolDocumentListResponse,
  MusicSchoolSearchRequest,
  MusicSchoolSearchResponse,
} from '~/types'

export const useMusicSchool = () => {
  const { apiFetch } = useApi()

  // --- Music Schools CRUD ---
  async function listSchools(search?: string) {
    const query = new URLSearchParams()
    if (search) query.set('search', search)
    return apiFetch<{ items: MusicSchoolResponse[] }>(`/api/music-schools?${query.toString()}`)
  }

  async function getSchool(id: string) {
    return apiFetch<MusicSchoolResponse>(`/api/music-schools/${id}`)
  }

  async function createSchool(data: { name: string; code?: string | null }) {
    return apiFetch<MusicSchoolResponse>('/api/music-schools', { method: 'POST', body: data })
  }

  async function updateSchool(id: string, data: { name: string; code?: string | null }) {
    return apiFetch<MusicSchoolResponse>(`/api/music-schools/${id}`, { method: 'PUT', body: data })
  }

  async function deleteSchool(id: string) {
    return apiFetch(`/api/music-schools/${id}`, { method: 'DELETE' })
  }

  // --- Music School Documents CRUD ---
  async function listDocuments(params: {
    music_school_id?: string
    graduation_year?: number
    specialty?: string
    search?: string
    page?: number
    page_size?: number
  }) {
    const query = new URLSearchParams()
    if (params.music_school_id) query.set('music_school_id', params.music_school_id)
    if (params.graduation_year) query.set('graduation_year', String(params.graduation_year))
    if (params.specialty) query.set('specialty', params.specialty)
    if (params.search) query.set('search', params.search)
    if (params.page) query.set('page', String(params.page))
    if (params.page_size) query.set('page_size', String(params.page_size))

    return apiFetch<{ items: MusicSchoolDocumentResponse[]; total: number; page: number; page_size: number }>(
      `/api/music-school-documents?${query.toString()}`
    )
  }

  async function getDocument(id: string) {
    return apiFetch<MusicSchoolDocumentResponse>(`/api/music-school-documents/${id}`)
  }

  async function createDocument(data: Record<string, any>) {
    return apiFetch<MusicSchoolDocumentResponse>('/api/music-school-documents', { method: 'POST', body: data })
  }

  async function updateDocument(id: string, data: Record<string, any>) {
    return apiFetch<MusicSchoolDocumentResponse>(`/api/music-school-documents/${id}`, { method: 'PUT', body: data })
  }

  async function deleteDocument(id: string) {
    return apiFetch(`/api/music-school-documents/${id}`, { method: 'DELETE' })
  }

  async function uploadFile(id: string, file: File) {
    const formData = new FormData()
    formData.append('file', file)
    return apiFetch<MusicSchoolDocumentResponse>(`/api/music-school-documents/${id}/file`, {
      method: 'POST',
      body: formData,
    })
  }

  // --- Elasticsearch-backed search ---
  async function searchDocuments(request: MusicSchoolSearchRequest) {
    return apiFetch<MusicSchoolSearchResponse>('/api/music-school-documents/search', {
      method: 'POST',
      body: request,
    })
  }

  // --- Music School Specialties ---
  async function listSpecialties(schoolId: string) {
    return apiFetch<any[]>(`/api/music-schools/${schoolId}/specialties`)
  }

  async function createSpecialty(schoolId: string, name: string) {
    return apiFetch<any>(`/api/music-schools/${schoolId}/specialties`, {
      method: 'POST',
      body: { name },
    })
  }

  async function deleteSpecialty(schoolId: string, specialtyId: string) {
    return apiFetch(`/api/music-schools/${schoolId}/specialties/${specialtyId}`, {
      method: 'DELETE',
    })
  }

  async function importSpecialties(schoolId: string, sourceSchoolId: string, specialtyIds: string[]) {
    return apiFetch<any[]>(`/api/music-schools/${schoolId}/specialties/import`, {
      method: 'POST',
      body: {
        source_school_id: sourceSchoolId,
        specialty_ids: specialtyIds,
      },
    })
  }

  return {
    listSchools,
    getSchool,
    createSchool,
    updateSchool,
    deleteSchool,
    listDocuments,
    getDocument,
    createDocument,
    updateDocument,
    deleteDocument,
    uploadFile,
    searchDocuments,
    listSpecialties,
    createSpecialty,
    deleteSpecialty,
    importSpecialties,
  }
}
