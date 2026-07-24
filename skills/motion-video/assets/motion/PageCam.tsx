// ABSORBED from video-shotcraft (Apache-2.0): assets/lib/PageCam.tsx
// Upstream: https://github.com/Vincentwei1021/video-shotcraft
//
// CHANGES vs upstream (both required by this skill's own rules — do not revert):
//   1. FORMAT-AWARE. Upstream hardcodes a 1920x1080 viewport (960/540 centres,
//      1920 page width). It therefore only renders correctly in 16:9, which
//      breaks rule 1.5 "reframe, never crop". Here the viewport centre comes
//      from useVideoConfig(), and page width is a prop, so ONE component set
//      renders at 16:9 / 9:16 / 4:5 / 1:1.
//   2. BRAND-NEUTRAL. Upstream paints the Ink Press cream (#faf7f2) behind the
//      page. Hardcoding a template's colour breaks rule 3 "brand-match
//      verbatim". Background is now a prop defaulting to transparent.
// Everything else (the key interpolation, the 3D pivot math, the layout-scale
// `zoom` sharpness trick, DOF) is upstream's and is deliberately untouched.
import React from 'react';
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig, Easing } from 'remotion';

export type CamKey = {
  frame: number;
  cx: number;
  cy: number;
  zoom: number;
  rotX?: number; // deg, tilt about the horizontal axis (positive = top leans away, like looking at a table)
  rotY?: number; // deg, tilt about the vertical axis (positive = right edge recedes, i.e. seen from the LEFT)
  rotZ?: number; // deg, in-plane roll
  persp?: number; // px, perspective strength (default 1400; smaller = stronger)
};

const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

/**
 * Zoom that makes a page of `pageW` exactly span the viewport width. Use as
 * `zoomScale` when reframing a landscape page into a vertical cut: the page
 * becomes a band across the middle and the freed space above/below carries the
 * title and CTA. That is re-authoring for the ratio, not cropping it.
 */
export const fitWidthZoom = (viewportW: number, pageW = 1920) => viewportW / pageW;

/**
 * 2.5D camera over a full-page screenshot. (cx, cy) is the page-space CSS point
 * held at the viewport centre; zoom is scale (1 = 1 CSS px -> 1 output px).
 * Page textures should be 2x and are rendered at CSS size via width.
 *
 * Optional 3D: keys may carry rotX/rotY/rotZ/persp to tilt the page like a
 * plane seen from an oblique camera. When NO key declares any 3D field, the
 * markup degrades to a flat pan/zoom.
 *
 * Optional DOF: a screen-space gradient-blur band approximating a focal plane
 * near `focusY` (blurring the far/top part of a tilted page).
 */
export const PageCam: React.FC<{
  src: string; // staticFile path, e.g. textures/live/dashboard.png
  pageH: number; // CSS page height
  keys: CamKey[];
  pageW?: number; // CSS page width (default 1920)
  zoomScale?: number; // multiplier applied to every key's zoom — reframes a whole scene for another ratio
  bg?: string; // backdrop behind the page; default transparent so the scene's own brand surface shows
  children?: React.ReactNode; // page-space overlays (positioned in CSS px, they track the camera)
  blur?: number;
  saturate?: number;
  ease?: (t: number) => number;
  dof?: { focusY: number; strength: number };
  // Optional absolute-frame override: when PageCam is rendered inside a
  // <Sequence> (which rebases useCurrentFrame), the parent can pass the
  // restored absolute comp frame so the keys keep their absolute frame refs.
  frame?: number;
}> = ({
  src,
  pageH,
  keys,
  pageW = 1920,
  zoomScale = 1,
  bg = 'transparent',
  children,
  blur = 0,
  saturate = 1,
  ease = Easing.bezier(0.33, 0, 0.15, 1),
  dof,
  frame: frameProp,
}) => {
  const ownFrame = useCurrentFrame();
  const frame = frameProp ?? ownFrame;
  const { width: vpW, height: vpH } = useVideoConfig();
  // The viewport point the focal page-point is pinned to. Upstream hardcoded
  // (960, 540); deriving it is what makes every other ratio work.
  const midX = vpW / 2;
  const midY = vpH / 2;

  // find segment
  let a = keys[0], b = keys[keys.length - 1];
  for (let i = 0; i < keys.length - 1; i++) {
    if (frame >= keys[i].frame && frame <= keys[i + 1].frame) { a = keys[i]; b = keys[i + 1]; break; }
  }
  const t = a.frame === b.frame ? 1 : interpolate(frame, [a.frame, b.frame], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease,
  });
  const cx = lerp(a.cx, b.cx, t);
  const cy = lerp(a.cy, b.cy, t);
  const zoom = lerp(a.zoom, b.zoom, t) * zoomScale;

  const filters: string[] = [];
  if (blur > 0) filters.push(`blur(${blur}px)`);
  if (saturate !== 1) filters.push(`saturate(${saturate})`);

  // Does any key request 3D? If not, keep the flat markup.
  const has3D = keys.some((k) => k.rotX !== undefined || k.rotY !== undefined || k.rotZ !== undefined || k.persp !== undefined);

  if (!has3D) {
    return (
      <AbsoluteFill style={{ overflow: 'hidden', backgroundColor: bg }}>
        <div
          style={{
            position: 'absolute', width: pageW, height: pageH,
            transform: `translate(${midX - cx * zoom}px, ${midY - cy * zoom}px) scale(${zoom})`,
            transformOrigin: '0 0',
            filter: filters.length ? filters.join(' ') : undefined,
          }}
        >
          <Img src={staticFile(src)} style={{ position: 'absolute', width: pageW, height: pageH }} />
          {children}
        </div>
      </AbsoluteFill>
    );
  }

  // 3D mode: pivot rotation/scale about the focal page-point (cx, cy) so it
  // stays centred in the viewport. With rot=0 this reduces to the flat
  // transform: (midX, midY) + zoom*(p - (cx, cy)).
  const rotX = lerp(a.rotX ?? 0, b.rotX ?? 0, t);
  const rotY = lerp(a.rotY ?? 0, b.rotY ?? 0, t);
  const rotZ = lerp(a.rotZ ?? 0, b.rotZ ?? 0, t);
  const persp = lerp(a.persp ?? 1400, b.persp ?? 1400, t);

  return (
    <AbsoluteFill style={{ overflow: 'hidden', backgroundColor: bg }}>
      <div
        style={{
          position: 'absolute', inset: 0,
          perspective: `${persp * zoom}px`,
          perspectiveOrigin: `${midX}px ${midY}px`,
        }}
      >
        {/* LAYOUT-SCALE zoom (upstream's trick, kept verbatim): instead of
            scale(zoom) in the transform chain — which makes Chromium rasterize
            the 3D-composited layer at layout size then GPU-upscale, softening
            every glyph — the magnification is applied as the CSS `zoom`
            property. `zoom` enlarges the layout box itself, so the page and any
            overlay cards rasterize at the ENLARGED device size and sample down
            from their hi-res sources, giving sharp edges under perspective.

            Coordinate math: `zoom` scales this element's local coordinate space,
            so a page point (cx,cy) renders at (cx*zoom, cy*zoom) device px from
            the box origin, and translate(Tx px) renders as Tx*zoom device px.
            To land the focal point at the viewport centre (midX, midY):
              cx*zoom + Tx*zoom = midX  =>  Tx = midX/zoom - cx  (likewise Ty).
            Rotations pivot about transform-origin (cx,cy) = the focal point, so
            they leave its screen position unchanged. */}
        <div
          style={{
            position: 'absolute', width: pageW, height: pageH,
            zoom,
            transform: `translate(${midX / zoom - cx}px, ${midY / zoom - cy}px) rotateY(${rotY}deg) rotateX(${rotX}deg) rotateZ(${rotZ}deg)`,
            transformOrigin: `${cx}px ${cy}px`,
            transformStyle: 'preserve-3d',
            filter: filters.length ? filters.join(' ') : undefined,
          }}
        >
          <Img src={staticFile(src)} style={{ position: 'absolute', width: pageW, height: pageH }} />
          {children}
        </div>
      </div>

      {/* Depth-of-field approximation: a top-band gradient blur (the far part of
          a tilted page reads soft). Screen-space, over the page. */}
      {dof ? (
        <div
          style={{
            position: 'absolute',
            left: 0,
            right: 0,
            top: 0,
            height: Math.max(0, dof.focusY),
            backdropFilter: `blur(${dof.strength}px)`,
            WebkitBackdropFilter: `blur(${dof.strength}px)`,
            maskImage: 'linear-gradient(to bottom, rgba(0,0,0,1) 0%, rgba(0,0,0,1) 45%, rgba(0,0,0,0) 100%)',
            WebkitMaskImage: 'linear-gradient(to bottom, rgba(0,0,0,1) 0%, rgba(0,0,0,1) 45%, rgba(0,0,0,0) 100%)',
            pointerEvents: 'none',
          }}
        />
      ) : null}
    </AbsoluteFill>
  );
};
