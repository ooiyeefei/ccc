"""Regressions use synthetic audio and stub QA; never load a speech model."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / '.git').exists())
sys.path.insert(0, str(SCRIPTS))
import audio_inputs as inputs
import voice_lines as voice
import mix_soundtrack as mixer


class InputFixture:
    def setUp(self):
        (ROOT / '.scratch').mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / '.scratch')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.lines = self.root / 'lines.json'
        self.out = self.root / 'clips'
        self.out.mkdir()

    def put(self, rows):
        self.lines.write_text(json.dumps(rows))

    def invoke(self, flags):
        with patch.object(sys, 'argv', ['voice_lines', str(self.lines), '--out', str(self.out), *flags]), contextlib.redirect_stderr(io.StringIO()):
            voice.main()


class InputTests(InputFixture, unittest.TestCase):
    def test_unsafe_and_duplicate_ids(self):
        for ident in ('../escape', '/absolute', 'x/y', '', '.', 'x\\y'):
            with self.subTest(ident=ident):
                self.put([{'id': ident, 'text': 'Synthetic words.'}])
                with self.assertRaises(ValueError):
                    inputs.records(self.lines, ('id', 'text'))
        self.put([{'id': 'A1'}, {'id': 'A1'}])
        with self.assertRaises(ValueError):
            inputs.records(self.lines, ('id',))

    def test_empty_and_malformed_records(self):
        for rows in ([], {}, [1], [{'id': 'A1'}]):
            self.put(rows)
            with self.assertRaises(ValueError):
                inputs.records(self.lines, ('id', 'text'))

    def test_nonfinite_and_out_of_range_numbers(self):
        for value in (float('nan'), float('inf'), -1, True, '1'):
            with self.assertRaises(ValueError):
                inputs.finite(value, 'time')
        with self.assertRaises(ValueError):
            inputs.finite(0, 'speed', positive=True)
        with self.assertRaises(ValueError):
            inputs.finite(1.21, 'speed', maximum=1.2)

    def test_symlink_rejected(self):
        target = self.root / 'protected.wav'
        target.write_bytes(b'synthetic')
        (self.out / 'A1.wav').symlink_to(target)
        with self.assertRaises(ValueError):
            inputs.child(self.out, 'A1.wav')
        self.assertEqual(target.read_bytes(), b'synthetic')

    def test_retained_clip_cannot_certify_old_text(self):
        self.put([{'id': 'A1', 'text': 'The new sentence.'}])
        (self.out / 'A1.wav').write_bytes(b'synthetic')
        (self.out / 'clips.json').write_text(json.dumps([{'id': 'A1', 'text': 'The old sentence.'}]))
        with patch.object(voice, 'dependencies') as dep:
            with self.assertRaises(SystemExit):
                self.invoke(['--check-only', '--check'])
            dep.assert_not_called()

    def test_unknown_only_id_and_missing_retained_clip(self):
        self.put([{'id': 'A1', 'text': 'Synthetic sentence.'}])
        for flags in (['--only', 'A9'], ['--check-only', '--check']):
            with self.subTest(flags=flags), self.assertRaises(SystemExit):
                self.invoke(flags)

    def test_missing_dependency_is_actionable(self):
        with patch.object(inputs.importlib.util, 'find_spec', return_value=None):
            with self.assertRaisesRegex(ValueError, 'missing dependencies: kokoro'):
                inputs.dependencies(('kokoro',))

    def test_respell_source_cannot_be_overwritten(self):
        self.put([{'id': 'A1', 'text': 'Synthetic sentence.'}])
        rules = self.out / 'clips-checked.json'
        rules.write_text('[]')
        with self.assertRaises(SystemExit):
            self.invoke(['--respell', str(rules)])
        self.assertEqual(rules.read_text(), '[]')

    def test_readback_miss_fails_command(self):
        self.put([{'id': 'A1', 'text': 'Synthetic sentence.'}])
        (self.out / 'A1.wav').write_bytes(b'synthetic')
        (self.out / 'clips.json').write_text(json.dumps([{'id': 'A1', 'text': 'Synthetic sentence.', 'duration': 1}]))
        with patch.object(voice, 'dependencies'), patch.object(voice, 'check', return_value=[{'id': 'A1'}]), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(ValueError, 'below threshold'):
                self.invoke(['--check-only', '--check'])

    def test_readback_reports_actual_mismatch_without_model(self):
        fake = types.SimpleNamespace(WhisperModel=lambda *a, **k: types.SimpleNamespace(
            transcribe=lambda *a, **k: ([types.SimpleNamespace(text='Different content.')], None)))
        with patch.dict(sys.modules, {'faster_whisper': fake}), contextlib.redirect_stdout(io.StringIO()):
            low = voice.check(self.out, [{'id': 'A1', 'text': 'Synthetic sentence.'}], 'stub', .85)
        self.assertEqual(len(low), 1)
        report = json.loads((self.out / 'clips-checked.json').read_text())
        self.assertEqual(report[0]['heard'], 'Different content.')

    @unittest.skipUnless(importlib.util.find_spec('numpy'), 'numpy required')
    def test_empty_and_silent_synthesis_refused(self):
        import numpy as np
        with self.assertRaises(ValueError):
            voice.synth(lambda *a, **k: [], 'text', 'af_heart', 1)
        with self.assertRaises(ValueError):
            voice.trim(np.zeros(100))


@unittest.skipUnless(importlib.util.find_spec('soundfile') and importlib.util.find_spec('numpy'), 'audio dependencies required')
class MixerTests(InputFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        import numpy as np
        import soundfile as sf
        self.np, self.sf = np, sf
        self.audio = .3 * np.sin(2 * np.pi * 220 * np.arange(2 * mixer.SR) / mixer.SR)
        sf.write(self.out / 'A1.wav', self.audio, mixer.SR, subtype='FLOAT')
        sf.write(self.out / 'A2.wav', self.audio, mixer.SR, subtype='FLOAT')
        self.bed = self.root / 'bed.wav'
        sf.write(self.bed, .8 * np.sin(2 * np.pi * 440 * np.arange(14 * mixer.SR) / mixer.SR), mixer.SR, subtype='FLOAT')
        self.place = self.root / 'placement.json'
        self.place.write_text(json.dumps([{'id': 'A1', 'at': 2}, {'id': 'A2', 'at': 8}]))
        self.mix = self.root / 'mix'

    def mix_call(self, flags=()):
        with patch.object(sys, 'argv', ['mixer', str(self.place), '--clips', str(self.out), '--out', str(self.mix), *flags]), contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            mixer.main()

    def test_overlap_and_tail_overrun_refused_before_output(self):
        self.place.write_text(json.dumps([{'id': 'A1', 'at': 0}, {'id': 'A2', 'at': 1}]))
        with self.assertRaises(SystemExit):
            self.mix_call(['--length', '10'])
        self.assertFalse(self.mix.exists())
        self.place.write_text(json.dumps([{'id': 'A1', 'at': 4}]))
        with self.assertRaises(SystemExit):
            self.mix_call(['--length', '5'])
        self.assertFalse(self.mix.exists())

    def test_input_output_alias_refused(self):
        (self.out / "narration.wav").write_bytes(b"protected synthetic source")
        with self.assertRaises(SystemExit):
            self.mix_call(['--out', str(self.out), '--music', str(self.out / 'narration.wav')])
        self.assertEqual((self.out / "narration.wav").read_bytes(), b"protected synthetic source")

    def test_mux_requires_film_before_writes(self):
        with self.assertRaises(SystemExit):
            self.mix_call(['--mux', str(self.root / 'final.mp4')])
        self.assertFalse(self.mix.exists())

    def test_shorter_mux_cannot_truncate_picture(self):
        film = self.root / 'film.mp4'
        subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-f', 'lavfi', '-i', 'color=s=32x32:r=10:d=12', '-c:v', 'libx264', str(film)], check=True)
        with self.assertRaises(SystemExit):
            self.mix_call(['--film', str(film), '--length', '11', '--mux', str(self.root / 'final.mp4')])
        self.assertFalse(self.mix.exists())

    def test_mux_preserves_full_picture(self):
        film = self.root / 'film.mp4'
        final = self.root / 'final.mp4'
        subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-f', 'lavfi', '-i', 'color=s=32x32:r=10:d=12', '-c:v', 'libx264', str(film)], check=True)
        self.mix_call(['--film', str(film), '--mux', str(final)])
        self.assertAlmostEqual(mixer.duration(final), mixer.duration(film), places=3)

    def test_real_mix_has_float_intermediate_and_mastered_outputs(self):
        self.mix_call(['--length', '12', '--music', str(self.bed)])
        self.assertEqual(self.sf.info(self.mix / 'mix.wav').subtype, 'FLOAT')
        self.assertEqual(self.sf.info(self.mix / 'soundtrack.wav').channels, 2)
        self.assertAlmostEqual(mixer.lufs(self.mix / 'narration.wav'), -23, delta=.3)
        self.assertAlmostEqual(mixer.lufs(self.mix / 'soundtrack.m4a'), -16, delta=1)
        self.assertEqual(self.sf.info(self.mix / 'soundtrack.wav').frames, 12 * mixer.SR)

    def test_music_only_and_silent_music(self):
        self.place.write_text('[]')
        self.mix_call(['--length', '12', '--music', str(self.bed)])
        self.assertAlmostEqual(mixer.lufs(self.mix / 'soundtrack.m4a'), -16, delta=1)
        self.sf.write(self.bed, self.np.zeros(2 * mixer.SR), mixer.SR)
        with self.assertRaisesRegex(ValueError, 'silent'):
            self.mix_call(['--length', '12', '--music', str(self.bed)])

    def test_duck_mask_and_ramps(self):
        mask = self.np.zeros(mixer.SR * 4, self.np.float32)
        mask[mixer.SR:3*mixer.SR] = 1
        duck = mixer.box(mask, int(.3*mixer.SR))
        gain = 1 - duck * (1 - 10 ** (-8 / 20))
        self.assertAlmostEqual(20 * self.np.log10(gain[2*mixer.SR]), -8, places=4)
        self.assertEqual(gain[mixer.SR//2], 1)
        self.assertTrue(1 > gain[mixer.SR] > 10 ** (-8/20))
        edge = mixer.box(self.np.ones(mixer.SR, self.np.float32), int(.3*mixer.SR))
        self.np.testing.assert_allclose(edge, 1)
