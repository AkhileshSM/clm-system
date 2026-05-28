export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'clm-dark': '#0b0f1a',
        'clm-card': '#161e2e',
        'clm-card-hover': '#1e293b',
        'clm-accent': '#38bdf8',
        'clm-border': '#1e293b',
        'risk-normal': '#10b981',
        'risk-elevated': '#f59e0b',
        'risk-high': '#f97316',
        'risk-burnout': '#ef4444',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
}
