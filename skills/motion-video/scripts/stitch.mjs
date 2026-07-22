/**
 * Stitch rendered Remotion scenes and the one real capture into the final film,
 * with crossfades. Edit CLIPS (in play order) and CROSS; run `node stitch.mjs`.
 *
 * Why a script and not an NLE: the clip list is the edit, in version control, so
 * a re-render of one scene is a one-line change and a re-run, not a manual
 * re-cut. Timings for any narration come from the DELIVERED mp4 this produces,
 * never from the planned scene lengths (the demo-video Gate-3 rule).
 *
 * Requires ffmpeg. All clips must already be the same resolution/fps (render the
 * Remotion scenes and the capture at the same size, e.g. 1920x1080 @ 30).
 */
import { execFileSync } from 'node:child_process';

const CROSS = 0.5;                 // crossfade seconds between scenes
const OUT = 'out/film.mp4';

// [path, label] in play order. Mix rendered scenes and the real capture freely.
const CLIPS = [
  ['out/cold-open.mp4', 'cold open'],
  ['out/problem.mp4', 'the problem'],
  ['out/product-real.mp4', 'real capture (proof)'],
  ['out/payoff.mp4', 'payoff'],
  ['out/close.mp4', 'close'],
];

const dur = (f) => Number(execFileSync('ffprobe',
  ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], { encoding: 'utf8' }).trim());

const durations = CLIPS.map(([f]) => dur(f));
const total = durations.reduce((a, d) => a + d, 0) - CROSS * (CLIPS.length - 1);

// Build the xfade chain. Each clip is normalised (fps/format/pts) then dissolved
// into the previous at a running offset = sum(prev durations) - one CROSS each.
const inputs = CLIPS.flatMap(([f]) => ['-i', f]);
const norm = CLIPS.map((_, i) =>
  `[${i}:v]settb=AVTB,fps=30,format=yuv420p,setpts=PTS-STARTPTS[v${i}]`).join(';');

let chain = '', prev = 'v0', offset = 0;
for (let i = 1; i < CLIPS.length; i++) {
  offset += durations[i - 1] - CROSS;
  const out = i === CLIPS.length - 1 ? 'vout' : `x${i}`;
  chain += `;[${prev}][v${i}]xfade=transition=fade:duration=${CROSS}:offset=${offset.toFixed(3)}[${out}]`;
  prev = out;
}

CLIPS.forEach(([, label], i) => console.log(`  ${i + 1}. ${label.padEnd(24)} ${durations[i].toFixed(1)}s`));
console.log(`  total (with ${CROSS}s crossfades): ${total.toFixed(1)}s\n`);

execFileSync('ffmpeg', [
  '-y', ...inputs,
  '-filter_complex', norm + chain, '-map', '[vout]',
  '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p',
  '-movflags', '+faststart', OUT,
], { stdio: 'inherit' });

console.log(`\n  ${OUT}  ${dur(OUT).toFixed(2)}s`);
