import { loadPyodide } from "pyodide";
import langString from './lang.py?raw';
import CanvasKitInit from 'canvaskit-wasm';

const ckLoaded = CanvasKitInit({
    // locateFile: (file) => 'https://unpkg.com/canvaskit-wasm@0.39.1/bin/' + file
    locateFile: (file) => 'node_modules/canvaskit-wasm/bin/' + file
});

export const loadCanvasKit = (() => {
    return () => ckLoaded;
})();

async function loadLangInternal() {
    let pyodide = await loadPyodide();
    await pyodide.loadPackage("https://cdn.jsdelivr.net/pyodide/v0.25.0/full/packaging-23.1-py3-none-any.whl");
    await pyodide.loadPackage("https://cdn.jsdelivr.net/pyodide/v0.25.0/full/micropip-0.5.0-py3-none-any.whl");
    const micropip = pyodide.pyimport("micropip");
    await micropip.install("lark");
    await pyodide.FS.writeFile("lang.py", langString, { encoding: "utf8" });
    // Pyimport lang.py
    return pyodide.pyimport("lang")
}

// Export a memoized function to avoid loading the module multiple. Only call promise during first call.

let memoizedLangPromise = null;

export const loadLang = (() => {
    return () => {
        if (memoizedLangPromise === null) {
            memoizedLangPromise = loadLangInternal();
        }
        return memoizedLangPromise;
    };
})();