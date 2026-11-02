// The comparison view's one camera (T16 i, S83): two panes, each its own canvas and its own orbit controls, driven by
// one camera state. Whatever moves either pane's camera - an orbit, a pan, a zoom by the wheel or the slider - is
// published here and written to the other's, so the two panes look at the same place from the same eye through the
// same lens at every frame. Pure and out of React, so it is tested as it is (cameraLink.test.ts); CameraLinkProbe.tsx
// joins a canvas's camera and controls to it.
//
// The left pane leads: it publishes its pose as it joins, so a fresh camera (a landing, a preset, the comparison
// switched on over an orbited view) starts both panes from the left pane's stand. The right pane follows: it takes the
// link's pose as it joins - or the leader's first one - and publishes its own moves only once it has taken one, so its
// canvas's own first stand (its first frame's update) never moves the left pane.

/** Where a camera stands and what it looks at, scene kpc. The lens and the up direction are the panes' shared props. */
export interface CameraPose {
  position: [number, number, number];
  target: [number, number, number];
}

/** A pane's camera as the link sees it: read its pose, write one, and hear of every change (the controls' "change"). */
export interface LinkedView {
  read(): CameraPose;
  write(pose: CameraPose): void;
  onChange(listener: () => void): () => void;
}

type Listener = (pose: CameraPose, from: object) => void;

const copy = (pose: CameraPose): CameraPose => ({ position: [...pose.position], target: [...pose.target] });

/** One camera state for two views: the last pose published and who published it. */
export class CameraLink {
  private pose: CameraPose | null = null;
  private readonly listeners = new Set<Listener>();

  /** The camera state both views stand at; null until the leading view has joined. */
  get current(): CameraPose | null {
    return this.pose ? copy(this.pose) : null;
  }

  /** A view moved: the state is its pose, and every other view is told. */
  publish(from: object, pose: CameraPose): void {
    this.pose = copy(pose);
    this.listeners.forEach((listener) => listener(copy(pose), from));
  }

  subscribe(listener: Listener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }
}

/**
 * Join a view to the link: its moves are published, the others' written to it. A pose written here moves the view's
 * camera, which tells its listeners as a drag would; that change is the link's, and is not published back. Returns the
 * way to leave.
 */
export function joinLink(link: CameraLink, view: LinkedView, leads: boolean): () => void {
  const me = {};
  let writing = false;
  // A follower publishes nothing until it stands where the link says: its own first stand is not the shared camera.
  let joined = leads;
  const take = (pose: CameraPose) => {
    writing = true;
    try {
      view.write(pose);
    } finally {
      writing = false;
    }
    joined = true;
  };
  const off = link.subscribe((pose, from) => {
    if (from !== me) take(pose);
  });
  const stop = view.onChange(() => {
    if (writing || !joined) return;
    link.publish(me, view.read());
  });
  if (leads) link.publish(me, view.read());
  else if (link.current) take(link.current);
  return () => {
    off();
    stop();
  };
}
