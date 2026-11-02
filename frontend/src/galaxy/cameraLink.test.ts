import { describe, expect, it } from "vitest";

import { type CameraPose, CameraLink, type LinkedView, joinLink } from "./cameraLink";

/** A pane's camera as the orbit controls are: a write moves it and tells its listeners, as controls.update() does. */
class Pane implements LinkedView {
  private listeners = new Set<() => void>();
  changes = 0;
  constructor(public pose: CameraPose) {}
  read(): CameraPose {
    return { position: [...this.pose.position], target: [...this.pose.target] };
  }
  write(pose: CameraPose): void {
    this.move(pose);
  }
  /** A drag, a wheel, the zoom slider: the camera moves and the controls say so. */
  move(pose: CameraPose): void {
    this.pose = { position: [...pose.position], target: [...pose.target] };
    this.changes += 1;
    this.listeners.forEach((l) => l());
  }
  onChange(listener: () => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }
}

const pose = (x: number, z: number, tx = 0): CameraPose => ({ position: [x, 10, z], target: [tx, 0, 0] });

describe("the comparison's one camera (T16 i, S83)", () => {
  it("one state, two views: a move in either pane is the other's", () => {
    const link = new CameraLink();
    const left = new Pane(pose(0, 20));
    const right = new Pane(pose(5, 5)); // its canvas's own first stand, before it has joined
    joinLink(link, left, true);
    joinLink(link, right, false);
    expect(right.pose).toEqual(left.pose); // the right takes the left's stand as it joins
    expect(link.current).toEqual(left.pose);

    left.move(pose(3, 12, 1)); // an orbit and a pan in the left pane
    expect(right.pose).toEqual(pose(3, 12, 1));
    right.move(pose(-4, 8, 2)); // a zoom in the right pane
    expect(left.pose).toEqual(pose(-4, 8, 2));
    expect(link.current).toEqual(pose(-4, 8, 2));
    // No echo: each move wrote the other pane once and came back to nobody.
    expect(left.changes).toBe(2);
    expect(right.changes).toBe(3);
  });

  it("the follower's own first stand never moves the leader; it waits for the leader's", () => {
    const link = new CameraLink();
    const right = new Pane(pose(5, 5));
    joinLink(link, right, false);
    right.move(pose(6, 6)); // the canvas's first update, before any shared state
    expect(link.current).toBeNull();
    const left = new Pane(pose(0, 20));
    joinLink(link, left, true);
    expect(left.pose).toEqual(pose(0, 20));
    expect(right.pose).toEqual(pose(0, 20));
    right.move(pose(1, 2)); // joined now: its moves are the shared camera
    expect(left.pose).toEqual(pose(1, 2));
  });

  it("a fresh camera is a fresh link, led from the left pane's new stand; a pane that leaves moves nothing", () => {
    const old = new CameraLink();
    const left = new Pane(pose(0, 20));
    const right = new Pane(pose(0, 20));
    const leaveLeft = joinLink(old, left, true);
    const leaveRight = joinLink(old, right, false);
    left.move(pose(9, 9));
    leaveLeft();
    leaveRight();
    left.move(pose(1, 1));
    expect(right.pose).toEqual(pose(9, 9));
    // A preset pressed: both canvases are made again at the stand; the new link starts at the left's.
    const fresh = new CameraLink();
    const left2 = new Pane(pose(0, 30));
    const right2 = new Pane(pose(0, 25)); // another galaxy's own framing would put it elsewhere
    joinLink(fresh, right2, false);
    joinLink(fresh, left2, true);
    expect(right2.pose).toEqual(pose(0, 30));
  });
});
