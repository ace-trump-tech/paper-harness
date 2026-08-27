import tempfile
import unittest
from pathlib import Path

from paper_harness.report import write_latex_project


class LatexReportTest(unittest.TestCase):
    def test_writes_escaped_latex(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_latex_project(Path(tmp), {"title": "A & B", "objective": "x_y"}, [])
            text = path.read_text(encoding="utf-8")
            self.assertIn(r"A \& B", text)
            self.assertIn(r"x\_y", text)
            self.assertTrue((Path(tmp) / "references.bib").exists())


if __name__ == "__main__":
    unittest.main()
