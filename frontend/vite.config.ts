import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/ai': 'http://localhost:8000',
      '/residents': 'http://localhost:8000',
      '/supervisors': 'http://localhost:8000',
      '/subscriptions': 'http://localhost:8000',
      '/invoices': 'http://localhost:8000',
      '/assets': 'http://localhost:8000',
      '/maintenance': 'http://localhost:8000',
      '/notifications': 'http://localhost:8000',
      '/ops': 'http://localhost:8000'
    }
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true
  }
});
