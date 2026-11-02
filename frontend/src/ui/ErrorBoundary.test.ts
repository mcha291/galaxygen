import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { ErrorBoundary } from "./ErrorBoundary";
import { attrs } from "./testing";

/** The boundary's drawing in a given state (the server renderer runs no boundary of its own, so its render is called). */
function drawn(state: Partial<ErrorBoundary["state"]>): string {
  const boundary = new ErrorBoundary({ resetKey: "galaxy", children: h("p", null, "the view") });
  boundary.state = { ...boundary.state, ...state };
  return renderToStaticMarkup(h("div", null, boundary.render()));
}

describe("the error boundary (T17: the fault in the design system's Dialog)", () => {
  it("draws its children while nothing has failed", () => {
    expect(drawn({})).toBe("<div><p>the view</p></div>");
  });

  it("says a fault in an alert dialog with the next action, and in a line where the view stood", () => {
    const html = drawn({ error: new Error("no field star_age") });
    expect(attrs(html, "role")).toEqual(["alertdialog"]);
    expect(html).toContain("This view failed: no field star_age. Change the checkpoint or view to retry.");
    expect(html).toContain(">Retry</button>");
    expect(attrs(html, "aria-label")).toContain("Close");
  });

  it("once the dialog is closed, keeps the line, now the alert", () => {
    const html = drawn({ error: new Error("x"), dismissed: true });
    expect(html).not.toContain("alertdialog");
    expect(attrs(html, "role")).toEqual(["alert"]);
  });

  it("clears a fault, and opens the dialog again, at a new key", () => {
    const state = { error: new Error("x"), key: "galaxy", dismissed: true };
    expect(ErrorBoundary.getDerivedStateFromProps({ resetKey: "science", children: null }, state)).toEqual({ error: null, key: "science", dismissed: false });
    expect(ErrorBoundary.getDerivedStateFromProps({ resetKey: "galaxy", children: null }, state)).toBeNull();
    expect(ErrorBoundary.getDerivedStateFromError(new Error("y")).dismissed).toBe(false);
  });
});
