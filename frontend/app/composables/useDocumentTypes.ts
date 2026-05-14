import type { DocumentTypeResponse } from '~/types'

export const useDocumentTypes = () => {
  const { apiFetch } = useApi()

  async function list(opts?: { search?: string }) {
    const params = new URLSearchParams()
    if (opts?.search) params.set('search', opts.search)
    const query = params.toString() ? `?${params.toString()}` : ''
    return apiFetch<{ items: DocumentTypeResponse[] }>(`/api/document-types${query}`)
  }

  async function get(id: string) {
    return apiFetch<DocumentTypeResponse>(`/api/document-types/${id}`)
  }

  async function create(data: { name: string }) {
    return apiFetch<DocumentTypeResponse>('/api/document-types', { method: 'POST', body: data })
  }

  async function update(id: string, data: { name?: string }) {
    return apiFetch<DocumentTypeResponse>(`/api/document-types/${id}`, { method: 'PUT', body: data })
  }

  async function remove(id: string) {
    return apiFetch(`/api/document-types/${id}`, { method: 'DELETE' })
  }

  return { list, get, create, update, remove }
}
