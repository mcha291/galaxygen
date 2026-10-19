// The GPU's time for the march (S67, BUILD_III V8; D227 R6; T14): a WebGL2 timer query
// (EXT_disjoint_timer_query_webgl2) around the march's render call, read back a frame or more later when the GPU
// has the answer. Where the extension is absent (a browser that withholds it, WebGL1) there is no number, and the
// readout says so rather than showing the CPU's side as the GPU's. An instrument (rule B1): it times, and draws nothing.

/** What the extension adds, by its constants (the WebGL registry's values). */
interface TimerExt {
  TIME_ELAPSED_EXT: number;
  GPU_DISJOINT_EXT: number;
}

type Gl2 = Pick<
  WebGL2RenderingContext,
  "getExtension" | "createQuery" | "deleteQuery" | "beginQuery" | "endQuery" | "getQueryParameter" | "getParameter" | "QUERY_RESULT" | "QUERY_RESULT_AVAILABLE"
>;

export interface GpuTimer {
  /** Whether the extension is there: false and every call is a no-op. */
  readonly available: boolean;
  /** Around the work to time: one query open at a time (a begin while one is open is skipped). */
  begin(): void;
  end(): void;
  /** The latest finished query's time, ms, or null while none has come back (or with no extension). */
  poll(): number | null;
  dispose(): void;
}

/** A timer on `ctx`, or an unavailable one where the context is not WebGL2 or withholds the extension. */
export function gpuTimer(ctx: Partial<Gl2> | null | undefined): GpuTimer {
  const ext = (ctx?.getExtension?.("EXT_disjoint_timer_query_webgl2") ?? null) as TimerExt | null;
  if (!ctx || !ext || typeof ctx.createQuery !== "function") {
    return { available: false, begin() {}, end() {}, poll: () => null, dispose() {} };
  }
  const gl = ctx as Gl2;
  const pending: WebGLQuery[] = [];
  let open: WebGLQuery | null = null;
  let last: number | null = null;
  return {
    available: true,
    begin() {
      if (open) return;
      open = gl.createQuery();
      if (open) gl.beginQuery(ext.TIME_ELAPSED_EXT, open);
    },
    end() {
      if (!open) return;
      gl.endQuery(ext.TIME_ELAPSED_EXT);
      pending.push(open);
      open = null;
    },
    poll() {
      // A disjoint event (a context switch, a clock change) spoils every query in flight: they are dropped.
      const disjoint = Boolean(gl.getParameter(ext.GPU_DISJOINT_EXT));
      while (pending.length > 0) {
        const q = pending[0];
        if (!disjoint && !gl.getQueryParameter(q, gl.QUERY_RESULT_AVAILABLE)) break;
        pending.shift();
        if (!disjoint) last = Number(gl.getQueryParameter(q, gl.QUERY_RESULT)) / 1e6;
        gl.deleteQuery(q);
      }
      return last;
    },
    dispose() {
      for (const q of pending) gl.deleteQuery(q);
      pending.length = 0;
    },
  };
}

/** The readout's words: the GPU's milliseconds, or that there are none. */
export function gpuWords(ms: number | null | undefined, available: boolean): string {
  if (!available) return "GPU time not available";
  return ms == null ? "GPU time: waiting" : `GPU ${ms.toFixed(1)} ms`;
}
