/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3b82f6', // Cyber blue
        accent: '#f59e0b', // Amber alert
        success: '#10b981', // Neon green
        slate: {
          850: '#151e2e',
          900: '#0f172a',
          950: '#020617',
        }
      },
      animation: {
        'fade-in-up': 'fadeInUp 0.5s ease-out',
        'spin-slow': 'spin 3s linear infinite',
        'progress-bar': 'progress 3s ease-in-out infinite',
      },
      keyframes: {
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        progress: {
          '0%': { width: '0%', marginLeft: '0%' },
          '50%': { width: '30%', marginLeft: '70%' },
          '100%': { width: '0%', marginLeft: '100%' },
        }
      }
    },
  },
  plugins: [],
}
