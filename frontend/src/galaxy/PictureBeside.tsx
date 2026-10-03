import { useRef } from "react";

import styles from "./PictureBeside.module.css";

// "Compare with a picture" (T16 ii; S54, D213 ruling 7): a picture the user picks from disk, set beside the
// render at the same height. Nothing is bundled and nothing is sent: the file is shown through an object URL the
// browser makes for it, so it never leaves the page (BUILD_III section 7, ruling 5; rule D2 - no request here).

/** A picture chosen from disk: the object URL it is shown through and the file's name. */
export interface ComparePicture {
  url: string;
  name: string;
}

interface PickerProps {
  picture: ComparePicture | null;
  onPick(file: File): void;
  onDismiss(): void;
}

/** The control: choose an image file, choose another, or dismiss the one shown. Its buttons take the panel's own style. */
export function ComparePicker({ picture, onPick, onDismiss }: PickerProps) {
  const input = useRef<HTMLInputElement>(null);
  return (
    <>
      <input
        ref={input}
        type="file"
        accept="image/*"
        hidden
        aria-label="Picture to compare with"
        onChange={(e) => {
          const file = e.target.files?.[0];
          e.target.value = ""; // so the same file can be chosen again after a dismissal
          if (file) onPick(file);
        }}
      />
      <button type="button" title="Choose an image file from this computer to set beside the render. It stays in the browser." onClick={() => input.current?.click()}>
        {picture ? "another picture" : "compare with a picture"}
      </button>
      {picture && (
        <button type="button" title="Take the picture away" onClick={onDismiss}>
          dismiss
        </button>
      )}
    </>
  );
}

/** The picture's half of the stage: the image fitted to the render's height, its file name, and a way to dismiss it. */
export function ComparePane({ picture, onDismiss }: { picture: ComparePicture; onDismiss(): void }) {
  return (
    <figure className={styles.pane}>
      <img className={styles.image} src={picture.url} alt={`The picture chosen: ${picture.name}`} />
      <figcaption className={styles.caption}>
        <span className={styles.name}>Picture: {picture.name}</span>
        <button type="button" className={styles.close} onClick={onDismiss}>
          dismiss
        </button>
      </figcaption>
    </figure>
  );
}

/** Under the render: what it is (compare.ts compareCaption), so the two halves are each named. */
export function RenderCaption({ lines }: { lines: string[] }) {
  return (
    <div className={styles.renderCaption}>
      {lines.map((line) => (
        <div key={line}>{line}</div>
      ))}
    </div>
  );
}
