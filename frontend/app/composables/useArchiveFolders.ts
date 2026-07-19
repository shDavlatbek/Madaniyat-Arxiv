import type { ArchiveFolderResponse } from '~/types'

interface ArchiveFolderPayload {
  index_code?: string
  title?: string
  department_id?: string | null
  article_number?: string | null
  list_number?: string | null
  note?: string | null
  retention_period_id?: string | null
  total_sheets?: number | null
  start_date?: string | null
  end_date?: string | null
}

export const useArchiveFolders = () => {
  const { apiFetch } = useApi()

  async function list(opts?: { search?: string }) {
    const params = new URLSearchParams()
    if (opts?.search) params.set('search', opts.search)
    const query = params.toString() ? `?${params.toString()}` : ''
    return apiFetch<{ items: ArchiveFolderResponse[] }>(`/api/archive-folders${query}`)
  }

  async function get(id: string) {
    return apiFetch<ArchiveFolderResponse>(`/api/archive-folders/${id}`)
  }

  async function create(data: ArchiveFolderPayload) {
    return apiFetch<ArchiveFolderResponse>('/api/archive-folders', { method: 'POST', body: data })
  }

  async function update(id: string, data: ArchiveFolderPayload) {
    return apiFetch<ArchiveFolderResponse>(`/api/archive-folders/${id}`, { method: 'PUT', body: data })
  }

  async function remove(id: string) {
    return apiFetch(`/api/archive-folders/${id}`, { method: 'DELETE' })
  }

  return { list, get, create, update, remove }
}
