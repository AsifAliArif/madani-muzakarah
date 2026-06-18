/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#0B6487",
        "primary-dark": "#064661",
        "primary-light": "#1A9BC4",
        accent: "#C9932E",
        "accent-hover": "#A87820",
        section: "#F0F7FA",
        badge: "#D4EDF5",
        surface: "#FFFFFF",
        muted: "#64748B",
      },
      fontFamily: {
        urdu: ['"Mehr Nastaliq Web 3"', '"Mehr Nastaliq Web"', '"Mehr Nastaliq"', "serif"],
        title: ['"Aslam-new"', '"Aslam"', "serif"],
        quran: ['"Al-Qalam-V1"', '"Amiri Quran"', '"Scheherazade New"', "serif"],
        arabic: ['"Naskh Unicode"', '"Traditional Arabic"', '"Scheherazade New"', "serif"],
      },
      borderRadius: {
        card: "12px",
      },
      boxShadow: {
        card: "0 2px 12px rgba(6, 70, 97, 0.08)",
        elevated: "0 8px 24px rgba(6, 70, 97, 0.12)",
      },
    },
  },
  plugins: [],
};
