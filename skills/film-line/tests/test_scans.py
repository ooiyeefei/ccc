"""narration_scan and frame_scan: pure-function checks, plus one real OCR run when ffmpeg, tesseract
and a font are installed. Run: python -m unittest skills/film-line/tests/test_scans.py"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
ROOT = next(p for p in Path(__file__).resolve().parents if (p / ".git").exists())
sys.path.insert(0, str(SCRIPTS))
import frame_scan as fs  # noqa: E402
import narration_scan as ns  # noqa: E402

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def line(i, text, window=None, **kw):
    d = {"id": i, "text": text}
    if window:
        d["window"] = window
    d.update(kw)
    return d


class NarrationScan(unittest.TestCase):
    def kinds(self, res, key="style"):
        return {k for r in res["lines"] for k, _ in r[key]}

    def test_clean_line_in_band_has_no_findings(self):
        text = "Open the claim and the receipt sits beside the fields. The shop, date and amount are read from it."
        res = ns.scan([line("a", text, window=7.5)])
        self.assertEqual(res["hard_findings"], 0)
        self.assertEqual(self.kinds(res), set())

    def test_contrast_denial_colon_and_filler_are_flagged(self):
        bad = "It is not just a form, it is a teammate. No setup, no config. Here is everything: simply post it."
        res = ns.scan([line("b", bad)])
        self.assertTrue({"contrast", "denial_stack", "colon", "filler", "signpost"} <= self.kinds(res))

    def test_digits_dashes_exclamations_are_hard(self):
        res = ns.scan([line("c", "Post 3 bills - then check the total!")])
        self.assertEqual({"digit", "dash", "exclamation"}, self.kinds(res, "hard"))
        self.assertEqual(ns.main([str(self.write([line("c", "Post 3 bills")]))]), 1)

    def test_a_window_can_come_from_start_and_end_and_a_missing_one_is_reported(self):
        words = "word " * 30
        res = ns.scan([line("a", words, start=0, end=12), line("b", words), line("c", words, start=0, end=6)])
        self.assertEqual([r["wps"] for r in res["lines"]], [2.5, None, 5.0])
        self.assertEqual(res["pace_unchecked"], 1)
        self.assertEqual(res["hard_findings"], 1)
        self.assertIn("pace unchecked on 1 of 3 lines", ns.report(res))

    def test_pace_band_is_enforced_per_window(self):
        words = "word " * 30
        res = ns.scan([line("slow", words, window=30), line("fast", words, window=6)])
        pace = {r["id"]: [k for k, _ in r["hard"]] for r in res["lines"]}
        self.assertEqual(pace["slow"], ["pace"])
        self.assertEqual(pace["fast"], ["pace"])
        ok = ns.scan([line("fit", words, window=12)])
        self.assertEqual(ok["hard_findings"], 0)

    def test_allowed_exception_is_recorded_not_flagged(self):
        res = ns.scan([line("d", "Groot records the payment, not the transfer.", allow=["contrast"])])
        self.assertEqual(self.kinds(res), set())
        self.assertEqual({k for k, _ in res["lines"][0]["allowed"]}, {"contrast"})

    def test_avoid_list_flags_jargon_whole_words_only(self):
        res = ns.scan([line("g", "Every accrual is posted to the ledger. Ledgers tie out.")], avoid=["accrual", "ledger"])
        found = [c for r in res["lines"] for k, c in r["style"] if k == "jargon"]
        self.assertEqual(len(found), 2)
        self.assertEqual(ns.scan([line("h", "Receipts fill their own forms.")], avoid=["ledger"])["lines"][0]["style"], [])

    def test_a_hard_finding_can_be_an_approved_exception(self):
        res = ns.scan([line("f", "The voucher is PV2610012.", allow=["digit"])])
        self.assertEqual(res["hard_findings"], 0)
        self.assertEqual({k for k, _ in res["lines"][0]["allowed"]}, {"digit"})

    def test_repeated_openers_inside_a_line_and_across_the_film(self):
        res = ns.scan([line("e", "The bill arrives. The bill is read.")])
        self.assertIn("repeated_opener", self.kinds(res))
        film = [line(str(i), "The farm buys feed.") for i in range(6)]
        self.assertEqual(ns.scan(film)["openers_6_plus"], [("the", 6)])

    def write(self, lines):
        d = tempfile.TemporaryDirectory(dir=(ROOT / ".scratch") if (ROOT / ".scratch").exists() else None)
        self.addCleanup(d.cleanup)
        p = Path(d.name) / "lines.json"
        p.write_text(json.dumps(lines))
        return p


class FrameScanText(unittest.TestCase):
    ban = fs.ban_regex(fs.DEFAULT_BAN.split(","))

    def test_banned_words_match_whole_words_only(self):
        self.assertIn("banned_word", fs.scan_text("Demo workspace", self.ban))
        self.assertIn("banned_word", fs.scan_text("UAT run", self.ban))
        self.assertNotIn("banned_word", fs.scan_text("Contestant and attested", self.ban))

    def test_email_domains_are_checked_against_the_allowlist(self):
        ok = fs.scan_text("accounts@film.example.com", self.ban, ["film.example.com"])
        self.assertNotIn("email", ok)
        sub = fs.scan_text("ops@mail.film.example.com", self.ban, ["film.example.com"])
        self.assertNotIn("email", sub)
        bad = fs.scan_text("someone@gmail.com", self.ban, ["film.example.com"])
        self.assertEqual(bad["email"], ["someone@gmail.com"])

    def test_stale_figures_match_whole_numbers_with_or_without_commas(self):
        figs = fs.figure_regex(["21,456", "1234.50"])
        for text in ("Net profit 21,456.56", "profit 21456", "RM1,234.50", "due 1234.50"):
            self.assertIn("stale_figure", fs.scan_text(text, self.ban, [], None, figs), text)
        for text in ("121,456", "21,4567", "RM11,234.50", "1234.505"):
            self.assertNotIn("stale_figure", fs.scan_text(text, self.ban, [], None, figs), text)

    def test_a_pipe_or_space_separated_ban_list_is_read_as_words_and_an_empty_one_is_refused(self):
        for spec in ("demo|test", "demo test", "demo,test"):
            rx = fs.ban_regex(spec)
            self.assertIn("banned_word", fs.scan_text("a demo", rx), spec)
            self.assertIn("banned_word", fs.scan_text("a test", rx), spec)
        self.assertIsNone(fs.ban_regex(" , | "))
        with self.assertRaises(SystemExit):
            fs.main(["--text", __file__, "--ban", " , "])

    def test_designated_is_banned_by_default(self):
        self.assertIn("banned_word", fs.scan_text("a designated workspace", self.ban))

    def test_text_files_are_scanned_line_by_line(self):
        base = ROOT / ".scratch"
        base.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as d:
            srt = Path(d) / "film.srt"
            srt.write_text("1\n00:00:01,000 --> 00:00:03,000\nOpen the claim.\n\n2\n00:00:03,000 --> 00:00:05,000\nA sample receipt from ops@gmail.com\n")
            rows = fs.scan_files([srt], self.ban, ["film.example.com"], None, None)
            self.assertEqual([r["line"] for r in rows], [7])
            self.assertEqual(set(rows[0]["hits"]), {"banned_word", "email"})
            self.assertEqual(fs.main(["--text", str(srt), "--allow-domain", "film.example.com"]), 1)

    def test_brands_raw_ids_and_banners(self):
        brands = fs.brand_regex(["Acme Bank"])
        hits = fs.scan_text("Acme Bank statement  js7a8b9c0d1e2f3g4h5i6j7k8l9m0n  Download started", self.ban, [], brands)
        self.assertEqual({"brand", "raw_id", "download_banner"}, set(hits))


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("tesseract") and Path(FONT).exists(),
                     "needs ffmpeg, tesseract and a font")
class FrameScanVideo(unittest.TestCase):
    def make(self, text, path):
        subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                        "color=c=white:s=1280x720:d=2:r=5", "-vf",
                        f"drawtext=fontfile={FONT}:text='{text}':fontsize=72:fontcolor=black:x=60:y=300",
                        "-pix_fmt", "yuv420p", str(path)], check=True)

    def test_a_banned_word_on_screen_fails_and_a_clean_film_passes(self):
        base = ROOT / ".scratch"
        base.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as d:
            d = Path(d)
            self.make("Demo workspace report", d / "bad.mp4")
            self.make("Quarterly report ready", d / "good.mp4")
            args = ["--workdir", str(d / "w"), "--out", str(d / "r.json")]
            self.assertEqual(fs.main([str(d / "bad.mp4")] + args), 1)
            flagged = json.loads((d / "r.json").read_text())["flagged"]
            self.assertTrue(flagged and "banned_word" in flagged[0]["hits"])
            self.assertEqual(fs.main([str(d / "good.mp4")] + args), 0)


if __name__ == "__main__":
    unittest.main()
