import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      boxShadow: {
        glow: "0 0 0 1px rgba(255,255,255,0.08), 0 18px 48px rgba(0,0,0,0.38)",
      },
      colors: {
        ink: {
          950: "#07111f",
          900: "#0b1628",
          800: "#12233e",
        },
        ember: {
          500: "#f97316",
          600: "#ea580c",
        },
        aurora: {
          500: "#34d399",
          600: "#10b981",
        },
      },
    },
  },
  plugins: [],
};

export default config;
