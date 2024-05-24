import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import Icons from 'unplugin-icons/vite'

// Import fs and path modules
import fs from 'fs';
import path from 'path';

export default defineConfig({
	plugins: [
		sveltekit(),
		Icons({
			compiler: 'svelte',
		}),
		{
			name: 'copy-pyodide',
			// At build end, copy all files in /node_modules/pyodide/* to build/_app/immutable/chunks/*
			async closeBundle() {
				const src = path.join('node_modules', 'pyodide');
				// const dest = path.join('build', '_app', 'immutable', 'chunks');
				const dest = path.join('.svelte-kit', 'output', 'client', '_app', 'immutable', 'chunks');
				fs.mkdirSync(dest, { recursive: true });
				fs.readdirSync(src).forEach(file => {
					fs.copyFileSync(path.join(src, file), path.join(dest, file));
				});
			}

		}
	],
	resolve: {
		alias: {
			'node-fetch': 'isomorphic-fetch',
		},
	},
	optimizeDeps: {
		include: ["canvaskit-wasm"],
		exclude: ["pyodide"],
	},
});
