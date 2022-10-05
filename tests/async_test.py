import asyncio
import brawling
from pathlib import Path
from datetime import datetime, timezone
import time

TAG = "#UC8L2YC0"
CLUB_TAG = "#2GLLYGG2G"
TEST_BRAWLER_ID = brawling.BrawlerID.SHELLY
PAGE_ITEMS = 42

token = (Path(__file__).parent.parent / ".token").read_text()
def assert_ne(l):
    assert not isinstance(l, brawling.ErrorResponse), str(l)

async def test_battle_log(client):
    log = await client.get_battle_log(TAG)

    assert not isinstance(log, brawling.ErrorResponse), str(log)
    assert len(log) > 0, "Empty battle log"

async def test_player(client):
    player = await client.get_player(TAG)

    assert_ne(player)
    assert player.tag == TAG, str(player)

async def test_club(client):
    club = await client.get_club(CLUB_TAG)

    assert_ne(club)
    assert club.tag == CLUB_TAG

async def test_club_members(client):
    members = await client.get_club_members(CLUB_TAG)

    assert_ne(members)
    assert len(members) > 0, "Empty club member list"

async def test_brawlers(client):
    brawlers = await client.get_brawlers()
    assert_ne(brawlers)
    assert len(brawlers) > 0, "Empty brawler list"

async def test_brawler(client):
    brawler = await client.get_brawler(TEST_BRAWLER_ID)
    assert_ne(brawler)
    assert brawler.id == TEST_BRAWLER_ID.value, "Invalid brawler id"

async def test_brawler_by_name(client):
    brawler = await client.get_brawler("COLT")
    assert_ne(brawler)
    assert brawler.id == brawling.BrawlerID.COLT.value, "Invalid brawler id"

async def test_bad_brawler(client):
    brawler = await client.get_brawler(0xdeadbeef)
    assert isinstance(brawler, brawling.ErrorResponse), str(brawler)

async def test_event_rotation(client):
    rotation = await client.get_event_rotation()
    change = rotation.next_change
    events = rotation.events
    now = datetime.now(timezone.utc)

    assert change > now, "Change had already happened?"
    assert len(events) > 0, "No events available"

async def test_club_ranking(client):
    rankings = await client.get_club_rankings("global")
    assert_ne(rankings)
    assert len(rankings) > 0

async def test_brawler_ranking(client):
    rankings = await client.get_brawler_rankings(16000000, 'global')
    assert_ne(rankings)
    assert len(rankings) > 0

async def test_player_ranking(client):
    rankings = await client.get_player_rankings('global')
    assert_ne(rankings)
    assert len(rankings) > 0

async def test_page_club_members(client):
    member_tags = [x.tag for x in await client.get_club_members(CLUB_TAG)]

    iterator_tags = []

    iterator = await client.page_club_members(CLUB_TAG, PAGE_ITEMS)
    async for page in iterator:
        assert len(page) > 0
        assert len(page) <= PAGE_ITEMS
        for p in page:
            iterator_tags.append(p.tag)

    assert len(member_tags) == len(iterator_tags)

    member_tags.sort()
    iterator_tags.sort()

    for x,y in zip(member_tags, iterator_tags):
        assert x == y

async def test_page_brawlers(client):
    brawler_ids = [x.id for x in await client.get_brawlers()]

    iterator_ids = []

    iterator =await  client.page_brawlers(PAGE_ITEMS)
    async for page in iterator:
        assert len(page) > 0
        assert len(page) <= PAGE_ITEMS
        for p in page:
            iterator_ids.append(p.id)

    assert len(brawler_ids) == len(iterator_ids)

    brawler_ids.sort()
    iterator_ids.sort()

    for x,y in zip(brawler_ids, iterator_ids):
        assert x == y

async def test_page_club_rankings(client):
    tags = [x.tag for x in await client.get_club_rankings()]

    iterator_tags = []

    iterator = await client.page_club_rankings(PAGE_ITEMS, max=len(tags))
    async for page in iterator:
        assert len(page) > 0
        assert len(page) <= PAGE_ITEMS
        for p in page:
            iterator_tags.append(p.tag)

    assert len(tags) == len(iterator_tags)

    tags.sort()
    iterator_tags.sort()

    for x,y in zip(tags, iterator_tags):
        assert x == y

async def test_page_player_rankings(client):
    # TODO : I don't know if it's a problem with API or not, but this test keeps failing.
    # Despite being exactly the same as other tests, this one fails to work with 'global' region.
    # It's highly likely that it's a coincidence and could fix itself by later,
    # or other tests could break as well. This does not reproduce if you use a region like 'pl' (at least now)

    tags = [x.tag for x in await client.get_player_rankings('global')]

    iterator_tags = []

    iterator = await client.page_player_rankings(PAGE_ITEMS, 'global', max=len(tags))
    async for page in iterator:
        assert len(page) > 0
        assert len(page) <= PAGE_ITEMS
        for p in page:
            iterator_tags.append(p.tag)

    assert len(tags) == len(iterator_tags)

    tags.sort()
    iterator_tags.sort()

    for x,y in zip(tags, iterator_tags):
        assert x == y

async def test_page_brawler_rankings(client):
    tags = [x.tag for x in await client.get_brawler_rankings(TEST_BRAWLER_ID, 'global')]

    iterator_tags = []

    iterator = await client.page_brawler_rankings(TEST_BRAWLER_ID, PAGE_ITEMS, max=len(tags))
    async for page in iterator:
        assert len(page) > 0
        assert len(page) <= PAGE_ITEMS
        for p in page:
            iterator_tags.append(p.tag)

    assert len(tags) == len(iterator_tags)

    tags.sort()
    iterator_tags.sort()

    for x,y in zip(tags, iterator_tags):
        print(x, y)
        assert x == y

async def main():
    now = time.time()
    async with brawling.AsyncClient(token, proxy=True, strict_errors=False) as client:
        await test_battle_log(client)
        await test_player(client)
        await test_club(client)
        await test_club_members(client)
        await test_brawlers(client)
        await test_brawler(client)
        await test_brawler_by_name(client)
        await test_bad_brawler(client)
        await test_event_rotation(client)
        await test_club_ranking(client)
        await test_brawler_ranking(client)
        await test_player_ranking(client)
        # await test_page_club_members(client)
        # await test_page_club_rankings(client)
        # await test_page_player_rankings(client)
        # await test_page_brawlers(client)
        # await test_page_brawler_rankings(client)
        print(f"All tests passed in {time.time() - now}")

asyncio.get_event_loop().run_until_complete(main())