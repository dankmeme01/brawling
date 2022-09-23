from pathlib import Path
import brawling
import unittest

TAG = "#UC8L2YC0"

class Tests(unittest.TestCase):
    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)

        token = (Path(__file__).parent.parent / ".token").read_text()
        self.client = brawling.Client(token, proxy=True, strict_errors=False)

    def test_battle_log(self):
        log = self.client.get_battle_log(TAG)
        self.assertNotIsInstance(log, brawling.ErrorResponse)
        print(log[0])

    def test_player(self):
        player = self.client.get_player(TAG)
        self.assertNotIsInstance(player, brawling.ErrorResponse)
        self.assertEqual(player.tag, TAG)
        print(player)

if __name__ == '__main__':
    unittest.main()
