// T13 (S83): the renderer survives a lost WebGL context. The watch's state machine here; the forced loss on a real GPU
// - WEBGL_lose_context's loseContext() then restoreContext(), and the frame drawn after it - is e2e/context.spec.ts's.
import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import { CONTEXT_LOST_WORDS, contextWatch } from "./contextLoss";

const lost = () => new Event("webglcontextlost", { cancelable: true });
const restored = () => new Event("webglcontextrestored");

describe("the context's watch (T13)", () => {
  it("counts a loss, then a restore, and tells its listeners at each", () => {
    const canvas = new EventTarget();
    const watch = contextWatch(canvas);
    expect(watch.state).toEqual({ lost: false, generation: 0, losses: 0 });
    let told = 0;
    const stop = watch.subscribe(() => (told += 1));
    canvas.dispatchEvent(lost());
    expect(watch.state).toEqual({ lost: true, generation: 0, losses: 1 });
    canvas.dispatchEvent(restored());
    expect(watch.state).toEqual({ lost: false, generation: 1, losses: 1 });
    canvas.dispatchEvent(lost());
    canvas.dispatchEvent(restored());
    expect(watch.state).toEqual({ lost: false, generation: 2, losses: 2 });
    expect(told).toBe(4);
    stop();
    canvas.dispatchEvent(lost());
    expect(told).toBe(4);
  });

  it("is one watch per canvas, its state replaced at each event so a snapshot of it is stable", () => {
    const canvas = new EventTarget();
    const watch = contextWatch(canvas);
    expect(contextWatch(canvas)).toBe(watch);
    expect(contextWatch(new EventTarget())).not.toBe(watch);
    const before = watch.state;
    expect(watch.state).toBe(before); // no event, the same object: useSyncExternalStore reads it without re-rendering
    canvas.dispatchEvent(lost());
    expect(watch.state).not.toBe(before);
    expect(before).toEqual({ lost: false, generation: 0, losses: 0 });
  });

  it("does not take the loss's default itself: three.js does, and that is what lets the browser restore", () => {
    const canvas = new EventTarget();
    contextWatch(canvas);
    const event = lost();
    canvas.dispatchEvent(event);
    expect(event.defaultPrevented).toBe(false);
    // three's renderer, the dependency the viewer relies on: its listener prevents the default and re-initialises on the
    // restore (WebGLRenderer onContextLost / onContextRestore, three r186). A three without it fails here, by name.
    const three = readFileSync(new URL("../../node_modules/three/build/three.module.js", import.meta.url), "utf-8");
    const onLost = three.slice(three.indexOf("function onContextLost( event ) {"), three.indexOf("function onContextRestore("));
    expect(onLost).toContain("event.preventDefault();");
    const onRestore = three.slice(three.indexOf("function onContextRestore("), three.indexOf("function onContextCreationError("));
    expect(onRestore).toContain("initGLContext();");
    expect(three).toContain("canvas.addEventListener( 'webglcontextlost', onContextLost, false );");
  });

  it("says what happened in the form of the app's other status lines", () => {
    expect(CONTEXT_LOST_WORDS).toMatch(/^Context lost · .*drawing again$/);
  });
});
