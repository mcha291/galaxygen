import { WebGLRenderer, type WebGLRendererParameters } from "three";

/**
 * three's check of every program it links (S80, #208 (c)): with `renderer.debug.checkShaderErrors` on, three reads
 * each program's and each shader's info log (`getProgramInfoLog`, `getShaderInfoLog`) on its first use and reports a
 * failure - 12-14 calls on the landing, 15-27 ms of the main thread (D242's profile), each a round trip to the GPU
 * process. On in development and in the tests (a broken shader is said where it broke), off in a production build,
 * where nothing reads the report. Read from Vite's `import.meta.env.PROD`: true in `vite build` (the production mode -
 * what the picture test, the smoothness probe and the images serve), false under `vite` (the dev server) and vitest.
 */
export const SHADER_CHECKS: boolean = !import.meta.env.PROD;

/**
 * The Galaxy view's renderer: what react-three-fiber makes from `gl={{ alpha: true, antialias: true }}` - its defaults
 * (the canvas, `powerPreference`) with those two over them - and the shader checks set before anything is compiled.
 */
export function galaxyRenderer(defaults: WebGLRendererParameters): WebGLRenderer {
  const gl = new WebGLRenderer({ ...defaults, alpha: true, antialias: true });
  gl.debug.checkShaderErrors = SHADER_CHECKS;
  return gl;
}
