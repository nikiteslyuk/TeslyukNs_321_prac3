"""Client test."""
import unittest
from unittest.mock import MagicMock, patch
from io import StringIO
from mood.client.__main__ import MUDclient


class TestClientCommands(unittest.TestCase):
    """TestClientCommands."""

    def setUp(self):
        """Set up."""
        self.socket_mock = MagicMock()
        self.client = MUDclient(self.socket_mock)

    def test_attack_command_conversion(self):
        """Test attck."""
        test_cases = [
            ("dragon with spear", "attack dragon 15 spear\n"),
            ("jgsbat with axe", "attack jgsbat 20 axe\n"),
            ("moose", "attack moose 10 sword\n")
        ]
        for inp, out in test_cases:
            self.client.do_attack(inp)
            self.client.soc.sendall.assert_called_with(bytes(out.encode()))

    def test_attack_invalid_parameters(self):
        """Test attack."""
        test_cases = [
            ("", "Invalid arguments"),
            ("dragon with", "Invalid arguments"),
            ("dragon with unknown_weapon", "Unknown weapon"),
            ("dragon spear", "Invalid arguments"),
            ("dragon with spear extra", "Invalid arguments")
        ]

        with patch('sys.stdout', new=StringIO()) as fake_out:
            for inp, out in test_cases:
                self.client.soc.sendall.reset_mock()
                self.client.do_attack(inp)
                self.client.soc.sendall.assert_not_called()
                self.assertIn(out, fake_out.getvalue().strip())

    def test_addmon_command_conversion(self):
        """Test addmon."""
        test_cases = [
            ("jgsbat hello 'BAT!' hp 50 coords 4 5",
                "addmon jgsbat 50 5 4 'BAT!'\n"
             ),
            ('moose hello "Hello, world!" hp 100 coords 1 0',
                "addmon moose 100 0 1 'Hello, world!'\n"
             )
        ]
        for inp, out in test_cases:
            self.client.do_addmon(inp)
            self.client.soc.sendall.assert_called_with(bytes(out.encode()))


if __name__ == '__main__':
    unittest.main()
