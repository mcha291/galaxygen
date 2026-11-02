import { type ReactElement, type ReactNode, cloneElement, isValidElement, useId, useState } from "react";

import { cx } from "./cx";
import styles from "./Tooltip.module.css";

interface Props {
  /** One line, no title, no rich content. */
  content: ReactNode;
  placement?: "top" | "bottom";
  /** Where the line stands against its control: centred (the design's), or from its start or end edge where a panel's
   * side would clip it. */
  align?: "center" | "start" | "end";
  /** The control it explains; it is described by the line (aria-describedby). */
  children: ReactElement<{ "aria-describedby"?: string }>;
  /** A class for the anchor that holds the control and the line (to size it in its row). */
  className?: string;
}

/**
 * The design system's Tooltip: a one-line explanation shown while its control is hovered or focused, gone on
 * Escape. The control is described by it, so the line is read without the pointer.
 */
export function Tooltip({ content, placement = "top", align = "center", children, className }: Props) {
  const id = useId();
  const [dismissed, setDismissed] = useState(false);
  const described = isValidElement(children)
    ? cloneElement(children, { "aria-describedby": cx(children.props["aria-describedby"], id) })
    : children;
  return (
    <span
      className={cx(styles.anchor, className)}
      data-dismissed={dismissed || undefined}
      onKeyDown={(e) => {
        if (e.key === "Escape") setDismissed(true);
      }}
      onMouseLeave={() => setDismissed(false)}
      onBlur={() => setDismissed(false)}
    >
      {described}
      <span id={id} role="tooltip" className={cx(styles.tip, styles[placement], styles[align])}>
        {content}
      </span>
    </span>
  );
}
