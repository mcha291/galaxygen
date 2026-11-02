import { useState } from "react";

import { formatNumber } from "../workflow/logic";
import { type PictureScale, kpcPerPicturePixel, pictureCaption, pictureWidthPx } from "./compare";
import { scaleBar } from "./zoom";
import styles from "./PictureBeside.module.css";

// "Compare with a picture" (T16 ii; S54, D213 ruling 7; S83 at a stated band and scale): a picture the user picks
// from disk, drawn in the comparison's right pane at the scale of the render beside it. Nothing is bundled and nothing
// is sent: the file is shown through an object URL the browser makes for it, so it never leaves the page (BUILD_III
// section 7, ruling 5; rule D2 - no request here). The browser resamples it; nothing here is physics (rule D5).

/** A picture chosen from disk: the object URL it is shown through and the file's name. */
export interface ComparePicture {
  url: string;
  name: string;
}

/**
 * The picture's pane: the image centred on the pane's centre - where the render beside it has its orbit target - at
 * the width its stated scale gives at the render's pixels per kpc (compare.ts pictureWidthPx), so the two panes are the
 * same kpc across; the render's scale bar under it; the band and the scale as its caption. Without a scale it is fitted
 * to the pane and says so, with no scale bar.
 */
export function PictureFrame({ picture, band, scale, pxPerKpc }: { picture: ComparePicture | null; band: string; scale: PictureScale; pxPerKpc: number | null }) {
  // The picture's own width in pixels, read when it has loaded (and again for another file).
  const [natural, setNatural] = useState<{ url: string; width: number } | null>(null);
  const imagePx = natural && picture && natural.url === picture.url ? natural.width : null;
  const kpc = kpcPerPicturePixel(scale);
  const width = kpc !== null && imagePx !== null && pxPerKpc !== null ? pictureWidthPx(imagePx, kpc, pxPerKpc) : null;
  const bar = kpc !== null && pxPerKpc !== null ? scaleBar(pxPerKpc) : null;
  return (
    <figure className={styles.pane}>
      {picture ? (
        <img
          className={width === null ? styles.fitted : styles.scaled}
          style={width === null ? undefined : { width }}
          src={picture.url}
          alt={`The picture chosen: ${picture.name}`}
          onLoad={(e) => setNatural({ url: picture.url, width: e.currentTarget.naturalWidth })}
        />
      ) : (
        <p className={styles.empty}>Choose a picture file above: PNG or JPEG, from this computer. It stays in the browser.</p>
      )}
      {bar && (
        <div className={styles.scale}>
          <div className={styles.scaleBar} style={{ width: bar.px }} />
          <div>{formatNumber(bar.kpc, 2)} kpc</div>
        </div>
      )}
      {picture && <RenderCaption lines={pictureCaption(picture.name, band, scale, imagePx)} />}
    </figure>
  );
}

/** Under a pane: what it is (compare.ts compareCaption, pictureCaption), so the two panes are each named. */
export function RenderCaption({ lines }: { lines: string[] }) {
  return (
    <div className={styles.renderCaption}>
      {lines.map((line) => (
        <div key={line}>{line}</div>
      ))}
    </div>
  );
}
