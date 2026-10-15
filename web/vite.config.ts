import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// In dev, Vite serves the app on :5173 and forwards /api to `uv run listening serve --dev` on :8000.
export default defineConfig({
  plugins: [react()],
  server: { proxy: { "/api": "http://127.0.0.1:8000" } },
});
