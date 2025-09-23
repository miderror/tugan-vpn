import { fileURLToPath, URL } from 'node:url'

import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import { createSvgIconsPlugin } from 'vite-plugin-svg-icons';
import path from 'path';

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, process.cwd(), '');

    return { 
        plugins: [
            vue(),
            vueDevTools(),
            createSvgIconsPlugin({
                iconDirs: [path.resolve(process.cwd(), 'src/assets/icons')],
                symbolId: 'icon-[dir]-[name]',
            }),
        ],
        resolve: {
            alias: {
                '@': fileURLToPath(new URL('./src', import.meta.url))
            },
        },
        server: {
            host: '0.0.0.0',
            port: 5173,
            hmr: {
                protocol: 'ws',
                host: 'localhost',
                port: 80,
            },
            watch: {
                usePolling: true,
            },
            strictPort: true,
            allowedHosts: env.VITE_ALLOWED_HOSTS?.split(',') || ['localhost'],
        },
    }
})