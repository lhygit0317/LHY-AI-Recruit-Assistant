/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#EEF1F7",
        surface: "#FFFFFF",
        ink: "#141823",
        text: "#1B2030",
        "text-2": "#5A6477",
        "text-3": "#8B95A7",
        line: "#E4E8F0",
        blue: { DEFAULT: "#2B59FF", dark: "#1B3FCC", soft: "#EAF0FF" },
        teal: { DEFAULT: "#0CA5A0", soft: "#E1F6F4" },
        violet: { DEFAULT: "#7C3AED", soft: "#F1EBFE" },
        amber: { DEFAULT: "#C77A0B", soft: "#FBEEDA" },
        green: { DEFAULT: "#1E9E54", soft: "#E3F5EA" },
        red: { DEFAULT: "#D2453F", soft: "#FBEBEA" },
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', '"PingFang SC"', '"Microsoft YaHei"', 'sans-serif'],
        mono: ['"Space Grotesk"', 'ui-monospace', 'monospace'],
      },
      borderRadius: { DEFAULT: "10px", lg: "14px" },
      boxShadow: {
        sh: "0 1px 2px rgba(20,30,55,.04), 0 6px 20px rgba(20,30,55,.06)",
        "sh-lg": "0 12px 40px rgba(20,30,55,.14)",
      },
    },
  },
  plugins: [],
};