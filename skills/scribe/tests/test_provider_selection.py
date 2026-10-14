"""Provider dispatch regressions: no model loading, real audio or external requests."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / '.git').exists())
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location('scribe_transcribe', SCRIPTS / 'transcribe.py')
transcribe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(transcribe)


class ProviderSelectionTests(unittest.TestCase):
    def setUp(self):
        (ROOT / '.scratch').mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / '.scratch')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.audio = self.root / 'synthetic.wav'
        self.audio.write_bytes(b'synthetic dispatch fixture')
        self.out = self.root / 'transcripts'
        self.calls = []

    def provider(self, name):
        def run(path, args):
            self.calls.append(name)
            return {'model': 'stub', 'language': args.language,
                    'confidence_source': 'avg_logprob',
                    'segments': [{'start': 0.0, 'end': 1.0, 'text': 'Synthetic sentence.',
                                  'speaker': None, 'confidence': .9}]}
        return run

    def invoke(self, flags=(), providers=None):
        mapping = providers or {name: self.provider(name) for name in transcribe.PROVIDERS}
        argv = ['transcribe', str(self.audio), '--out', str(self.out), '--language', 'en', *flags]
        with patch.dict('os.environ', {'ELEVENLABS_API_KEY': 'synthetic-test-only',
                                     'DEEPGRAM_API_KEY': 'synthetic-test-only',
                                     'OPENAI_API_KEY': 'synthetic-test-only'}), \
             patch.object(transcribe, 'PROVIDERS', mapping), \
             patch.object(transcribe, 'duration_s', return_value=2.0), \
             patch.object(sys, 'argv', argv), \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            transcribe.main()

    def test_default_uses_local_even_with_all_cloud_keys(self):
        self.invoke()
        self.assertEqual(self.calls, ['local'])
        doc = json.loads((self.out / 'synthetic.json').read_text())
        self.assertEqual(doc['provider'], 'local')

    def test_legacy_auto_is_local_even_with_all_cloud_keys(self):
        self.invoke(['--provider', 'auto'])
        self.assertEqual(self.calls, ['local'])

    def test_hosted_provider_requires_explicit_selection(self):
        for name in ('elevenlabs', 'deepgram', 'openai'):
            with self.subTest(provider=name):
                self.calls.clear()
                self.invoke(['--provider', name])
                self.assertEqual(self.calls, [name])

    def test_missing_local_dependency_does_not_fall_back_to_cloud(self):
        providers = {name: self.provider(name) for name in transcribe.PROVIDERS}
        providers['local'] = transcribe.run_local
        with patch.dict(sys.modules, {'faster_whisper': None}), self.assertRaises(SystemExit):
            self.invoke(providers=providers)
        self.assertEqual(self.calls, [])
        self.assertFalse(list(self.out.glob('*.json')))

    def test_unsupported_diarization_fails_before_processing(self):
        for flags in (['--diarize'], ['--provider', 'auto', '--diarize'],
                      ['--provider', 'openai', '--diarize']):
            with self.subTest(flags=flags), self.assertRaises(SystemExit):
                self.invoke(flags)
        self.assertEqual(self.calls, [])
        self.assertFalse(self.out.exists())
