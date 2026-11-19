"""Unit tests for FastAPI endpoints, authentication, concurrency lock, and error handling."""

import os
import subprocess
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app, runner


class TestRPAEndpoints(unittest.TestCase):
    """Verify health, status, auth, concurrency, and RPA trigger endpoints."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.env_patch = patch.dict(os.environ, {"ROBOT_OUTPUT_DIR": self.temp_dir.name})
        self.env_patch.start()
        self.client = TestClient(app)

    def tearDown(self) -> None:
        self.env_patch.stop()
        self.temp_dir.cleanup()

    def test_health_check_is_public(self) -> None:
        with patch.dict(os.environ, {"API_KEY": "super-secret-key"}):
            response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "service": "rpa-api"})

    def test_missing_api_key_returns_401_when_configured(self) -> None:
        with patch.dict(os.environ, {"API_KEY": "super-secret-key"}):
            response = self.client.post("/api/v1/rpa/register-visitor")
        self.assertEqual(response.status_code, 401)

    def test_invalid_api_key_returns_401(self) -> None:
        with patch.dict(os.environ, {"API_KEY": "super-secret-key"}):
            response = self.client.get(
                "/api/v1/rpa/status",
                headers={"X-API-Key": "wrong-key"},
            )
        self.assertEqual(response.status_code, 401)

    def test_status_endpoint_with_valid_api_key(self) -> None:
        with patch.dict(os.environ, {"API_KEY": "super-secret-key"}):
            response = self.client.get(
                "/api/v1/rpa/status",
                headers={"X-API-Key": "super-secret-key"},
            )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("running", body)
        self.assertFalse(body["running"])

    @patch("app.runner.subprocess.run")
    @patch("pathlib.Path.exists", return_value=True)
    def test_register_visitor_success(
        self, _mock_exists: MagicMock, mock_run: MagicMock
    ) -> None:
        mock_run.return_value = MagicMock(returncode=0, stdout="1 test, 1 passed", stderr="")
        with patch.dict(os.environ, {"API_KEY": "test-key"}):
            response = self.client.post(
                "/api/v1/rpa/register-visitor",
                headers={"X-API-Key": "test-key"},
            )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "success")
        self.assertEqual(body["returncode"], 0)
        self.assertIn("1 passed", body["salida"])
        self.assertIsInstance(body["duration_seconds"], float)

    @patch("app.runner.subprocess.run")
    @patch("pathlib.Path.exists", return_value=True)
    def test_ejecutar_login_failure_returns_500(
        self, _mock_exists: MagicMock, mock_run: MagicMock
    ) -> None:
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="Element not found")
        with patch.dict(os.environ, {"API_KEY": ""}):
            response = self.client.get("/ejecutar-login")
        self.assertEqual(response.status_code, 500)
        body = response.json()
        self.assertEqual(body["status"], "error")
        self.assertEqual(body["returncode"], 1)

    @patch(
        "app.runner.subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd="robot", timeout=120),
    )
    @patch("pathlib.Path.exists", return_value=True)
    def test_timeout_returns_504(
        self, _mock_exists: MagicMock, _mock_run: MagicMock
    ) -> None:
        with patch.dict(os.environ, {"API_KEY": ""}):
            response = self.client.post("/api/v1/rpa/register-visitor")
        self.assertEqual(response.status_code, 504)

    @patch("pathlib.Path.exists", return_value=True)
    def test_concurrent_execution_returns_409(self, _mock_exists: MagicMock) -> None:
        acquired = runner._lock.acquire(blocking=False)
        self.assertTrue(acquired)
        try:
            with patch.dict(os.environ, {"API_KEY": ""}):
                response = self.client.post("/api/v1/rpa/register-visitor")
            self.assertEqual(response.status_code, 409)
        finally:
            runner._lock.release()


if __name__ == "__main__":
    unittest.main()
