import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: '0.0.0.0', // 监听所有网络接口
    port: 5173,
    strictPort: false, // 如果端口被占用，尝试下一个可用端口
    // 显示所有可用的网络地址
    // Vite 会自动检测并显示所有网络接口的 IP
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '/api/v1')
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    // rolldown-vite 使用 esbuild 进行压缩（需要安装 esbuild 依赖）
    minify: 'esbuild',
    chunkSizeWarningLimit: 1000,
  },
  base: '/'
})