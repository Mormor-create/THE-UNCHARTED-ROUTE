/** @type {import('tailwindcss').Config} */

module.exports = {
    content: [
        "./templates/**/*.html",
        "./static/**/*.js",
    ],

    theme: {
        extend: {
            colors: {
                route: {
                    deep: "#12372A",
                    forest: "#1F5138",
                    safari: "#5C6B32",
                    gold: "#D89B24",
                    terracotta: "#C96A2C",
                    cream: "#F7F1E5",
                    sand: "#E9DDC8",
                    ink: "#1C2822",
                    muted: "#66736B",
                    white: "#FFFFFF",
                },
            },

            fontFamily: {
                sans: [
                    "DM Sans",
                    "ui-sans-serif",
                    "system-ui",
                    "sans-serif",
                ],

                display: [
                    "Playfair Display",
                    "Georgia",
                    "serif",
                ],
            },

            boxShadow: {
                route: "0 10px 30px rgba(18, 55, 42, 0.10)",
                "route-lg": "0 20px 50px rgba(18, 55, 42, 0.14)",
            },

            borderRadius: {
                route: "0.75rem",
            },
        },
    },

    plugins: [],
};