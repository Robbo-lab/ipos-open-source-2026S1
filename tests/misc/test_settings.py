import unittest

from app.core.settings import settings, Settings


class TestSettings(unittest.TestCase):
    """
    Tests the settings module
    These tests verify that configuration values are set correctly in settings.py.
    """

    # --- Module checks ---

    def test_settings_importable(self):
        """The Settings module is importable and it exists."""
        self.assertIsNotNone(settings)

    def test_settings_is_correct_type(self):
        """Settings instance is the correct type."""
        self.assertIsInstance(settings, Settings)

    # --- Default values ---

    def test_default_host(self):
        """Host defaults to localhost."""
        self.assertEqual(settings.host, "localhost")

    def test_default_port(self):
        """Port defaults to 8003."""
        self.assertEqual(settings.port, 8003)

    def test_default_mcp_base_url(self):
        """MCP base URL defaults to http://localhost:8003."""
        self.assertEqual(settings.mcp_base_url, "http://localhost:8003")

    def test_default_mcp_protocol_version(self):
        """MCP protocol version defaults to 2025-06-18."""
        self.assertEqual(settings.mcp_protocol_version, "2025-06-18")

    # --- Value validation ---

    def test_host_is_string(self):
        """Host is a string."""
        self.assertIsInstance(settings.host, str)

    def test_port_is_integer(self):
        """Port is an integer."""
        self.assertIsInstance(settings.port, int)

    def test_mcp_base_url_starts_with_http(self):
        """MCP base URL begins with http."""
        self.assertTrue(settings.mcp_base_url.startswith("http"))

    def test_protocol_version_format(self):
        """Protocol version follows YYYY-MM-DD date format."""
        parts = settings.mcp_protocol_version.split("-")
        self.assertEqual(len(parts), 3)


if __name__ == "__main__":
    unittest.main()