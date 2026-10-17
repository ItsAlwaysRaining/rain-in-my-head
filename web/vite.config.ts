import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// In dev, Vite serves the app on :5173 and forwards /api to `uv run rain-in-my-head serve --dev` on :8000.
export default defineConfig({
  plugins: [react()],
  server: { proxy: { "/api": "http://127.0.0.1:8000" } },
  // Vega is most of the bundle; it's a local app, so one ~1 MB chunk is fine.
  build: { chunkSizeWarningLimit: 1500 },
});
