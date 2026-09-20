import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validator", ROOT / "scripts/validate_book.py")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class LinkTests(unittest.TestCase):
    def test_fenced_examples_are_not_links(self):
        source = "````markdown\n```\n![not real](no.png)\n```\n````\n[real](README.md)"
        self.assertEqual(VALIDATOR.prose(source), "[real](README.md)")

    def test_relative_paths(self):
        source = ROOT / "chapters/chapter.md"
        self.assertEqual(VALIDATOR.local_target(ROOT, source, "../README.md"), ROOT / "README.md")

    def test_external_links(self):
        self.assertIsNone(VALIDATOR.local_target(ROOT, ROOT / "README.md", "https://example.org/a"))

    def test_site_root_paths_are_rejected(self):
        with self.assertRaises(ValueError):
            VALIDATOR.local_target(ROOT, ROOT / "README.md", "/blog-assets/a.webp")

    def test_escape_is_rejected(self):
        with self.assertRaises(ValueError):
            VALIDATOR.local_target(ROOT, ROOT / "README.md", "../outside.md")


class BookTests(unittest.TestCase):
    def test_current_book(self):
        result = VALIDATOR.validate(ROOT)
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual(result["referenced_images"], 32)

    def test_missing_image_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            clone = Path(directory) / "book"
            shutil.copytree(ROOT, clone, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            image = next((clone / "assets").rglob("*.webp"))
            image.unlink()
            result = VALIDATOR.validate(clone)
            self.assertFalse(result["ok"])
            self.assertTrue(any("missing" in error for error in result["errors"]))

    def test_modified_article_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            clone = Path(directory) / "book"
            shutil.copytree(ROOT, clone, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            article = clone / "articles/astrbot-plugin-dev-experience.md"
            article.write_bytes(article.read_bytes() + b"\nChanged.\n")
            result = VALIDATOR.validate(clone)
            self.assertTrue(any("hash mismatch" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
