import type { PersonResponse } from '~/types'

export const usePersons = () => {
  const { apiFetch } = useApi()

  async function listPersons(search?: string) {
    const query = search ? `?search=${encodeURIComponent(search)}` : ''
    return apiFetch<{ items: PersonResponse[] }>(`/api/persons${query}`)
  }

  async function getActivePersons(date: string) {
    return apiFetch<{ items: PersonResponse[] }>(`/api/persons/active?date=${date}`)
  }

  async function getPerson(id: string) {
    return apiFetch<PersonResponse>(`/api/persons/${id}`)
  }

  async function createPerson(data: Record<string, any>) {
    return apiFetch<PersonResponse>('/api/persons', { method: 'POST', body: data })
  }

  async function updatePerson(id: string, data: Record<string, any>) {
    return apiFetch<PersonResponse>(`/api/persons/${id}`, { method: 'PUT', body: data })
  }

  async function deletePerson(id: string) {
    return apiFetch(`/api/persons/${id}`, { method: 'DELETE' })
  }

  return { listPersons, getActivePersons, getPerson, createPerson, updatePerson, deletePerson }
}
