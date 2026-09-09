import hashlib
from io import BytesIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from uncertainty_risk_control.goemotions.sources import checked_download


class SourceAcquisitionTests(unittest.TestCase):
    def test_verified_download_is_atomic_and_does_not_overwrite(self):
        content = b"synthetic upstream fixture\n"
        digest = hashlib.sha256(content).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "source.txt"
            with patch("urllib.request.urlopen", return_value=BytesIO(content)):
                checked_download("https://example.invalid/test", destination, digest, len(content))
            self.assertEqual(destination.read_bytes(), content)
            with self.assertRaises(ValueError):
                checked_download("https://example.invalid/test", destination, digest, len(content))
            self.assertEqual(list(Path(directory).iterdir()), [destination])

    def test_changed_upstream_bytes_fail_without_leaving_an_asset(self):
        for content, size in ((b"wrong", 5), (b"too long", 3)):
            with tempfile.TemporaryDirectory() as directory:
                destination = Path(directory) / "source.txt"
                with patch("urllib.request.urlopen", return_value=BytesIO(content)), self.assertRaises(ValueError):
                    checked_download("https://example.invalid/test", destination, "0" * 64, size)
                self.assertFalse(destination.exists())
                self.assertEqual(list(Path(directory).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
