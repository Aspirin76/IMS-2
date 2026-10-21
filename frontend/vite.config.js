import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// 開發期：Vite dev server (5173) → 代理 /api 到 Flask (5000)
// 正式啟動：npm run build 產生 dist/，由 Flask 同時提供 API 與靜態檔（單一指令、單一網址）
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
  },
})
