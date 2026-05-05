import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

const SHARED_SRC = resolve(__dirname, '../web/frontend/src')

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': SHARED_SRC,
    },
  },
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
  build: {
    outDir: 'dist',
    rollupOptions: {
      external: ['@tauri-apps/api/core'],
    },
  },
})
