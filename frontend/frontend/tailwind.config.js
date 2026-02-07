/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                brand: {
                    dark: '#0f172a',    // Slate 900
                    primary: '#4f46e5', // Indigo 600
                    accent: '#06b6d4',  // Cyan 500
                    light: '#f8fafc',   // Slate 50
                }
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
            }
        },
    },
    plugins: [],
}
