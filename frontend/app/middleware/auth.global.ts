export default defineNuxtRouteMiddleware((to) => {
  const { loggedIn } = useAuth()

  if (to.path === '/login') {
    if (loggedIn.value) {
      return navigateTo('/archive')
    }
    return
  }

  if (!loggedIn.value && to.path !== '/login') {
    return navigateTo('/login')
  }
})
