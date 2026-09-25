import importlib.util
import json
import re
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
        self.assertEqual(result["referenced_images"], 40)

    def test_reader_pages_have_bottom_navigation(self):
        pages = list((ROOT / "chapters").glob("*.md"))
        pages += list((ROOT / "guides").glob("*.md"))
        pages += [path for path in (ROOT / "articles").glob("*.md")
                  if path.name != "README.md"]
        for page in pages:
            last_line = page.read_text(encoding="utf-8").rstrip().splitlines()[-1]
            self.assertEqual(last_line.count("["), 3, page.name)
            self.assertEqual(last_line.count("]"), 3, page.name)
            self.assertIn("[目录]", last_line, page.name)

    def test_example_admin_ports_default_to_loopback_and_onebot_stays_internal(self):
        compose = (ROOT / "examples/astrbot-napcat/compose.yaml").read_text(encoding="utf-8")
        example_env = (ROOT / "examples/astrbot-napcat/.env.example").read_text(encoding="utf-8")
        self.assertIn("ADMIN_BIND_IP=127.0.0.1", example_env)
        self.assertIn("${ADMIN_BIND_IP:-127.0.0.1}:6185:6185", compose)
        self.assertIn("${ADMIN_BIND_IP:-127.0.0.1}:6099:6099", compose)
        self.assertNotIn("6199:6199", compose)

    def test_handoff_example_is_valid_json_with_labeled_synthetic_history(self):
        example = json.loads(
            (ROOT / "examples/conversation-handoff-history.example.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual([item["role"] for item in example], ["user", "assistant"])
        self.assertTrue(example[0]["content"][0]["text"].startswith("【历史对话摘要】"))
        for heading in [
            "【初始目标 / 长期主线】",
            "【已讨论的核心话题与结论】",
            "【当前最新焦点】",
            "【关键配置 / 技术细节】",
            "【用户偏好与风格要求】",
            "【失败尝试 / 注意事项】",
            "【待办 / 下一步】",
        ]:
            self.assertIn(heading, example[0]["content"][0]["text"])
        self.assertEqual(example[1]["content"][0]["text"], "已收到")
        self.assertNotIn("<system_reminder>", json.dumps(example, ensure_ascii=False))

    def test_segmentation_example_keeps_spaces_inside_bubbles(self):
        pattern = (ROOT / "examples/astrbot-segment-regex.txt").read_text(
            encoding="utf-8"
        ).strip()
        cleanup = re.compile(r"^[。\s]+|[。\s]+$")

        def split(text):
            segments = re.findall(pattern, text, re.DOTALL | re.MULTILINE)
            return [cleaned for seg in segments if (cleaned := cleanup.sub("", seg).strip())]

        self.assertEqual(split("你好，今天怎么样？"), ["你好，", "今天怎么样？"])
        self.assertEqual(split("唔...\n你还醒着吗？"), ["唔...", "你还醒着吗？"])
        self.assertEqual(split("甲（乙）丙"), ["甲", "（乙）", "丙"])
        self.assertEqual(split("他说“好呀”然后笑了。"), ["他说", "“好呀”", "然后笑了"])
        self.assertEqual(split("hello world。 next"), ["hello world", "next"])

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

    def test_modified_handbook_figure_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            clone = Path(directory) / "book"
            shutil.copytree(ROOT, clone, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            figure = clone / "assets/book/04-future-task-redacted.png"
            figure.write_bytes(figure.read_bytes() + b"changed")
            result = VALIDATOR.validate(clone)
            self.assertTrue(any("hash mismatch" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
