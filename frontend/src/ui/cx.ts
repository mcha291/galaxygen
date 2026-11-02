/** Join class names, dropping the absent ones: the design system's components take a `className` beside their own. */
export function cx(...names: (string | false | null | undefined)[]): string {
  return names.filter(Boolean).join(" ");
}
