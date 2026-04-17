import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    port: 5173,
    strictPort: true,
    cors: true,
    origin: 'http://127.0.0.1:5173',
  },
  build: {
    // Generate manifest.json in outDir
    manifest: true,
    outDir: '../backend/apps/core/static/react',
    emptyOutDir: true,
    rollupOptions: {
      input: './src/main.jsx',
      output: {
        entryFileNames: 'js/main.js',
        chunkFileNames: 'js/[name].js',
        assetFileNames: 'css/[name].[ext]'
      }
    }
  }
})
