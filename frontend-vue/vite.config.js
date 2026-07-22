import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
export default defineConfig({plugins:[vue()],resolve:{alias:{'@':fileURLToPath(new URL('./src',import.meta.url))}},build:{chunkSizeWarningLimit:1600,rollupOptions:{output:{manualChunks:{echarts:['echarts'],'element-plus':['element-plus','@element-plus/icons-vue'],vue:['vue','vue-router']}}}},server:{host:'127.0.0.1',port:5173,proxy:{'/api':{target:'http://127.0.0.1:8000',changeOrigin:true},'/static':{target:'http://127.0.0.1:8000',changeOrigin:true}}}})
