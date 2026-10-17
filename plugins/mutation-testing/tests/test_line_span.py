"""Unit tests for line-span helper; no .NET runtime needed."""
import importlib.util
from pathlib import Path
import tempfile
import unittest


HELPER = Path(__file__).resolve().parents[1] / "scripts" / "line-span.py"
spec = importlib.util.spec_from_file_location("line_span", HELPER)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SpanTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name) / "App"
        (self.root / "Services").mkdir(parents=True)
        self.source = self.root / "Services" / "OrderService.cs"

    def write(self, text):
        with self.source.open("w", encoding="utf-8", newline="") as f:
            f.write(text)

    def test_project_relative_and_line_span(self):
        self.write("class A {\n    bool Flag => true;\n}\n")
        self.assertEqual(
            module.selector(self.root, self.source, 2, 2),
            "Services/OrderService.cs{10..33}",
        )

    def test_crlf_and_unicode_are_utf16_positions(self):
        self.write("😀\r\nX\r\n")
        self.assertEqual(
            module.selector(self.root, self.source, 2, 2),
            "Services/OrderService.cs{4..7}",
        )

    def test_invalid_line_range(self):
        self.write("one\n")
        for start, end in [(0, 1), (1, 2), (2, 1)]:
            with self.subTest(start=start, end=end):
                with self.assertRaises(ValueError):
                    module.selector(self.root, self.source, start, end)

    def test_reject_source_outside_project(self):
        outside = self.root.parent / "outside.cs"
        outside.write_text("class O {}")
        with self.assertRaisesRegex(ValueError, "inside"):
            module.selector(self.root, outside, 1, 1)

    def test_reject_non_csharp_source(self):
        other = self.root / "README.md"
        other.write_text("hi")
        with self.assertRaisesRegex(ValueError, "existing .cs"):
            module.selector(self.root, other, 1, 1)


if __name__ == "__main__":
    unittest.main()
