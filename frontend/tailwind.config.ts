import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./features/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        border: "#1f2937",
        background: "#030712",
        foreground: "#f9fafb",
        muted: "#111827",
        accent: "#22c55e",
        card: "#0b1220"
      }
    }
  },
  plugins: []
};

export default config;
