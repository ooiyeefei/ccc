// ABSORBED from video-shotcraft (Apache-2.0): assets/lib/DigitRoll.tsx
// Upstream: https://github.com/Vincentwei1021/video-shotcraft
//
// CHANGES vs upstream (required by rule 3 "brand-match verbatim" — do not revert):
//   - Upstream hardcodes the Ink Press amber `oklch(52% 0.115 65)` as the digit
//     colour. Shipping that in another product's film paints a foreign brand
//     into the money shot. Colour now defaults to `currentColor`, and font
//     family/weight are props, so the roll inherits the product's real type.
// The roll timing and offset math are upstream's and are untouched.
import React from 'react';
import { interpolate, useCurrentFrame, Easing } from 'remotion';

const DIGITS = '0123456789';

/**
 * Odometer-style digit roll. Use it the moment a NUMBER is the point of the
 * shot — a total, a count, an outstanding balance, a percentage. A figure that
 * rolls into place reads as "the system computed this"; the same figure fading
 * in reads as a caption. Non-digit characters (currency marks, separators,
 * decimal points) are rendered static so "RM6,821.00" rolls only its numerals.
 *
 * Feed it a pre-formatted string, not a number, so the film's money formatting
 * stays the product's own.
 */
export const DigitRoll: React.FC<{
  value: string;
  delay?: number;
  fontSize?: number;
  color?: string;
  fontFamily?: string;
  fontWeight?: number | string;
  /** Frames between adjacent digits starting their roll (upstream: 4). */
  stagger?: number;
}> = ({
  value,
  delay = 0,
  fontSize = 30,
  color = 'currentColor',
  fontFamily,
  fontWeight,
  stagger = 4,
}) => {
  const frame = useCurrentFrame();
  const lineH = fontSize * 1.15;
  return (
    <span style={{ display: 'inline-flex', overflow: 'hidden', height: lineH, verticalAlign: 'bottom', fontFamily, fontWeight }}>
      {value.split('').map((ch, i) => {
        const target = DIGITS.indexOf(ch);
        if (target < 0) {
          return (
            <span key={i} style={{ fontSize, lineHeight: `${lineH}px`, color }}>{ch}</span>
          );
        }
        const t = interpolate(frame, [delay + i * stagger, delay + i * stagger + 22], [0, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
          easing: Easing.bezier(0.25, 0.8, 0.25, 1),
        });
        // roll through one full strip then land on the target digit
        const offset = (10 + target) * t * lineH;
        return (
          <span key={i} style={{ display: 'inline-block', height: lineH }}>
            <span style={{ display: 'block', transform: `translateY(${-offset}px)` }}>
              {(DIGITS + DIGITS).split('').map((d, j) => (
                <span key={j} style={{ display: 'block', fontSize, lineHeight: `${lineH}px`, color, fontVariantNumeric: 'tabular-nums' }}>
                  {d}
                </span>
              ))}
            </span>
          </span>
        );
      })}
    </span>
  );
};
