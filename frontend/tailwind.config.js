/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#084981",
        "primary-light": "#1889c9",
        accent: "#d39e37",
        "accent-hover": "#bb8214",
        section: "#f1f5f8",
        badge: "#d5edff",
      },
      fontFamily: {
        urdu: ['"Mehr Nastaliq"', '"Mehr Nastaliq Web 3"', "serif"],
        title: ['"Aslam"', "serif"],
        quran: ['"Amiri Quran"', '"Scheherazade New"', "serif"],
        arabic: ['"Traditional Arabic"', '"Scheherazade New"', "serif"],
      },
      borderRadius: {
        card: "12px",
      },
    },
  },
  plugins: [],
};
