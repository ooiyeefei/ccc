"""derive.py against a synthetic take (ffmpeg test pattern) and a hand-written sidecar in the shape
demo-video's harness writes. Run: python -m unittest skills/help-center-tutorial/tests/test_derive.py"""
import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = next(p for p in Path(__file__).resolve().parents if (p / ".git").exists())
sys.path.insert(0, str(HERE / "scripts"))
import derive as d  # noqa: E402

SHEET = HERE / "references" / "example-sheet.yaml"
HAVE_FFMPEG = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))
TIMES = {"open": (1.0, 1.6), "choose": (3.0, 3.6), "pick-type": (4.5, 5.0), "set-end": (6.0, 6.6), "save": (7.5, 8.1)}


def sidecar_for(sheet, bbox_on=None):
    ms = []
    for s in sheet["steps"]:
        tv, tp = TIMES[s["id"]]
        m = {"milestone": s["id"], "t_wall": tv, "t_video": tv, "t_proof": tp}
        if s["id"] == bbox_on:
            m["bbox"] = [100, 80, 300, 60]
        ms.append(m)
    ms.append({"milestone": "END", "t_video": 9.0, "t_proof": 9.0})
    return {"name": "block-time", "storyboard": {"path": "plan.json", "sha256": d.plan_hash(sheet)}, "milestones": ms}


class Lint(unittest.TestCase):
    def setUp(self):
        self.sheet = d.load_sheet(SHEET)

    def test_example_sheet_is_publishable(self):
        self.assertEqual(d.lint(self.sheet), [])

    def test_a_step_with_no_proof_text_is_refused(self):
        s = copy.deepcopy(self.sheet)
        del s["steps"][1]["proof"]
        self.assertTrue(any("missing 'proof'" in e for e in d.lint(s)))

    def test_duplicate_ids_and_undeclared_writes_are_refused(self):
        s = copy.deepcopy(self.sheet)
        s["steps"][1]["id"] = "open"
        s["writes"] = False
        errs = d.lint(s)
        self.assertTrue(any("duplicate step id" in e for e in errs))
        self.assertTrue(any("does not declare 'writes: true'" in e for e in errs))

    def test_a_proof_that_only_repeats_the_typed_text_is_refused(self):
        s = copy.deepcopy(self.sheet)
        s["steps"][3]["proof"] = "13:00"
        self.assertTrue(any("only repeats the typed text" in e for e in d.lint(s)))

    def test_a_label_missing_from_its_sentence_is_refused(self):
        s = copy.deepcopy(self.sheet)
        s["steps"][4]["label"] = "Spara"
        self.assertTrue(any("does not appear in its sentence" in e for e in d.lint(s)))

    def test_placeholders_block_a_recorder_but_not_a_draft(self):
        s = copy.deepcopy(self.sheet)
        s["steps"][0]["action"] = {"click": "TODO:empty-slot"}
        s["path"] = "PLACEHOLDER menu path"
        errs = d.lint(s)
        self.assertTrue(any("2 placeholder(s) remain" in e for e in errs))
        self.assertEqual(d.lint(s, draft=True), [])

    def test_plan_hash_ignores_wording_and_moves_with_actions_proof_locale_and_platform(self):
        base = d.plan_hash(self.sheet)
        wording = copy.deepcopy(self.sheet)
        wording["steps"][0]["caption"] = "A new caption."
        wording["steps"][0]["alt"] = "A different description of the picture."
        wording["title"] = "Another title"
        wording["not_covered"] = "Something else."
        self.assertEqual(d.plan_hash(wording), base)
        for mutate in (lambda s: s["steps"][4]["action"].update(click="[data-testid=save]"),
                       lambda s: s["steps"][4].update(proof="Saved"),
                       lambda s: s.update(locale="ms"),
                       lambda s: s.update(platform="mobile")):
            changed = copy.deepcopy(self.sheet)
            mutate(changed)
            self.assertNotEqual(d.plan_hash(changed), base)

    def test_beats_use_step_ids_as_labels_and_wait_for_the_proof_text(self):
        b = d.beats(self.sheet)
        self.assertEqual([x["label"] for x in b], ["open", "choose", "pick-type", "set-end", "save"])
        self.assertIn('includes("Blocked time added")', b[4]["ready"])
        self.assertEqual(b[3]["type"]["text"], "13:00")

    def test_a_mobile_tap_is_a_click_for_the_harness(self):
        s = copy.deepcopy(self.sheet)
        s["steps"][0]["action"] = {"tap": "[data-testid=empty-slot]"}
        self.assertEqual(d.beats(s)[0]["click"], "[data-testid=empty-slot]")

    def test_stem_names_the_platform_and_locale_so_outputs_never_collide(self):
        self.assertEqual(d.stem(self.sheet), "block-time.web")
        ms = d.with_strings(self.sheet, {"locale": "ms"})
        self.assertEqual(d.stem(ms), "block-time.web.ms")


class Queue(unittest.TestCase):
    def test_surfaces_match_changed_files(self):
        m = d.surface_matches
        self.assertTrue(m("route:/calendar", "src/app/calendar/page.tsx"))
        self.assertFalse(m("route:/calendar", "src/app/calendars-admin/page.tsx"))
        self.assertTrue(m("component:BlockedTimeDialog", "src/components/blocked-time-dialog.tsx"))
        self.assertFalse(m("component:BlockedTimeDialog", "src/components/invoice-dialog.tsx"))
        self.assertTrue(m("file:src/app/sales/**", "src/app/sales/invoices/page.tsx"))

    def test_queue_lists_only_sheets_that_name_a_changed_surface(self):
        base = ROOT / ".scratch"
        base.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as t:
            shutil.copy(SHEET, Path(t) / "block-time.yaml")
            other = copy.deepcopy(d.load_sheet(SHEET))
            other.update(task="send-quote", surfaces=["route:/sales/quotations"])
            (Path(t) / "send-quote.json").write_text(json.dumps(other))
            hits = d.queue(t, ["src/app/calendar/page.tsx", "README.md"])
            self.assertEqual([h["task"] for h in hits], ["block-time.web"])
            hits = d.queue(t, ["src/app/sales/quotations/new/page.tsx"])
            self.assertEqual([h["task"] for h in hits], ["send-quote.web"])
            self.assertEqual(d.queue(t, ["docs/notes.md"]), [])


@unittest.skipUnless(HAVE_FFMPEG, "needs ffmpeg")
class Derive(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base = ROOT / ".scratch"
        base.mkdir(exist_ok=True)
        cls.tmp = tempfile.TemporaryDirectory(dir=base)
        cls.dir = Path(cls.tmp.name)
        cls.take = cls.dir / "take.mp4"
        subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                        "testsrc2=s=640x400:r=10:d=10", "-pix_fmt", "yuv420p", str(cls.take)], check=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_derive(self, sheet, sidecar, out, video=False, drift=False):
        sc = self.dir / f"{out}.json"
        sc.write_text(json.dumps(sidecar))
        return d.derive(sheet, self.take, sc, self.dir / out, "build-42", "2026-10-29", 1.0, video, drift)

    def test_three_outputs_from_one_run(self):
        sheet = d.load_sheet(SHEET)
        res = self.run_derive(sheet, sidecar_for(sheet, bbox_on="open"), "out1", video=True)
        out = self.dir / "out1"
        for sid in TIMES:
            self.assertTrue((out / "img" / f"block-time.web-{sid}.png").stat().st_size > 1000, sid)
        self.assertEqual(set(res["clips"]), {"choose"})
        self.assertTrue((out / "clips" / "block-time.web-choose.mp4").exists())
        self.assertTrue((out / "block-time.web.mp4").exists())
        md = (out / "block-time.web.md").read_text()
        self.assertIn("1. Click an empty slot in the calendar.", md)
        self.assertIn("![The calendar showing the new blocked time greyed out.](img/block-time.web-save.png)", md)
        self.assertIn("Checked against build build-42 on 2026-10-29.", md)
        self.assertIn("## If something goes wrong", md)
        self.assertIn("## Not covered here", md)
        vtt = (out / "block-time.web.vtt").read_text()
        self.assertIn("00:00:01.000 --> 00:00:03.000\nClick an empty slot in the calendar.", vtt)
        self.assertIn("00:00:07.500 --> 00:00:09.000\nClick Save.", vtt)
        art = json.loads((out / "block-time.web.article.json").read_text())
        self.assertEqual([s["video_t"] for s in art["steps"]], [1.0, 3.0, 4.5, 6.0, 7.5])
        self.assertEqual(art["platform"], "web")

    def test_a_highlight_changes_the_frame(self):
        sheet = d.load_sheet(SHEET)
        self.run_derive(sheet, sidecar_for(sheet), "plain")
        self.run_derive(sheet, sidecar_for(sheet, bbox_on="open"), "marked")
        a = (self.dir / "plain" / "img" / "block-time.web-open.png").read_bytes()
        b = (self.dir / "marked" / "img" / "block-time.web-open.png").read_bytes()
        self.assertNotEqual(a, b)

    def test_changed_action_since_the_take_forces_a_rerecord_but_wording_does_not(self):
        sheet = d.load_sheet(SHEET)
        side = sidecar_for(sheet)
        edited = copy.deepcopy(sheet)
        edited["steps"][0]["caption"] = "Click any empty slot."
        self.run_derive(edited, side, "wording")
        moved = copy.deepcopy(sheet)
        moved["steps"][0]["action"]["click"] = "[data-testid=other-slot]"
        with self.assertRaises(SystemExit) as cm:
            self.run_derive(moved, side, "drifted")
        self.assertIn("re-record", str(cm.exception))
        self.run_derive(moved, side, "allowed", drift=True)

    def test_a_take_that_misses_a_step_is_refused(self):
        sheet = d.load_sheet(SHEET)
        side = sidecar_for(sheet)
        side["milestones"] = [m for m in side["milestones"] if m["milestone"] != "set-end"]
        with self.assertRaises(SystemExit) as cm:
            self.run_derive(sheet, side, "missing")
        self.assertIn("no milestone", str(cm.exception))

    def test_a_locale_take_is_its_own_plan_and_an_english_take_cannot_pass_as_it(self):
        sheet = d.load_sheet(SHEET)
        english = sidecar_for(sheet)
        malay = d.with_strings(sheet, {
            "locale": "ms", "title": "Blok masa dalam kalendar", "path": "Kalendar > Tambah > Masa disekat",
            "who": ["pemilik", "pengurus"], "_headings": {"steps": "Langkah", "checked": "Disemak pada versi {build}, {date}."},
            "open": {"do": "Klik slot kosong dalam Kalendar.", "label": "Kalendar", "proof": "Tambah masa disekat"},
        })
        with self.assertRaises(SystemExit):
            self.run_derive(malay, english, "ms-wrong")
        ms_side = sidecar_for(malay)
        self.run_derive(malay, ms_side, "ms", video=True)
        out = self.dir / "ms"
        md = (out / "block-time.web.ms.md").read_text()
        self.assertIn("1. Klik slot kosong dalam **Kalendar**.", md)
        self.assertIn("## Langkah", md)
        self.assertIn("Disemak pada versi build-42, 2026-10-29.", md)
        self.assertIn("**Who can do this:** pemilik, pengurus", md)
        self.assertIn('srclang="ms"', md)
        self.assertEqual(json.loads((out / "block-time.web.ms.article.json").read_text())["locale"], "ms")

    def test_screenshots_carry_a_hash_a_replay_can_compare(self):
        try:
            import PIL  # noqa: F401
        except ImportError:
            self.skipTest("Pillow not installed")
        sheet = d.load_sheet(SHEET)
        res = self.run_derive(sheet, sidecar_for(sheet), "hashes")
        h = res["hashes"]
        self.assertTrue(all(len(v) == 16 for v in h.values()))
        self.assertEqual(d.distance(h["open"], h["open"]), 0)
        self.assertEqual(d.distance("0" * 16, "f" * 16), 64)
        self.assertEqual(d.distance("0" * 16, "0000000000000003"), 2)


if __name__ == "__main__":
    unittest.main()
