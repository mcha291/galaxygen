import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import { DRAWER_WIDTH_PX, regimePlace } from "./drawerLayout";

// #190 (S82): the regime caption stands left of the edit drawer while it is open. The rule is CSS, so the test
// holds the two stylesheets to one number - the drawer's width - and the class chosen to the drawer's state.

const css = (name: string) => readFileSync(new URL(name, import.meta.url), "utf-8");

/** The declarations of the top-level rule for `selector`: written at the line's start, outside any media query
 *  (whose rules are indented). */
function rule(sheet: string, selector: string): string {
  const m = new RegExp(`(^|\\n)${selector.replace(".", "\\.")}\\s*\\{([^}]*)\\}`).exec(sheet);
  if (!m) throw new Error(`no rule ${selector}`);
  return m[2];
}

describe("the regime caption and the edit drawer (#190)", () => {
  it("moves only while the drawer is open, and by the stage it is drawn over", () => {
    expect(regimePlace(false, false)).toBe("home");
    expect(regimePlace(false, true)).toBe("home");
    expect(regimePlace(true, false)).toBe("besideDrawer");
    expect(regimePlace(true, true)).toBe("besideDrawerHalf");
  });

  it("is shifted by the drawer's own width and inset", () => {
    const drawer = rule(css("../App.module.css"), ".editDrawer");
    expect(drawer).toMatch(new RegExp(`\\bwidth:\\s*${DRAWER_WIDTH_PX}px;`));
    expect(drawer).toMatch(/\bright:\s*var\(--space-4\);/);
    const tab = css("./GalaxyTab.module.css");
    expect(rule(tab, ".besideDrawer")).toMatch(new RegExp(`\\bright:\\s*calc\\(${DRAWER_WIDTH_PX}px \\+ var\\(--space-4\\)\\);`));
    expect(rule(tab, ".besideDrawerHalf")).toMatch(
      new RegExp(`\\bright:\\s*max\\(0px, calc\\(${DRAWER_WIDTH_PX}px \\+ var\\(--space-4\\) - 100%\\)\\);`),
    );
    // The caption's home stays where it was: closed, nothing moves (the picture test's captures).
    expect(rule(tab, ".regime")).toMatch(/\bright:\s*0;/);
  });

  it("stays home on phones, where the drawer is a bottom sheet", () => {
    const phones = css("./GalaxyTab.module.css").split("@media (max-width: 640px)").slice(1).join("");
    expect(phones).toMatch(/\.besideDrawer,\s*\.besideDrawerHalf\s*\{\s*right:\s*0;/);
    const app = css("../App.module.css").split("@media (max-width: 640px)")[1];
    expect(app).toMatch(/\.editDrawer\s*\{[^}]*bottom:\s*var\(--space-4\)/);
  });
});
