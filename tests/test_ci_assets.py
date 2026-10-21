import unittest
from pathlib import Path


class CIAssetTests(unittest.TestCase):
    def test_workflow_exists(self) -> None:
        workflow = Path(__file__).parents[1] / ".github" / "workflows" / "ci.yml"
        self.assertTrue(workflow.exists())
        self.assertIn("python -m unittest discover", workflow.read_text())
