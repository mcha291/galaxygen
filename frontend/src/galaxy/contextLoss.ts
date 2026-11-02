import { useSyncExternalStore } from "react";

// The renderer survives a lost WebGL context (S83, T13). A browser takes a page's context away when the GPU process
// resets, a driver times a draw out, or too many contexts are open; the owner saw five losses in the app's pane and the
// stars regime drawn black after them. What already happens, and is not duplicated here: three.js's WebGLRenderer
// listens for `webglcontextlost` on its canvas from before the context is made and calls `preventDefault()` on it -
// which is what lets the browser restore the context at all - and stops drawing (`render` returns while lost); on
// `webglcontextrestored` it re-initialises its whole GL state (its `initGLContext`: new properties, textures, attributes,
// programs), so every texture whose pixels are still on the CPU side (a DataTexture's `image.data`, a canvas), every
// geometry's attributes and every material's program are uploaded or compiled again on their next use, and every render
// target's framebuffer is made again the next time it is bound. What three cannot know, and the viewer does: which of its
// render targets hold pixels drawn once and kept (the march's and the region's targets re-march only when the camera or a
// setting moves), which raw GL objects it made outside three (the march's timer queries), and which extensions it enabled
// itself (EXT_float_blend for the wings' target). Those follow `generation`, which this watch counts up at each restore,
// after three's own listener has run (it was added first). And the frame loop is paused while the context is lost, so no
// frame records a camera as marched that was never drawn.

/** The context's state as the viewer sees it: lost or not, how many restores so far, how many losses. */
export interface ContextState {
  /** True from a `webglcontextlost` event until the `webglcontextrestored` after it. */
  lost: boolean;
  /** 0 until the first restore; one more at each. Whatever the viewer keeps on the GPU is rebuilt when it moves. */
  generation: number;
  /** The losses seen on this canvas. */
  losses: number;
}

export interface ContextWatch {
  readonly state: ContextState;
  subscribe(listener: () => void): () => void;
}

const watches = new WeakMap<EventTarget, ContextWatch>();

/**
 * The one watch of a canvas's context: made on the first call for that canvas, its two listeners never removed (the
 * canvas's life is the renderer's). Its state is replaced, never changed in place, so a snapshot read by React is stable.
 */
export function contextWatch(canvas: EventTarget): ContextWatch {
  const kept = watches.get(canvas);
  if (kept) return kept;
  const listeners = new Set<() => void>();
  const watch = {
    state: { lost: false, generation: 0, losses: 0 } as ContextState,
    subscribe(listener: () => void) {
      listeners.add(listener);
      return () => {
        listeners.delete(listener);
      };
    },
  };
  const tell = (next: ContextState) => {
    watch.state = next;
    for (const listener of [...listeners]) listener();
  };
  canvas.addEventListener("webglcontextlost", () => tell({ ...watch.state, lost: true, losses: watch.state.losses + 1 }));
  canvas.addEventListener("webglcontextrestored", () => tell({ ...watch.state, lost: false, generation: watch.state.generation + 1 }));
  watches.set(canvas, watch);
  return watch;
}

/** The status line's words while the context is lost (GalaxyView), in the form of the app's other status lines. */
export const CONTEXT_LOST_WORDS = "Context lost · the graphics context was lost; drawing again";

/**
 * The context's state on a renderer's canvas (`gl.domElement`), re-rendering on a loss and on a restore. The canvas is
 * passed in rather than read from react-three-fiber here, so this file stays free of it (the e2e spec imports the words).
 */
export function useContextState(canvas: EventTarget): ContextState {
  const watch = contextWatch(canvas);
  return useSyncExternalStore(watch.subscribe, () => watch.state, () => watch.state);
}

/** The restores so far on a renderer's canvas: a dependency for what the viewer keeps on the GPU itself. */
export function useContextGeneration(canvas: EventTarget): number {
  return useContextState(canvas).generation;
}
