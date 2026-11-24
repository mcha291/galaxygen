// The arms' sparkle's drawing (BUILD_VIII row 108): armsSparkle.ts's points through FluxPoints, on the knots' gain (the
// field's scale and exposure), dimmed by the march's dust as the knots are. The buffers are built once per (arm map,
// shaping values, template), never per frame. Loaded lazily by arms.ts.
//
// S106 (the Milky Way's grain): the points are drawn in two tiers - the fine grain on the small sprite and the
// brightest share (`sparklebig`) on a larger one (`sparklebigsize`) - so the arms' grain has sizes, not one dot.
// A share of 0 draws every point on the small sprite, as S105 did.

import { useFrame } from "@react-three/fiber";
import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import type { Group } from "three";
import { FluxPoints, type PointDust } from "../FluxPoints";
import { shapeOf } from "./arms";
import { sparkleFlux, sparkleTiers, tierIndices } from "./armsSparkle";
import { ILL_MAP, type IllLayerProps } from "./feature";
import { illFieldDrawn, objectToken, requestSparkle, setSparkleDrawnFor, sparkleHeld } from "./illMapClient";
import { illChannelCurrent } from "./index";
import { type SparklePoints, sparkleKey, sparkleReadsLanes, sparkleShown } from "./sparkleJob";

/** The sparkle's blue-white at full share (over the white point). */
const SPARKLE_BLUE: readonly [number, number, number] = [0.72, 0.98, 1.2];
/** S107: the sparkle's cyan-teal, mixed into the blue-white by the arms' `cyan` share. */
const SPARKLE_CYAN: readonly [number, number, number] = [0.66, 1.1, 1.16];
/** S109 (A2): the bar's grain colour (arms.sparklebarcream), a warm cream-white. */
const BAR_CREAM: readonly [number, number, number] = [1.18, 1.0, 0.72];
/** S110 (A1, arms.sparklelav): the fine grain's lavender-white, the goal's disc grain. */
const SPARKLE_LAV: readonly [number, number, number] = [0.97, 0.95, 1.12];

/** The members `idx` of a flat buffer of `width` values per point. */
function pick(values: Float32Array, idx: Uint32Array, width: number): Float32Array {
  const out = new Float32Array(idx.length * width);
  for (let k = 0; k < idx.length; k++) for (let c = 0; c < width; c++) out[k * width + c] = values[idx[k] * width + c];
  return out;
}

/** The shared map's texture as the layer reads it: its RGBA bytes and the planes it was composed from (index.ts). */
type MapTexture = { image?: { data?: ArrayLike<number>; width?: number; height?: number }; userData?: { illPlanes?: (Uint8Array | null)[] } };

export default function ArmsSparkle({ params, runtime, context, knotsGain, dust }: IllLayerProps) {
  // S107: the points are built by the map worker (sparkleJob.ts, illMapClient.ts requestSparkle) - the same build the
  // layer made here, moved off the main thread - keyed on exactly what it reads: the frame, the arms' parameters and,
  // while the sparkle keeps off the lanes (S106), the lanes' own plane in the composed map (not the map's texture, which
  // moves with any channel). The last points stay drawn until the new ones arrive.
  const mapTex = sparkleReadsLanes(params) ? ((runtime as { uniforms?: Record<string, { value: unknown }> }).uniforms?.illMapTex?.value as MapTexture | undefined) : undefined;
  const img = mapTex?.image;
  const composed = !!img?.data && img.width === ILL_MAP.width && img.height === ILL_MAP.height;
  const lanesPlane = composed ? (mapTex?.userData?.illPlanes?.[0] ?? null) : null;
  const key = sparkleKey(params, context.frame, objectToken(context.frame), context.template, composed ? (lanesPlane ? `plane:${objectToken(lanesPlane)}` : "zeros") : "none");
  // The galaxy the points are for (rule D1): the last points stay drawn only on the same galaxy (a slider's move).
  const galaxy = `${objectToken(context.frame)}:${context.template}`;
  const [arrived, setArrived] = useState<{ key: string; galaxy: string; points: SparklePoints | null } | null>(null);
  const held = sparkleHeld(key);
  // While the lanes' plane for the parameters drawn is still being built, nothing is asked: the points for the new
  // lanes are built once, when it is in the map (not first over the previous lanes, as the layer did before).
  const lanesReady = !sparkleReadsLanes(params) || illChannelCurrent(mapTex ?? null, 0, context);
  useEffect(() => {
    if (held !== undefined || !lanesReady) return;
    const lanes = composed ? { plane: lanesPlane, rgba: img!.data! } : null;
    return requestSparkle(key, params, context, lanes, (points) => setArrived({ key, galaxy, points }));
  }, [key, lanesReady]); // eslint-disable-line react-hooks/exhaustive-deps -- the key names every input
  const points = sparkleShown(held, arrived, galaxy);
  // The probe's check of rule D1: the template these points were built for.
  const [owner] = useState(() => ({}));
  const shownFor = points ? context.template : null;
  // S107 (MW2, rule D1): drawn only while the field drawn is their galaxy, read at each frame before the render (the
  // canvas's own tree commits after GalaxyTab's: for a frame after a template switch it still held the last galaxy's
  // points while the field and the map were already the new one's). No view reporting a field (vitest): drawn.
  const showNow = useCallback(() => {
    const field = illFieldDrawn();
    return shownFor !== null && (field === undefined || field === shownFor);
  }, [shownFor]);
  const group = useRef<Group>(null);
  useFrame(() => {
    if (group.current) group.current.visible = showNow();
  });
  useLayoutEffect(() => {
    setSparkleDrawnFor(owner, shownFor === null ? null : () => (showNow() ? shownFor : null));
    return () => setSparkleDrawnFor(owner, null);
  }, [owner, shownFor, showNow]);
  const blue = params.sparkleblue ?? 0.7;
  const cyan = Math.min(1, Math.max(0, params.cyan ?? 0));
  const base = params.sparklegain ?? 2e4;
  const start = shapeOf(params, context.frame).start;
  const h = context.frame?.header.scalars.thin_disc_scale_length;
  const scale = (typeof h === "number" && h > 0 ? h : 2.5) * (params.sparklefall ?? 1);
  const flux = useMemo(() => {
    if (!points) return null;
    const c = SPARKLE_BLUE.map((v, k) => 1 + (v + (SPARKLE_CYAN[k] - v) * cyan - 1) * blue) as [number, number, number];
    const f = sparkleFlux(points.weight, points.radius, base, c, start, scale);
    // S109 (A2): the bar's points toward its cream (the same light: the colour's luminance kept).
    const cream = points.cream;
    if (cream) {
      const lc = 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2];
      const lk = 0.3 * BAR_CREAM[0] + 0.59 * BAR_CREAM[1] + 0.11 * BAR_CREAM[2];
      const k = BAR_CREAM.map((v, ch) => (v * lc) / lk / c[ch]);
      for (let i = 0; i < cream.length; i++) {
        const t = cream[i];
        if (t > 0) for (let ch = 0; ch < 3; ch++) f[3 * i + ch] *= 1 + (k[ch] - 1) * t;
      }
    }
    return f;
  }, [points, blue, cyan, base, start, scale]);
  const bigShare = params.sparklebig ?? 0;
  // S110 (A1): the fine tier's colour toward the goal's lavender-white by this share (its luminance kept); the bright
  // tier - the clumps' cores - keeps the blue-white.
  const lav = Math.min(1, Math.max(0, params.sparklelav ?? 0));
  const tiers = useMemo(() => {
    if (!points || !flux) return null;
    // S110 (A2): the field stars (the buffers' last `field` points) always on the fine sprite, and not counted in the
    // bright share (the arms' bright tier is as it was without them).
    const nField = points.field ?? 0;
    const t = nField > 0 ? new Uint8Array(points.weight.length) : sparkleTiers(points.weight, bigShare);
    if (nField > 0) t.set(sparkleTiers(points.weight.subarray(0, points.weight.length - nField), bigShare));
    return [0, 1].map((tier) => {
      const idx = tierIndices(t, tier);
      if (idx.length === 0) return null;
      const f = pick(flux, idx, 3);
      if (tier === 0 && lav > 0) {
        const c = SPARKLE_BLUE.map((v, k) => 1 + (v + (SPARKLE_CYAN[k] - v) * cyan - 1) * blue);
        const lc = 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2];
        const ll = 0.3 * SPARKLE_LAV[0] + 0.59 * SPARKLE_LAV[1] + 0.11 * SPARKLE_LAV[2];
        const k = SPARKLE_LAV.map((v, ch) => 1 + ((v * lc) / ll / c[ch] - 1) * lav);
        for (let i = 0; i < idx.length; i++) for (let ch = 0; ch < 3; ch++) f[3 * i + ch] *= k[ch];
      }
      return { positions: pick(points.positions, idx, 3), flux: f };
    });
  }, [points, flux, bigShare, lav, blue, cyan]);
  if (!tiers) return null;
  const sizes = [params.sparklesize ?? 1.5, params.sparklebigsize ?? 3];
  return (
    <group ref={group} visible={showNow()}>
      {tiers.map((t, i) =>
        t ? (
          <FluxPoints
            key={i}
            positions={t.positions}
            flux={t.flux}
            gain={knotsGain}
            psf={null}
            spriteSize={sizes[i]}
            illCap={params.sparklecap ?? 0}
            dust={(dust as PointDust | null) ?? null}
            ill={runtime as never}
          />
        ) : null,
      )}
    </group>
  );
}
