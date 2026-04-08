import type { DocumentResponse, PaginatedResponse } from '~/types'

export const useDocuments = () => {
  const { apiFetch } = useApi()

  async function listDocuments(params: {
    year_id?: number
    category_id?: string
    search?: string
    date_from?: string
    date_to?: string
    page?: number
    page_size?: number
    field_filters?: Record<string, string>
  }) {
    const query = new URLSearchParams()
    if (params.year_id) query.set('year_id', String(params.year_id))
    if (params.category_id) query.set('category_id', params.category_id)
    if (params.search) query.set('search', params.search)
    if (params.date_from) query.set('date_from', params.date_from)
    if (params.date_to) query.set('date_to', params.date_to)
    if (params.page) query.set('page', String(params.page))
    if (params.page_size) query.set('page_size', String(params.page_size))
    if (params.field_filters && Object.keys(params.field_filters).length > 0) {
      query.set('field_filters', JSON.stringify(params.field_filters))
    }

    return apiFetch<PaginatedResponse<DocumentResponse>>(`/api/documents?${query.toString()}`)
  }

  async function getDocument(id: string) {
    return apiFetch<DocumentResponse>(`/api/documents/${id}`)
  }

  async function createDocument(data: Record<string, any>) {
    return apiFetch<DocumentResponse>('/api/documents', { method: 'POST', body: data })
  }

  async function updateDocument(id: string, data: Record<string, any>) {
    return apiFetch<DocumentResponse>(`/api/documents/${id}`, { method: 'PUT', body: data })
  }

  async function deleteDocument(id: string) {
    return apiFetch(`/api/documents/${id}`, { method: 'DELETE' })
  }

  async function uploadFile(id: string, file: File) {
    const formData = new FormData()
    formData.append('file', file)
    return apiFetch<DocumentResponse>(`/api/documents/${id}/file`, { method: 'POST', body: formData })
  }

  return { listDocuments, getDocument, createDocument, updateDocument, deleteDocument, uploadFile }
}
