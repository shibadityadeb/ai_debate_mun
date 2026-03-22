"""Regression checks for CORS configuration."""
import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app  # noqa: E402


class CORSTestCase(unittest.TestCase):
    """Ensure browser preflight requests are accepted."""

    def setUp(self):
        self.client = TestClient(app)

    def test_vercel_origin_preflight_is_allowed(self):
        response = self.client.options(
            '/api/debate/run',
            headers={
                'Origin': 'https://ai-debate-mun.vercel.app',
                'Access-Control-Request-Method': 'POST',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get('access-control-allow-origin'),
            'https://ai-debate-mun.vercel.app',
        )


if __name__ == '__main__':
    unittest.main()
