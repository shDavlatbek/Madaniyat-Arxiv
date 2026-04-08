export default defineAppConfig({
  ui: {
    colors: {
      primary: 'madaniyat',
      neutral: 'slate',
    },
  },
  colorMode: {
    preference: 'light', // default = light
    fallback: 'light',   // fallback if system unknown
    classSuffix: ''      // important for Nuxt UI
  }
})
