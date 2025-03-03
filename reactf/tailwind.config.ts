import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic":
          "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
      },
    },
    screens: {
      'sm': '100px',
      // => @media (min-width: 640px) { ... }

      'md': '640px',
      // => @media (min-width: 840px) { ... }

      'lg': '1444px',
      // => @media (min-width: 1024px) { ... }
    },
    colors: {
      transparent: 'transparent',
      current: 'currentColor',
      'green': '#14532d',
      'red': '#b91c1c',
      'black': '#262626',
      'buttonwhite': '#d4d4d8',
      'grey': '#c4c2bb',
      'blue': '#8ec5ff',
      'purple': '#8200db'
    },
  },
  plugins: [],
};
export default config;
