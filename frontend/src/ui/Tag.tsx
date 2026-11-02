import { X } from "lucide-react";
import type { HTMLAttributes } from "react";

import { cx } from "./cx";
import styles from "./Tag.module.css";

interface Props extends HTMLAttributes<HTMLSpanElement> {
  /** Removes the tag: a small button after the text, named by `removeLabel`. */
  onRemove?(): void;
  /** The remove button's accessible name (the design's "Remove"; name the thing removed where there are several). */
  removeLabel?: string;
  /** A data colour for the swatch before the text - a token, e.g. SPECTRAL_COLORS.K - never a colour of the viewer's own. */
  color?: string;
}

/** The design system's Tag: a removable metadata chip - filters, spectral classes, survey labels. Mono, 22 px, hairline. */
export function Tag({ onRemove, removeLabel = "Remove", color, className, children, ...rest }: Props) {
  return (
    <span className={cx(styles.tag, className)} {...rest}>
      {color && <span className={styles.swatch} style={{ background: color }} aria-hidden />}
      {children}
      {onRemove && (
        <button type="button" className={styles.remove} aria-label={removeLabel} onClick={onRemove}>
          <X aria-hidden />
        </button>
      )}
    </span>
  );
}
