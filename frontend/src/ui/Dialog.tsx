import { X } from "lucide-react";
import { type KeyboardEvent, type ReactNode, useEffect, useId, useRef } from "react";
import { createPortal } from "react-dom";

import { IconButton } from "./IconButton";
import styles from "./Dialog.module.css";

const FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

/**
 * Where Tab moves focus inside an open dialog: from the last focusable element forward to the first, from the first
 * (or the panel itself, index -1) backward to the last; null where the browser's own move stays inside.
 */
export function trappedFocus(count: number, active: number, back: boolean): number | null {
  if (count === 0) return -1; // nothing to move to: the panel keeps the focus
  if (back) return active <= 0 ? count - 1 : null;
  return active < 0 || active === count - 1 ? 0 : null;
}

interface Props {
  open: boolean;
  /** The dialog's heading (h3 size); it names the dialog. */
  title: ReactNode;
  /** The mono micro-label above the title. */
  label?: ReactNode;
  /** The actions at the bottom right: verbs, one or two words. */
  footer?: ReactNode;
  /** The panel's largest width, px (the design's 480). */
  width?: number;
  /** "alertdialog" for a fault the reader must answer; "dialog" otherwise. */
  role?: "dialog" | "alertdialog";
  /** Close: the close button, Escape and a press on the scrim. */
  onClose(): void;
  children?: ReactNode;
}

/**
 * The design system's Dialog: a modal overlay, the only element that blurs what is behind it (--scrim with
 * --blur-md, an 8 px radius and --shadow-3). Escape, the close button and the scrim close it; Tab stays inside while it
 * is open, and the focus goes back where it was when it closes. Drawn into the document's body, so no panel's own
 * blur or transform holds it.
 */
export function Dialog({ open, title, label, footer, width = 480, role = "dialog", onClose, children }: Props) {
  const heading = useId();
  const panel = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!open) return;
    const before = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    panel.current?.focus();
    return () => before?.focus();
  }, [open]);
  if (!open) return null;

  const onKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
    if (e.key === "Escape") {
      e.stopPropagation();
      onClose();
      return;
    }
    if (e.key !== "Tab" || !panel.current) return;
    const items = [...panel.current.querySelectorAll<HTMLElement>(FOCUSABLE)];
    const to = trappedFocus(items.length, items.indexOf(document.activeElement as HTMLElement), e.shiftKey);
    if (to === null) return;
    e.preventDefault();
    (to < 0 ? panel.current : items[to]).focus();
  };

  const overlay = (
    <div className={styles.scrim} onClick={onClose}>
      <div
        ref={panel}
        role={role}
        aria-modal="true"
        aria-labelledby={heading}
        tabIndex={-1}
        className={styles.panel}
        style={{ maxWidth: width }}
        onClick={(e) => e.stopPropagation()}
        onKeyDown={onKeyDown}
      >
        <header className={styles.header}>
          <div className={styles.titles}>
            {label && <div className={styles.label}>{label}</div>}
            <div id={heading} className={styles.title}>
              {title}
            </div>
          </div>
          <IconButton label="Close" size="sm" onClick={onClose}>
            <X aria-hidden />
          </IconButton>
        </header>
        <div className={styles.body}>{children}</div>
        {footer && <footer className={styles.footer}>{footer}</footer>}
      </div>
    </div>
  );
  // Without a document (the server renderer, the unit tests) it is drawn where it stands.
  return typeof document === "undefined" ? overlay : createPortal(overlay, document.body);
}
