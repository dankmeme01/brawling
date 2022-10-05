from pathlib import Path
from datetime import datetime, timezone
import unittest

import brawling

TAG = "#UC8L2YC0"
CLUB_TAG = "#2GLLYGG2G"
TEST_BRAWLER_ID = brawling.BrawlerID.SHELLY
PAGE_ITEMS = 42

# unittest seems to reinitialize the Tests class each test, so bring this out

token = (Path(__file__).parent.parent / ".token").read_text()
global_client = brawling.Client(token, proxy=True, strict_errors=False)

class Tests(unittest.TestCase):
    def __init__(self, *a, **kw) -> None:
        global global_client
        super().__init__(*a, **kw)
        self.client = global_client

    def test_battle_log(self):
        log = self.client.get_battle_log(TAG)
        self.assertNotIsInstance(log, brawling.ErrorResponse, str(log))
        self.assertGreater(len(log), 0, "Empty battle log")

    def test_player(self):
        player = self.client.get_player(TAG)
        self.assertNotIsInstance(player, brawling.ErrorResponse, str(player))
        self.assertEqual(player.tag, TAG, str(player))

    def test_club(self):
        club = self.client.get_club(CLUB_TAG)
        self.assertNotIsInstance(club, brawling.ErrorResponse, str(club))
        self.assertEqual(club.tag, CLUB_TAG, str(club))

    def test_club_members(self):
        members = self.client.get_club_members(CLUB_TAG)
        self.assertNotIsInstance(members, brawling.ErrorResponse, str(members))
        self.assertGreater(len(members), 0, "Empty club member list")

    def test_brawlers(self):
        brawlers = self.client.get_brawlers()
        self.assertNotIsInstance(brawlers, brawling.ErrorResponse, str(brawlers))
        self.assertGreater(len(brawlers), 0, "Empty brawler list")

    def test_brawler(self):
        brawler = self.client.get_brawler(TEST_BRAWLER_ID)
        self.assertNotIsInstance(brawler, brawling.ErrorResponse, str(brawler))
        self.assertEqual(brawler.id, TEST_BRAWLER_ID.value, "Invalid brawler id")

    def test_brawler_by_name(self):
        brawler = self.client.get_brawler("COLT")
        self.assertNotIsInstance(brawler, brawling.ErrorResponse, str(brawler))
        self.assertEqual(brawler.id, brawling.BrawlerID.COLT.value, "Invalid brawler id")

    def test_bad_brawler(self):
        brawler = self.client.get_brawler(0xdeadbeef)
        self.assertIsInstance(brawler, brawling.ErrorResponse, str(brawler))

    def test_event_rotation(self):
        rotation = self.client.get_event_rotation()
        change = rotation.next_change
        events = rotation.events
        now = datetime.now(timezone.utc)

        self.assertGreater(change, now, "Change had already happened?")
        self.assertGreater(len(events), 0, "No events available")

    def test_club_ranking(self):
        rankings = self.client.get_club_rankings("global")
        self.assertNotIsInstance(rankings, brawling.ErrorResponse, str(rankings))
        self.assertGreater(len(rankings), 0)

    def test_brawler_ranking(self):
        rankings = self.client.get_brawler_rankings(16000000, 'global')
        self.assertNotIsInstance(rankings, brawling.ErrorResponse, str(rankings))
        self.assertGreater(len(rankings), 0)

    def test_player_ranking(self):
        rankings = self.client.get_player_rankings('global')
        self.assertNotIsInstance(rankings, brawling.ErrorResponse, str(rankings))
        self.assertGreater(len(rankings), 0)

    def test_page_club_members(self):
        member_tags = [x.tag for x in self.client.get_club_members(CLUB_TAG)]

        iterator_tags = []

        iterator = self.client.page_club_members(CLUB_TAG, PAGE_ITEMS)
        for page in iterator:
            self.assertGreater(len(page), 0)
            self.assertLessEqual(len(page), PAGE_ITEMS)
            for p in page:
                iterator_tags.append(p.tag)

        self.assertEqual(len(member_tags), len(iterator_tags))

        member_tags.sort()
        iterator_tags.sort()

        self.assertListEqual(member_tags, iterator_tags)

    def test_page_brawlers(self):
        brawler_ids = [x.id for x in self.client.get_brawlers()]

        iterator_ids = []

        iterator = self.client.page_brawlers(PAGE_ITEMS)
        for page in iterator:
            self.assertGreater(len(page), 0)
            self.assertLessEqual(len(page), PAGE_ITEMS)
            for p in page:
                iterator_ids.append(p.id)

        self.assertEqual(len(brawler_ids), len(iterator_ids))

        brawler_ids.sort()
        iterator_ids.sort()

        self.assertListEqual(brawler_ids, iterator_ids)

    def test_page_club_rankings(self):
        tags = [x.tag for x in self.client.get_club_rankings()]

        iterator_tags = []

        iterator = self.client.page_club_rankings(PAGE_ITEMS, max=len(tags))
        for page in iterator:
            self.assertGreater(len(page), 0)
            self.assertLessEqual(len(page), PAGE_ITEMS)
            for p in page:
                iterator_tags.append(p.tag)

        self.assertEqual(len(tags), len(iterator_tags))

        tags.sort()
        iterator_tags.sort()

        self.assertListEqual(tags, iterator_tags)

    def test_page_player_rankings(self):
        # TODO : I don't know if it's a problem with API or not, but this test keeps failing.
        # Despite being exactly the same as other tests, this one fails to work with 'global' region.
        # It's highly likely that it's a coincidence and could fix itself by later,
        # or other tests could break as well. This does not reproduce if you use a region like 'pl' (at least now)

        tags = [x.tag for x in self.client.get_player_rankings('global')]

        iterator_tags = []

        iterator = self.client.page_player_rankings(PAGE_ITEMS, 'global', max=len(tags))
        for page in iterator:
            self.assertGreater(len(page), 0)
            self.assertLessEqual(len(page), PAGE_ITEMS)
            for p in page:
                iterator_tags.append(p.tag)

        self.assertEqual(len(tags), len(iterator_tags))

        tags.sort()
        iterator_tags.sort()

        self.assertListEqual(tags, iterator_tags)

    def test_page_brawler_rankings(self):
        tags = [x.tag for x in self.client.get_brawler_rankings(TEST_BRAWLER_ID, 'global')]

        iterator_tags = []

        iterator = self.client.page_brawler_rankings(TEST_BRAWLER_ID, PAGE_ITEMS, max=len(tags))
        for page in iterator:
            self.assertGreater(len(page), 0)
            self.assertLessEqual(len(page), PAGE_ITEMS)
            for p in page:
                iterator_tags.append(p.tag)

        self.assertEqual(len(tags), len(iterator_tags))

        tags.sort()
        iterator_tags.sort()

        self.assertListEqual(tags, iterator_tags)

if __name__ == '__main__':
    unittest.main()