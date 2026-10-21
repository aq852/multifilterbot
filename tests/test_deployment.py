import unittest
from pathlib import Path


class DeploymentTests(unittest.TestCase):
    def test_deployment_assets_exist(self) -> None:
        root = Path(__file__).parents[1]
        self.assertTrue((root / "Dockerfile").exists())
        self.assertTrue((root / "docker-compose.prod.yml").exists())
        self.assertTrue((root / "docs" / "deployment.md").exists())
