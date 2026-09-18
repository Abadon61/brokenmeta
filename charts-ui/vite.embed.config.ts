import path from 'node:path'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: { alias: { '@': path.resolve(__dirname, './src') } },
  publicDir: false,
  define: { 'process.env.NODE_ENV': '"production"' },
  build: {
    outDir: '../site_build/vendor',
    emptyOutDir: false,
    lib: { entry: 'src/embed.tsx', formats: ['iife'], name: 'bmCharts', fileName: () => 'bm-charts.js' },
    cssCodeSplit: false,
  },
})
