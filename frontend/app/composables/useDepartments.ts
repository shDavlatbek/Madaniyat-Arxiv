import type { DepartmentResponse } from '~/types'

export const useDepartments = () => {
  const { apiFetch } = useApi()

  async function list(opts?: { search?: string, activeOnly?: boolean }) {
    const params = new URLSearchParams()
    if (opts?.search) params.set('search', opts.search)
    if (opts?.activeOnly) params.set('active_only', 'true')
    const query = params.toString() ? `?${params.toString()}` : ''
    return apiFetch<{ items: DepartmentResponse[] }>(`/api/departments${query}`)
  }

  async function get(id: string) {
    return apiFetch<DepartmentResponse>(`/api/departments/${id}`)
  }

  async function create(data: { name: string, description?: string | null }) {
    return apiFetch<DepartmentResponse>('/api/departments', { method: 'POST', body: data })
  }

  async function update(id: string, data: { name?: string, description?: string | null }) {
    return apiFetch<DepartmentResponse>(`/api/departments/${id}`, { method: 'PUT', body: data })
  }

  async function remove(id: string) {
    return apiFetch(`/api/departments/${id}`, { method: 'DELETE' })
  }

  async function activate(id: string) {
    return apiFetch<DepartmentResponse>(`/api/departments/${id}/activate`, { method: 'POST' })
  }

  async function deactivate(id: string) {
    return apiFetch<DepartmentResponse>(`/api/departments/${id}/deactivate`, { method: 'POST' })
  }

  return { list, get, create, update, remove, activate, deactivate }
}
