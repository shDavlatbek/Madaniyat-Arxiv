import type { ArchiveFolderResponse } from '~/types'

interface ArchiveFolderPayload {
  index_code?: string
  title?: string
  retention_period_id?: string | null
  start_date?: string
  end_date?: string | null
  year_id?: number | null
}

export const useArchiveFolders = () => {
  const { apiFetch } = useApi()

  async function list(opts?: { yearId?: number, search?: string }) {
    const params = new URLSearchParams()
    if (opts?.yearId != null) params.set('year_id', String(opts.yearId))
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
