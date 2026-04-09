export default defineNuxtConfig({
  compatibilityDate: '2025-01-01',

  modules: ['@nuxt/ui'],

  css: ['~/assets/css/main.css'],

  runtimeConfig: {
    public: {
      apiBase: 'http://192.168.20.196:8000',
      // apiBase: 'http://localhost:8000',
    },
  },

  vite: {
    optimizeDeps: {
      include: ['pdfjs-dist'],
    },
  },

  devtools: { enabled: true },

  colorMode: {
    preference: 'light',
    fallback: 'light',
    classSuffix: '',
  },
})
