"""Threshold resolution shared by transcribe.py and audit.py.

`exp(avg_logprob)` is monotonic but not calibrated, and its scale shifts with
recording conditions -- one 18-minute call clustered at a median of 0.51 while a
cleaner one sat at 0.62. A fixed absolute cutoff therefore flags the middle of
one distribution and the tail of another, which is why the default here is a
percentile of the recording's own scores.
"""

DEFAULT_THRESHOLD = "p20"


def resolve_threshold(spec, confidences):
    """Turn a threshold spec into an absolute value for this recording.

    spec: "p20" (bottom 20% of these scores) or "0.6" (absolute).
    Returns (value, description) -- description names what was applied, so
    callers can print it rather than implying a universal bar.
    """
    scored = sorted(c for c in confidences if c is not None)
    if isinstance(spec, str) and spec.startswith("p"):
        pct = float(spec[1:])
        if not scored:
            return 0.0, f"{spec} (no scores available)"
        idx = min(len(scored) - 1, int(len(scored) * pct / 100.0))
        return scored[idx], f"{spec} of this recording = {scored[idx]:.3f}"
    value = float(spec)
    return value, f"absolute {value:.2f}"


def describe(confidences):
    """One-line distribution summary, so a threshold can be judged in context."""
    scored = sorted(c for c in confidences if c is not None)
    if not scored:
        return "no confidence scores"
    n = len(scored)
    q = lambda p: scored[min(n - 1, int(n * p))]
    return (f"n={n} median={q(0.5):.3f} p10={q(0.10):.3f} "
            f"p25={q(0.25):.3f} p75={q(0.75):.3f}")
