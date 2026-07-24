// ABSORBED from video-shotcraft (Apache-2.0): assets/lib/Caption.tsx
// Upstream: https://github.com/Vincentwei1021/video-shotcraft
//
// CHANGES vs upstream (rule 3 "brand-match verbatim", rule 1.5 "safe zones"):
//   - Upstream hardcodes the Ink Press amber marker, warm-grey text, and a
//     generic mono stack. All three are props now, so the strip carries the
//     product's real mono face and accent.
//   - `bottom` still defaults to 72, but in a VERTICAL cut that sits inside the
//     platform caption bar. Pass the safe-zone offset from `safeBand` when
//     rendering 9:16 or 4:5 (see references/platform-formats.md).
// Timing is upstream's and is untouched.
import React from 'react';
import { interpolate, useCurrentFrame } from 'remotion';

/**
 * Screen-space narration caption: a mono info-strip led by a small accent
 * square. This is the film TALKING to the viewer, distinct from a lower-third
 * (which names what is on screen). Keep it to a short uppercase phrase; it is
 * a rhythm device, not a paragraph.
 */
export const Caption: React.FC<{
  text: string;
  duration: number;
  bottom?: number;
  color?: string;
  accent?: string;
  fontFamily?: string;
  fontSize?: number;
}> = ({
  text,
  duration,
  bottom = 72,
  color = 'currentColor',
  accent = 'currentColor',
  fontFamily = 'ui-monospace, SFMono-Regular, Menlo, monospace',
  fontSize = 22,
}) => {
  const frame = useCurrentFrame();
  const inT = interpolate(frame, [0, 8], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const outT = interpolate(frame, [duration - 8, duration], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        position: 'absolute',
        left: 0,
        right: 0,
        bottom,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'baseline',
        gap: 14,
        fontFamily,
        fontSize,
        letterSpacing: '0.14em',
        textTransform: 'uppercase',
        color,
        opacity: inT * outT,
        transform: `translateY(${(1 - inT) * 8}px)`,
        pointerEvents: 'none',
      }}
    >
      <span style={{ width: 6, height: 6, background: accent, display: 'inline-block' }} />
      <span>{text}</span>
    </div>
  );
};
