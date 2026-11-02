import { useThree } from "@react-three/fiber";
import { useEffect } from "react";
import type { OrbitControls as OrbitControlsImpl } from "three-stdlib";

import { type CameraLink, type LinkedView, joinLink } from "./cameraLink";

/**
 * The comparison view's shared camera (T16 i, S83), inside one pane's canvas: joins the canvas's camera and its orbit
 * controls to the link (cameraLink.ts). A move of either pane - the controls' "change", which a drag, the wheel, the
 * zoom slider and the picture test's `place` all raise - is published; the other pane's is written here, through the
 * controls' own update, so its zoom bridge reports the view as a drag's would. It draws nothing and adds no request.
 */
export function CameraLinkProbe({ link, leads }: { link: CameraLink; leads: boolean }) {
  const camera = useThree((s) => s.camera);
  const controls = useThree((s) => s.controls) as OrbitControlsImpl | null;
  useEffect(() => {
    if (!controls) return;
    const view: LinkedView = {
      read: () => ({
        position: camera.position.toArray() as [number, number, number],
        target: controls.target.toArray() as [number, number, number],
      }),
      write: (pose) => {
        controls.target.set(...pose.target);
        camera.position.set(...pose.position);
        controls.update();
      },
      onChange: (listener) => {
        controls.addEventListener("change", listener);
        return () => controls.removeEventListener("change", listener);
      },
    };
    return joinLink(link, view, leads);
  }, [link, leads, camera, controls]);
  return null;
}
