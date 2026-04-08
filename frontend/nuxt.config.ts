export default defineNuxtConfig({
  future: { compatibilityVersion: 4 },
  compatibilityDate: '2025-01-01',

  modules: ['@nuxt/ui'],

  css: ['~/assets/css/main.css'],

  runtimeConfig: {
    public: {
      apiBase: 'http://localhost:8000',
      // apiBase: 'http://192.168.20.196:8000',
    },
  },

  vite: {
    optimizeDeps: {
      include: ['pdfjs-dist'],
    },
  },

  devtools: { enabled: true },
  colorMode: {
    preference: 'light', // default = light
    fallback: 'light',   // fallback if system unknown
    classSuffix: ''      // important for Nuxt UI
  }
})
