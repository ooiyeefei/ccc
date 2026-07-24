// ABSORBED from video-shotcraft (Apache-2.0): assets/lib/FlashCut.tsx
// Upstream: https://github.com/Vincentwei1021/video-shotcraft
//
// CHANGES vs upstream (rule 3 "brand-match verbatim"):
//   - The bloom colour was hardcoded to the Ink Press warm white. It is now a
//     prop, so a cool/blue-grounded brand can flash in its own light. The
//     default keeps upstream's warm white, which is the flattering choice for
//     most product UI.
// Timing curve is upstream's and is untouched.
import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';

/**
 * Bright-field cut: a bloom that flashes over a hard cut, hiding the seam and
 * giving the change impact. Use on a HARD tonal break — the enemy scene giving
 * way to the product, a reveal landing — where a crossfade would read as soft
 * and apologetic. Do not use it between two calm beats; it will feel like a
 * camera fault.
 *
 * Mount it as the LAST child of the incoming scene, at the scene's frame 0, so
 * its own useCurrentFrame starts at the cut.
 */
export const FlashCut: React.FC<{
  duration?: number;
  /** Peak opacity of the bloom (upstream: 0.85). Lower it for a subtler blink. */
  peak?: number;
  /** Bloom colours: the hot centre and the falloff. */
  centre?: string;
  falloff?: string;
}> = ({
  duration = 10,
  peak = 0.85,
  centre = 'rgba(255,248,235,0.98)',
  falloff = 'rgba(255,244,224,0.55)',
}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [0, duration * 0.4, duration], [0, peak, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return (
    <AbsoluteFill
      style={{
        pointerEvents: 'none',
        opacity: o,
        background: `radial-gradient(ellipse at 50% 45%, ${centre}, ${falloff} 55%, transparent 80%)`,
      }}
    />
  );
};
