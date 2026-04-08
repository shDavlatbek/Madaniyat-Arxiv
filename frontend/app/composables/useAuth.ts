import type { UserResponse } from '~/types'

export const useAuth = () => {
  const token = useCookie('auth_token', { maxAge: 60 * 60 * 24 * 7 })
  const userCookie = useCookie<UserResponse | null>('auth_user', { maxAge: 60 * 60 * 24 * 7 })

  const user = computed(() => userCookie.value)
  const loggedIn = computed(() => !!token.value && !!userCookie.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  const { apiFetch } = useApi()

  async function login(username: string, password: string) {
    const response = await apiFetch<{ access_token: string; user: UserResponse }>('/api/auth/login', {
      method: 'POST',
      body: { username, password },
    })
    token.value = response.access_token
    userCookie.value = response.user
    return response.user
  }

  function logout() {
    token.value = null
    userCookie.value = null
    navigateTo('/login')
  }

  async function fetchMe() {
    try {
      const me = await apiFetch<UserResponse>('/api/auth/me')
      userCookie.value = me
      return me
    } catch {
      logout()
      return null
    }
  }

  return { user, loggedIn, isAdmin, token, login, logout, fetchMe }
}
