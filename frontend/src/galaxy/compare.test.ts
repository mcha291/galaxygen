import { describe, expect, it } from "vitest";

import { orbitPosition } from "./capture";
import { arcsecOf, compareCaption, kpcPerPicturePixel, kpcPerPixel, pictureCaption, pictureWidthPx } from "./compare";

// NGC 4414's stand (D213 ruling 5): 55° from face-on, 20 kpc framed through a 5° lens, on a canvas 1000 px high,
// so 40 kpc over 1000 pixels at the centre: 25 px per kpc.
const position = orbitPosition({ inclination_deg: 55, azimuth_deg: 0, radius_kpc: 20 }, 5);
const view = { pxPerKpc: 25, fov: 5, position, target: [0, 0, 0] };

describe("compare with a picture: what the render's caption states (T16 ii)", () => {
  it("the scale at the centre, in kiloparsecs per pixel and as an angle at the template's distance", () => {
    expect(kpcPerPixel(25)).toBeCloseTo(0.04, 12);
    // 40 pc at 17.7 Mpc: 0.04 / 17 700 rad = 0.466 arcsec.
    expect(arcsecOf(0.04, 17.7)).toBeCloseTo(0.4661, 4);
    expect(arcsecOf(1, 1)).toBeCloseTo(206.265, 3); // 1 kpc at 1 Mpc
  });

  it("names the template, the filter set, the scale and the inclination, read from the view as it stands", () => {
    const caption = compareCaption(view, { label: "NGC 4414", filters: "HST WFC3", distanceMpc: 17.7 });
    expect(caption.galaxy).toBe("NGC 4414");
    expect(caption.filters).toBe("HST WFC3");
    expect(caption.kpcPerPixel).toBeCloseTo(0.04, 12);
    expect(caption.arcsecPerPixel).toBeCloseTo(0.4661, 4);
    expect(caption.inclinationDeg).toBeCloseTo(55, 9);
    expect(caption.fovDeg).toBe(5);
    expect(caption.lines).toEqual([
      "Render: NGC 4414, through the HST WFC3 filters.",
      "0.04 kpc per pixel at the centre (0.466″ at 17.7 Mpc) · inclination 55.0° · 5° lens",
    ]);
  });

  it("follows the camera: an orbit changes the inclination, a zoom the scale", () => {
    const edgeOn = orbitPosition({ inclination_deg: 90, azimuth_deg: 40, radius_kpc: 5 }, 45);
    const caption = compareCaption({ pxPerKpc: 100, fov: 45, position: edgeOn, target: [0, 0, 0] }, { label: "Milky Way", filters: "RGB", distanceMpc: null });
    expect(caption.inclinationDeg).toBeCloseTo(90, 9);
    expect(caption.kpcPerPixel).toBeCloseTo(0.01, 12);
    expect(caption.lines[1]).toBe("0.01 kpc per pixel at the centre · inclination 90.0° · 45° lens");
  });

  it("states no angle where the template states no distance, and says so of an edited or a template-less galaxy", () => {
    const milkyWay = compareCaption(view, { label: "Milky Way · edited", filters: "RGB", distanceMpc: null });
    expect(milkyWay.arcsecPerPixel).toBeNull();
    expect(milkyWay.lines[0]).toBe("Render: Milky Way · edited, through the RGB filters.");
    expect(milkyWay.lines[1]).not.toMatch(/Mpc/);
    const none = compareCaption(view, { label: null, filters: "RGB", distanceMpc: null });
    expect(none.galaxy).toBe("the default galaxy");
  });

  it("a picture of known pixels at a stated scale is drawn at the render's kpc across (T16 ii, S83)", () => {
    // An 800-pixel picture at 0.05 kpc per pixel is 40 kpc wide. The left pane is 600 CSS px across 45 kpc at its orbit
    // target: 13.33 px per kpc, so the picture is drawn 533.33 px wide - 40 of the pane's 45 kpc.
    const pxPerKpc = 600 / 45;
    const kpc = kpcPerPicturePixel({ unit: "kpc", perPixel: 0.05 })!;
    expect(pictureWidthPx(800, kpc, pxPerKpc)).toBeCloseTo(533.3333, 3);
    expect(pictureWidthPx(800, kpc, pxPerKpc) / pxPerKpc).toBeCloseTo(40, 9);
    // The same kind of picture stated in arcseconds at NGC 4414's distance: 0.5″ per pixel at 17.7 Mpc is 42.9 pc.
    const arcsec = kpcPerPicturePixel({ unit: "arcsec", perPixel: 0.5, distanceMpc: 17.7 })!;
    expect(arcsec).toBeCloseTo(0.042906, 5);
    expect(arcsecOf(arcsec, 17.7)).toBeCloseTo(0.5, 12); // the inverse of the render's own caption
    expect(pictureWidthPx(1000, arcsec, 25)).toBeCloseTo(1000 * arcsec * 25, 9);
    // A zoom doubles the pixels per kpc: the picture doubles with the render.
    expect(pictureWidthPx(800, kpc, 2 * pxPerKpc)).toBeCloseTo(2 * 533.3333, 3);
  });

  it("no scale is drawn from a statement that is not one, and the caption says so", () => {
    expect(kpcPerPicturePixel({ unit: "kpc", perPixel: 0 })).toBeNull();
    expect(kpcPerPicturePixel({ unit: "kpc", perPixel: Number.NaN })).toBeNull();
    expect(kpcPerPicturePixel({ unit: "arcsec", perPixel: 0.5, distanceMpc: 0 })).toBeNull();
    expect(pictureCaption("m100.png", "", { unit: "kpc", perPixel: 0 }, 800)).toEqual([
      "Picture: m100.png, band not stated.",
      "Scale not stated: drawn to fit the pane, not to the render's scale.",
    ]);
    expect(pictureCaption("m100.png", " HST F814W ", { unit: "kpc", perPixel: 0.05 }, 800)).toEqual([
      "Picture: m100.png, in HST F814W.",
      "0.05 kpc per pixel · 800 px = 40 kpc across",
    ]);
    expect(pictureCaption("n4414.jpg", "V", { unit: "arcsec", perPixel: 0.5, distanceMpc: 17.7 }, null)[1]).toBe("0.5″ per pixel at 17.7 Mpc (0.0429 kpc)");
  });

  it("measures the inclination about what the camera looks at, not about the centre", () => {
    const panned = compareCaption({ pxPerKpc: 25, fov: 5, position: [position[0] + 3, position[1], position[2] - 2], target: [3, 0, -2] }, { label: null, filters: "RGB", distanceMpc: null });
    expect(panned.inclinationDeg).toBeCloseTo(55, 9);
  });
});
