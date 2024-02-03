const starlightPlugin = require('@astrojs/starlight-tailwind');

/** @type {import('tailwindcss').Config} */

// Generated color palettes
const accent = { 200: '#dab9f6', 600: '#9900dd', 900: '#461365', 950: '#301344' };
const gray = { 100: '#f4f6fa', 200: '#eaeef6', 300: '#bdc2cc', 400: '#838c9e', 500: '#505869', 700: '#313848', 800: '#202736', 900: '#15181f' };

/** @type {import('tailwindcss').Config} */
module.exports = {
	content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
	theme: {
		extend: {
			colors: { accent, gray },
		},
	},
	plugins: [starlightPlugin()],
};