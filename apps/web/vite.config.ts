import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// El frontend habla con la API a través de VITE_API_BASE (ver .env.example).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
});
