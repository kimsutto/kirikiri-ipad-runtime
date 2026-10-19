import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('checker', Path(__file__).resolve().parents[1] / 'tools/check_public.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

class PublicCheckTests(unittest.TestCase):
    def test_rejects_binary_private_path_and_private_name(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'README.md').write_text('neutral instructions')
            self.assertEqual(checker.inspect(root)[1], [])
            (root / 'data.xp3').write_bytes(b'\x00')
            self.assertTrue(checker.inspect(root)[1])
            (root / 'data.xp3').unlink()
            (root / 'README.md').write_text('/' + 'Users' + '/' + 'example' + '/project')
            self.assertTrue(checker.inspect(root)[1])
            (root / 'README.md').write_text('private-project-marker')
            self.assertTrue(checker.inspect(root, ['private-project-marker'])[1])
    def test_rejects_symlinks(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'escape').symlink_to('/tmp')
            self.assertTrue(checker.inspect(root)[1])

if __name__ == '__main__': unittest.main()
