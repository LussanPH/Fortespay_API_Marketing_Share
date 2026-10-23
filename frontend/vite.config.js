import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Em desenvolvimento, o Vite repassa as chamadas para a API local (sem CORS).
const API_LOCAL = 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/somaoffice_update': API_LOCAL,
      '/somaoffice_tempo': API_LOCAL,
      '/openapi.json': API_LOCAL,
      '/docs': API_LOCAL,
    },
  },
})
