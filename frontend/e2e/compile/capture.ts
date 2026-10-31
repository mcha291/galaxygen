// The compile probe's capture (S78, T29): the march's program text exactly as the viewer hands it to WebGL.
// Bundled by compile.probe.ts (vite, this frontend's own config) into one script for a blank page, it builds a
// renderer with react-three-fiber's defaults (GalaxyView's Canvas: alpha, antialias, high-performance) and runs the
// viewer's own precompileMarch, recording every shaderSource call: three's prefix (the version, the precision lines,
// the defines, the gl_FragColor and texture2D renames) and FieldVolume's VERTEX and fieldFragment(), as three r186's
// WebGLProgram assembles them for that ShaderMaterial into a float target. Until S78's fix the text had the step count
// compiled in, and the call took it (precompileMarch(gl, steps, [])); since then one program serves every count, and
// `steps` names the probe's row only.
// Typechecked with the viewer (tsconfig.json includes it): it imports FieldVolume.tsx.

import { ACESFilmicToneMapping, SRGBColorSpace, WebGLRenderer } from "three";

import { precompileMarch } from "../../src/galaxy/FieldVolume";

export interface Captured {
  vertex: string;
  fragment: string;
  /** The precompileMarch call's own time in this page, ms: the renderer's compileAsync to its resolution. */
  ms: number;
}

async function capture(steps: number): Promise<Captured> {
  const texts: { type: number; source: string }[] = [];
  const types = new WeakMap<WebGLShader, number>();
  const proto = WebGL2RenderingContext.prototype;
  const create = proto.createShader;
  const source = proto.shaderSource;
  proto.createShader = function (this: WebGL2RenderingContext, type: number) {
    const shader = create.call(this, type);
    if (shader) types.set(shader, type);
    return shader;
  };
  proto.shaderSource = function (this: WebGL2RenderingContext, shader: WebGLShader, text: string) {
    texts.push({ type: types.get(shader) ?? 0, source: text });
    return source.call(this, shader, text);
  };
  const canvas = document.createElement("canvas");
  canvas.width = 1;
  canvas.height = 1;
  const gl = new WebGLRenderer({ canvas, powerPreference: "high-performance", antialias: true, alpha: true });
  gl.outputColorSpace = SRGBColorSpace;
  gl.toneMapping = ACESFilmicToneMapping;
  const started = performance.now();
  void steps;
  await precompileMarch(gl);
  const ms = performance.now() - started;
  proto.createShader = create;
  proto.shaderSource = source;
  const ctx = gl.getContext();
  const vertex = texts.filter((t) => t.type === ctx.VERTEX_SHADER).map((t) => t.source);
  const fragment = texts.filter((t) => t.type === ctx.FRAGMENT_SHADER).map((t) => t.source);
  gl.dispose();
  if (vertex.length !== 1 || fragment.length !== 1) throw new Error(`expected one program, saw ${vertex.length} vertex and ${fragment.length} fragment shaders`);
  return { vertex: vertex[0], fragment: fragment[0], ms };
}

(globalThis as { __galaxygenCompileCapture?: typeof capture }).__galaxygenCompileCapture = capture;
