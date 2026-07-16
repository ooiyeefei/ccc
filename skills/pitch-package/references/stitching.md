# Stitching - assembly variants and fallbacks

## The three variants

**A. Fully recorded submission film** (for portals and async judging):
`deck Part A + demo film + deck Part B`, one voiceover recorded over the stitched cut following the combined script's timestamps. Production steps live in pitch-deck's `deck-recording.md`; narration re-sync rules in pitch-craft's `timing.md`.

**B. Live speech with recorded demo** (the default for stage slots):
Speak the deck live; at the demo-slot slide, play the film and go quiet; resume at the next slide. The live script must carry the demo-break marker stating exactly what the video covers ("this covers slides 8, 9, 10") so the speaker and any co-presenter never read the slide-number jump as a gap. Optional: keep the demo's voiceover script one tap away (collapsible section on the teleprompter) in case the venue audio fails and you must narrate the film live.

**C. Fully live** (product driven by hand on stage):
Highest wow, highest variance. Only with: a rehearsed driver, a deterministic staging environment, and variant B's film on local disk as the instant fallback. Decide the switch trigger in advance ("if login takes more than 15 seconds, roll the film") - deciding mid-failure always costs more time.

## Stitch recipe

Normalize parts first if they differ (resolution, fps), then concat:

```bash
# uniform sources - lossless
printf "file 'a.mp4'\nfile 'demo.mp4'\nfile 'b.mp4'\n" > list.txt
ffmpeg -f concat -safe 0 -i list.txt -c copy stitched.mp4

# mixed sources - re-encode
ffmpeg -f concat -safe 0 -i list.txt -c:v libx264 -crf 18 -preset slow \
  -pix_fmt yuv420p -movflags +faststart stitched.mp4
```

Voice is recorded separately over the stitched cut. The per-part milestone JSON sidecars carry exact slide times for re-alignment if any segment drifts.

## The fallback ladder

Write it down before the day; each rung is rehearsed once:

1. Embedded video won't load -> play the LOCAL mp4 (always on the presenting machine).
2. Live product misbehaves -> switch to the recorded demo (variant B), narrating from the demo script.
3. Machine or projector dies -> present from the phone teleprompter and tell the story over the gallery stills.
4. Everything dies -> the throughline, the three numbers, and the close, from memory. If the speaker can't do rung 4, the pitch isn't rehearsed yet.

## Phone teleprompter

The speaker holds the script on a phone. Requirements that matter in the hand:

- One page, native vertical scroll (no inner scroll boxes - they jank on mobile), dark background, ~22px text, thumb-reachable.
- Each beat: slide number + name + target seconds + the words. Numbers and emphasis words color-coded.
- The demo break as a visually loud band ("PLAY THE DEMO VIDEO - ~2:36 - you stay quiet"), with the demo voiceover in a collapsible section beneath it for the narrate-it-live contingency.
- Delivery cues inline in a muted style: read at a glance, skipped at speed.
- Test it ON the phone before the day: safe-area insets, font size at arm's length, screen-lock timeout off.
