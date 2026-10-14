#!/usr/bin/env python
"""Lay the voiced lines on the timeline, set a music bed under them, and master the soundtrack.

    python mix_soundtrack.py placement.json --clips clips [--music bed.m4a] [--duck 8] [--music-lufs -26]
                             [--length 629.6 | --film film.mp4] [--out soundtrack]
                             [--mux film-narrated.mp4]

placement.json is a list of {"id": "A1", "at": 12.4}: each voiced line (clips/<id>.wav from
voice_lines.py) and the second it starts. A line that runs into the next line's start is a
defect in the cut, not something to hide in the mix, so the script refuses it.

Writes <out>/narration.wav (normalised voice), <out>/mix.wav (float pre-master),
<out>/soundtrack.wav (PCM24 stereo master) and <out>/soundtrack.m4a
(AAC 192k, 48 kHz stereo, two-pass loudnorm to -16 LUFS, -1.5 dBTP). With --mux, puts it on the
film by stream copy. Needs ffmpeg and ffprobe on PATH, plus numpy and soundfile.

The numbers (the -23 LUFS voice stem, the 8 dB dip, the 0.3 s ramps, the -16 LUFS master) and
why they are what they are: references/soundtrack.md.
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys
from audio_inputs import child, dependencies, finite, records

SR = 48000
VOICE_LUFS = -23.0      # the narration stem before the master
PAD, RAMP = 0.3, 0.3    # the dip window pads each line this much each side; the ramps are this long
FADE_OUT = 3.0          # the bed fades over the film's last seconds
MASTER = "I=-16:TP=-1.5:LRA=11"


def run(cmd):
    cmd = [cmd[0], "-nostdin", *cmd[1:]] if cmd[0] == "ffmpeg" else cmd
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise ValueError("media command failed; check that the input is a supported local media file")
    return r


def decode(path):
    """Any audio file ffmpeg reads -> mono float32 at 48 kHz."""
    import numpy as np
    path = pathlib.Path(path).resolve()
    r = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-protocol_whitelist", "file,pipe", "-i", str(path), "-ac", "1", "-ar", str(SR),
                        "-f", "f32le", "-"], capture_output=True)
    if r.returncode != 0:
        raise ValueError("ffmpeg could not decode the local audio input")
    audio = np.frombuffer(r.stdout, np.float32).copy()
    if not len(audio) or not np.isfinite(audio).all() or not np.any(audio):
        raise ValueError("audio input is empty, silent or nonfinite")
    return audio


def lufs(path):
    path = pathlib.Path(path).resolve()
    err = run(["ffmpeg", "-hide_banner", "-protocol_whitelist", "file,pipe", "-i", str(path), "-af", "ebur128", "-f", "null", "-"]).stderr
    matches = re.findall(r"I:\s+(-?[\d.]+) LUFS", err)
    if not matches:
        raise ValueError("audio has no measurable integrated loudness")
    return finite(float(matches[-1]), "loudness", minimum=-100)


def duration(path):
    path = pathlib.Path(path).resolve()
    out = run(["ffprobe", "-v", "error", "-protocol_whitelist", "file,pipe", "-select_streams", "v:0", "-show_entries",
               "stream=duration", "-of", "csv=p=0", str(path)]).stdout
    return finite(float(out.strip()), "film video duration", positive=True)


def box(x, k):
    """A k-sample moving average by running sum: np.convolve's numbers, in seconds rather than minutes."""
    import numpy as np
    if k <= 1:
        return x
    # Extend edge values: a line at time zero must start fully ducked, not at half dip.
    right = (k - 1) // 2
    padded = np.pad(x, (k - 1 - right, right), mode="edge")
    c = np.concatenate(([0.0], np.cumsum(padded, dtype=np.float64)))
    return ((c[k:] - c[:-k]) / k).astype(np.float32)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("placement", help="JSON list of {id, at}")
    ap.add_argument("--clips", default="clips")
    ap.add_argument("--music", help="the music bed (any format ffmpeg reads); looped or cut to length")
    ap.add_argument("--duck", type=float, default=8.0, help="dB the bed dips under speech (default 8)")
    ap.add_argument("--music-lufs", type=float, default=-26.0,
                    help="unducked music level before mastering (default -26 LUFS)")
    ap.add_argument("--length", type=float,
                    help="soundtrack length in seconds (default: the film's, else the last line's end + 1 s)")
    ap.add_argument("--film", help="the picture; sets --length from it, and is what --mux writes onto")
    ap.add_argument("--out", default="soundtrack")
    ap.add_argument("--mux", help="write the film with this soundtrack to this path (video stream-copied)")
    args = ap.parse_args()

    if args.mux and not args.film:
        ap.error("--mux needs --film")
    finite(args.duck, "duck", maximum=60)
    finite(args.music_lufs, "music LUFS", minimum=-60, maximum=-10)
    if args.length is not None:
        finite(args.length, "length", positive=True)
    dependencies(("numpy", "soundfile"), ("ffmpeg", "ffprobe"))
    import numpy as np
    import soundfile as sf
    # Empty placement is supported for an explicitly music-only film.
    raw = json.loads(pathlib.Path(args.placement).read_text())
    if raw == [] and args.music:
        place = []
    else:
        place = records(args.placement, ("id", "at"))
    for p in place:
        finite(p["at"], "placement time")
    place.sort(key=lambda p: p["at"])
    clips = pathlib.Path(args.clips).resolve()
    out = pathlib.Path(args.out).resolve()
    inputs = [pathlib.Path(args.placement).resolve(), *[child(clips, f"{p['id']}.wav") for p in place]]
    for source in (args.music, args.film):
        if source:
            path = pathlib.Path(source).resolve()
            if not path.is_file():
                ap.error("media input must be an existing local file")
            inputs.append(path)
    outputs = [child(out, name) for name in ("narration.wav", "mix.wav", "soundtrack.wav", "soundtrack.m4a")]
    if args.mux:
        mux = pathlib.Path(args.mux)
        if mux.is_symlink():
            ap.error("mux output cannot be a symlink")
        outputs.append(mux.resolve())
    if len(set(outputs)) != len(outputs) or set(inputs) & set(outputs):
        ap.error("output paths must be distinct and must not overwrite any input")
    if any(not source.is_file() for source in inputs):
        ap.error("an audio input is missing")
    if any(output.exists() and source.samefile(output) for source in inputs for output in outputs):
        ap.error("output cannot overwrite an input through a hard link")

    # 1. The voice stem: each line at its second. A line that runs into the next is refused.
    audio = {p["id"]: decode(clips / f"{p['id']}.wav") for p in place}
    last_end = max((p["at"] + len(audio[p["id"]]) / SR for p in place), default=0.0)
    film_length = duration(args.film) if args.film else None
    length = args.length if args.length is not None else (film_length if film_length else last_end + 1.0)
    if args.mux and abs(length - film_length) > 0.05:
        ap.error("mux soundtrack length must match the entire film")
    n = int(round(length * SR))
    voice = np.zeros(n, np.float32)
    mask = np.zeros(n, np.float32)
    for i, p in enumerate(place):
        a = audio[p["id"]]
        at = int(p["at"] * SR)
        end = at + len(a)
        if i + 1 < len(place) and end / SR > place[i + 1]["at"]:
            sys.exit(f"{p['id']} runs {end / SR - place[i + 1]['at']:.2f}s into {place[i + 1]['id']}: "
                     "fix the cut, not the mix")
        if end > n:
            sys.exit(f"{p['id']} ends at {end / SR:.1f}s, past the {length:.1f}s soundtrack")
        voice[at:end] += a
        mask[max(0, at - int(PAD * SR)):min(n, end + int(PAD * SR))] = 1
    music = decode(args.music) if args.music else None
    music_gain = 10 ** ((args.music_lufs - lufs(args.music)) / 20) if args.music else None
    out.mkdir(parents=True, exist_ok=True)
    sf.write(out / "narration.wav", voice, SR, subtype="FLOAT")
    gain = 10 ** ((VOICE_LUFS - lufs(out / "narration.wav")) / 20) if place else 1.0
    voice *= gain
    sf.write(out / "narration.wav", voice, SR, subtype="FLOAT")
    print(f"{len(place)} lines, last ends {last_end:.1f}s, soundtrack {length:.1f}s, "
          f"voice gain {20 * np.log10(gain):+.1f} dB")

    # 2. The bed: the music at its own level where nobody speaks, dipped under the lines.
    mix = voice.copy()
    if args.music:
        music *= music_gain
        if len(music) < n:
            reps = int(np.ceil(n / len(music)))
            print(f"music is {len(music) / SR:.0f}s, film {length:.0f}s: looping it {reps}x "
                  "(choose a longer track if the join is audible)")
            music = np.tile(music, reps)
        music = music[:n].copy()
        fade = min(n, int(FADE_OUT * SR))
        music[n - fade:] *= np.linspace(1.0, 0.0, fade, dtype=np.float32)
        duck = box(mask, int(RAMP * SR)).clip(0, 1)
        bed = music * (1 - duck * (1 - 10 ** (-args.duck / 20)))
        mix = mix + bed
        print(f"bed dips {args.duck:g} dB under speech; speech covers {100 * mask.mean():.0f}% of the film")
    sf.write(out / "mix.wav", mix, SR, subtype="FLOAT")

    # 3. Master: measure, then apply the measured values (two-pass loudnorm). Stereo first, so the
    #    measurement is of what ships: a mono measure followed by an upmix lands about 3 dB hot.
    probe = run(["ffmpeg", "-hide_banner", "-i", str(out / "mix.wav"), "-af",
                 f"aformat=channel_layouts=stereo,loudnorm={MASTER}:print_format=json", "-f", "null", "-"]).stderr
    st = json.loads(probe[probe.rindex("{"):probe.rindex("}") + 1])
    for key in ("input_i", "input_tp", "input_lra", "input_thresh", "target_offset"):
        finite(float(st[key]), "master measurement", minimum=-100)
    second = (f"aformat=channel_layouts=stereo,loudnorm={MASTER}:measured_I={st['input_i']}:"
              f"measured_TP={st['input_tp']}:measured_LRA={st['input_lra']}:"
              f"measured_thresh={st['input_thresh']}:offset={st['target_offset']}:linear=true")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(out / "mix.wav"), "-af", second,
         "-c:a", "pcm_s24le", "-ar", str(SR), "-ac", "2", str(out / "soundtrack.wav")])
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(out / "soundtrack.wav"),
         "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-ac", "2", str(out / "soundtrack.m4a")])
    mastered = lufs(out / "soundtrack.m4a")
    if abs(mastered + 16) > 1:
        raise ValueError("encoded master missed -16 LUFS by more than 1 dB; inspect the mix")
    print(f"master: {float(st['input_i']):.1f} LUFS -> {mastered:.1f} LUFS, "
          f"{out / 'soundtrack.m4a'}")

    # 4. Put it on the picture.
    if args.mux:
        run(["ffmpeg", "-y", "-loglevel", "error", "-protocol_whitelist", "file,pipe", "-i", str(pathlib.Path(args.film).resolve()),
             "-protocol_whitelist", "file,pipe", "-i", str(out / "soundtrack.m4a"),
             "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "copy",
             "-movflags", "+faststart", str(pathlib.Path(args.mux).resolve())])
        print(f"muxed: {args.mux}")


if __name__ == "__main__":
    try:
        main()
    except ValueError as exc:
        sys.exit(str(exc))
    except (OSError, KeyError, TypeError, ImportError):
        sys.exit("Audio mix failed: invalid input or unavailable dependency.")
