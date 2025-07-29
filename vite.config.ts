import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { quasar, transformAssetUrls } from '@quasar/vite-plugin'
import monacoEditorPluginModule from 'vite-plugin-monaco-editor'
import type { UserConfig } from 'vite'

const isObjectWithDefaultFunction = (module: unknown): module is { default: typeof monacoEditorPluginModule } => (
    module != null &&
    typeof module === 'object' &&
    'default' in module &&
    typeof module.default === 'function'
)

const monacoEditorPlugin = isObjectWithDefaultFunction(monacoEditorPluginModule)
    ? monacoEditorPluginModule.default
    : monacoEditorPluginModule
// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        vue({
            template: { transformAssetUrls }
        }),
        quasar({
            sassVariables: 'src/styles/quasar-variables.scss'
        }),
        monacoEditorPlugin({
            publicPath: 'monaco-editor',
            customWorkers: [
                {
                    label: 'python',
                    entry: 'monaco-editor/esm/vs/basic-languages/python/python.contribution'
                }
            ]
        })
    ],
    resolve: {
        alias: {
            '@': '/src'
        }
    },
    server: {
        port: 3000,
        open: true,
        proxy: {
            '/api': {
                target: 'http://localhost:8000',
                changeOrigin: true,
                rewrite: (path: string) => path.replace(/^\/api/, '/api/')
            }
        }
    },
    build: {
        target: 'es2015',
        chunkSizeWarningLimit: 2000,
        rollupOptions: {
            output: {
                manualChunks: {
                    'vendor': ['vue', 'vue-router', 'pinia', 'quasar'],
                    'echarts': ['echarts']
                }
            }
        }
    }
} as UserConfig)
