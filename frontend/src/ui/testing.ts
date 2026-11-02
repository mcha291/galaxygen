import { readFileSync } from "node:fs";

// What the design system's component tests share (vitest only; nothing the app imports). The tests run in node
// (vite.config.ts `environment: "node"`), so a component is rendered to markup by react-dom/server and its
// stylesheet read as text; behaviour that needs events is a pure function each component exports and the tests call.

/** A stylesheet of src/ui, as text. */
export function stylesheet(name: string): string {
  return readFileSync(new URL(name, import.meta.url), "utf-8");
}

/** The declarations of the top-level rule written for exactly `selector` (at a line's start, outside any media query). */
export function cssRule(sheet: string, selector: string): string {
  const escaped = selector.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const m = new RegExp(`(^|\\n)${escaped}\\s*\\{([^}]*)\\}`).exec(sheet);
  if (!m) throw new Error(`no rule ${selector}`);
  return m[2];
}

/** The colour literals a stylesheet holds - hex, rgb(), hsl() - outside its comments: a component's colours are the tokens'. */
export function colourLiterals(sheet: string): string[] {
  const code = sheet.replace(/\/\*[\s\S]*?\*\//g, "");
  return code.match(/#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?)\(/g) ?? [];
}

/** A class attribute's CSS Module names as written in the stylesheet: vitest writes each as `_<name>_<hash>`. */
function local(attribute: string): string {
  return attribute
    .split(/\s+/)
    .filter(Boolean)
    .map((c) => /^_(.+)_[0-9a-f]+$/.exec(c)?.[1] ?? c)
    .join(" ");
}

/** The class names on the first element of some markup, as the stylesheet writes them. */
export function classOf(html: string): string {
  return local(/^<[a-z]+[^>]*?\sclass="([^"]*)"/.exec(html)?.[1] ?? "");
}

/** Every element's class names in some markup, in order, as the stylesheet writes them. */
export function classes(html: string): string[] {
  return attrs(html, "class").map(local);
}

/** Every value of `attr` in some markup, in order. */
export function attrs(html: string, attr: string): string[] {
  return [...html.matchAll(new RegExp(`\\s${attr}="([^"]*)"`, "g"))].map((m) => m[1]);
}
