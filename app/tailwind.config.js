/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{html,js,ts,jsx,tsx}"],
  plugins: [require("daisyui")],
  daisyui: {
    themes: ["dark"], // only dark theme
    darkTheme: "dark",
  },
}
