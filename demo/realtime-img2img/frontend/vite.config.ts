import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],
  server: {
    proxy: {
      '/api': 'http://192.168.0.19:7860',
      '/api/ws': {
        target: 'ws://192.168.0.19:7860',
        ws: true
      }
    }
  }
});
