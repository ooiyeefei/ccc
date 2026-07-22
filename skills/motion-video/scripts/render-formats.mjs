/**
 * Render every platform format from ONE Remotion project.
 *
 * Assumes Root.tsx registers a composition per ratio named `Film-<id>` (see
 * references/platform-formats.md). Renders only the ids you pass, so you never
 * produce a format no target platform uses.
 *
 *   node scripts/render-formats.mjs                         # all four defaults
 *   node scripts/render-formats.mjs reel-9x16 feed-4x5      # just these
 *   REMOTION_ENTRY=src/index.ts node scripts/render-formats.mjs
 *
 * Output: out/<id>.mp4  (H.264 / AAC MP4 - the one container every platform
 * accepts; LinkedIn rejects MOV, so never emit .mov here).
 */
import { execFileSync } from 'node:child_process';
import { mkdirSync } from 'node:fs';

const ENTRY = process.env.REMOTION_ENTRY || 'src/index.ts';
const OUTDIR = process.env.REMOTION_OUTDIR || 'out';
const DEFAULT_IDS = ['yt-16x9', 'reel-9x16', 'feed-4x5', 'sq-1x1'];
const ids = process.argv.slice(2).length ? process.argv.slice(2) : DEFAULT_IDS;

mkdirSync(OUTDIR, { recursive: true });

for (const id of ids) {
  const out = `${OUTDIR}/${id}.mp4`;
  console.log(`\n=== rendering Film-${id} -> ${out} ===`);
  execFileSync(
    'npx',
    ['remotion', 'render', ENTRY, `Film-${id}`, out, '--codec', 'h264'],
    { stdio: 'inherit' },
  );
}

console.log(`\nDone. ${ids.length} format(s) in ${OUTDIR}/. Watch each at its true ratio before shipping.`);
