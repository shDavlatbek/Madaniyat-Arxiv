import type { SearchRequest, SearchResponse } from '~/types'

/**
 * Thin client for ``POST /api/search``.
 *
 * Cancels any in-flight request when a new one fires so the UI never paints
 * stale results when the user keeps typing or flips filters quickly.
 */
export const useSearch = () => {
  const { apiFetch } = useApi()
  let currentAbort: AbortController | null = null

  async function search(request: SearchRequest): Promise<SearchResponse> {
    currentAbort?.abort()
    currentAbort = new AbortController()
    return apiFetch<SearchResponse>('/api/search', {
      method: 'POST',
      body: request,
      signal: currentAbort.signal,
    })
  }

  return { search }
}
