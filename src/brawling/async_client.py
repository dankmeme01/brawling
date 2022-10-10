from .client import *
from .exceptions import generate_exception
from .models import *
from .util import BrawlerID, AsyncRequestPaginator

from typing import Union, Optional, Iterator
from pathlib import Path
from urllib.parse import quote_plus
from datetime import timedelta
from difflib import SequenceMatcher

try:
    import aiohttp
    import asyncio
    HAS_AIOHTTP = True
except (ModuleNotFoundError, ImportError):
    HAS_AIOHTTP = False

try:
    from aiohttp_client_cache import CachedSession, SQLiteBackend
    HAS_CACHE = True
except (ModuleNotFoundError, ImportError):
    HAS_CACHE = False

__all__ = [
    "AsyncClient"
]

if not HAS_AIOHTTP:
    class AsyncClient:
        def __init__(self) -> None:
            raise NotImplementedError("async support not installed")

        def __getattribute__(self, __name: str):
            raise NotImplementedError("async support not installed")

else:
    class AsyncClient(Client):
        def __init__(self, token: Union[str, Path], *, proxy: bool = False, strict_errors: bool = True, force_no_cache: bool = False, force_no_sort: bool = False):
            self._setups(token, proxy, strict_errors, force_no_cache, force_no_sort, cache_const=HAS_CACHE)

            self._open = True
            if not self._caching:
                self._session = aiohttp.ClientSession()
            else:
                self._session = CachedSession(cache=SQLiteBackend(
                    expire_after=timedelta(hours=1),
                    cache_control=True,
                    use_temp=True,
                    cache_name='.bsapi_acache'
                ))

        # python methods, dunder and not

        async def aclose(self):
            self._open = False
            await self._session.close()

        def __del__(self):
            if self._open:
                self._logger.error("Client destructed before calling aclose()")

        def __repr__(self) -> str:
            return super().__repr__().replace("Client", "AsyncClient")

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            await self.aclose()

        # util

        async def _get(self, url: str, params: dict = None) -> Union[ErrorResponse, Union[dict, list]]:
            if not self._open:
                raise RuntimeError("Client has already been closed")

            if not url.startswith(self._base):
                url = self._base + quote_plus(url, safe='/')
            else:
                url = self._base + quote_plus(url[len(self._base):], safe='/')

            async with self._session.get(url, headers=self._headers, params=params) as r:
                while r.status == 429:
                    self._logger.warning("we got throttled, waiting 10 seconds and repeating")
                    await asyncio.sleep(10)
                    r = await self._session.get(url, headers=self._headers, params=params).__aenter__()

                self._logger.info(f"got url {url}, status {r.status}")

                if r.status != 200:
                    if not await r.text():
                        raise Exception(f"Got an error and no message, code: {r.status}")

                    json: dict = await r.json()
                    exc = generate_exception(r.status, json.get("reason", ''), json.get("message", ''))

                    self._logger.info("generated exception: %s", str(exc))

                    return self._exc_wrapper(exc)

                json = await r.json()
                return json

        async def _brawler_id(self, bid: Union[Union[int, str], BrawlerID]):
            if isinstance(bid, BrawlerID):
                return str(bid.value)

            val = str(bid).upper()
            if val.isdigit():
                return val

            # we got a name
            all_brawlers = await self.get_brawlers()
            table = {b.name.upper(): str(b.id) for b in all_brawlers}

            if val in table:
                return table[val]

            # not found

            closest = (0, None)
            for name in table.keys():
                match = SequenceMatcher(lambda x: x in " \t-.", name, val).ratio()
                if match > closest[0]:
                    closest = (match, name)

            if closest[0] == 1:
                return table[closest[1]]

            raise KeyError(f"Could not find the brawler. Closest match: {closest[1]} with {(closest[0]*100):.1f}% confidence")

        # public api methods

        async def get_battle_log(self, tag: str) -> list[Battle]:
            """Get a list of recent battles of a player by their tag. According to the API, it may take up to 30 minutes for a new battle to appear."""
            tag = self._verify_tag(tag)
            if isinstance(tag, Exception):
                return self._exc_wrapper(tag)

            res = await self._get(f"/players/{tag}/battlelog")
            if isinstance(res, ErrorResponse):
                return res

            battle_list = res["items"]

            battles = []

            for b in battle_list:
                battles.append(SoloBattle.from_json(b) if "players" in b["battle"] else TeamBattle.from_json(b))

            if self._sort:
                # most recent battles first
                battles.sort(key=lambda x: x.battle_time, reverse=True)

            return battles

        async def get_player(self, tag: str) -> Player:
            """Get information about a player by their tag."""
            tag = self._verify_tag(tag)
            if isinstance(tag, Exception):
                return self._exc_wrapper(tag)

            res = await self._get(f"/players/{tag}")
            if isinstance(res, ErrorResponse):
                return res

            return Player.from_json(res)

        # clubs

        async def get_club_members(self, tag: str) -> list[ClubMember]:
            """Get members of a club by its tag."""
            tag = self._verify_tag(tag)
            if isinstance(tag, Exception):
                return self._exc_wrapper(tag)

            res = await self._get(f"/clubs/{tag}/members")
            if isinstance(res, ErrorResponse):
                return res

            lst = self._unwrap_list(res["items"], ClubMember)

            return lst

        async def get_club(self, tag: str) -> Club:
            """Get the information about a club by its tag."""
            tag = self._verify_tag(tag)
            if isinstance(tag, Exception):
                return self._exc_wrapper(tag)

            res = await self._get(f"/clubs/{tag}")
            if isinstance(res, ErrorResponse):
                return res

            return Club.from_json(res)

        # rankings

        # -- power play seasons not included due to being obsolete -- #

        async def get_club_rankings(self, region: Optional[str] = None) -> list[ClubRanking]:
            if region is None:
                region = 'global'

            res = await self._get(f"/rankings/{region}/clubs")
            if isinstance(res, ErrorResponse):
                return res

            return self._unwrap_list(res["items"], ClubRanking)

        async def get_brawler_rankings(self, brawler_id: Union[Union[int, str], BrawlerID], region: Optional[str] = None) -> list[BrawlerRanking]:
            if region is None:
                region = 'global'

            res = await self._get(f"/rankings/{region}/brawlers/{await self._brawler_id(brawler_id)}")
            if isinstance(res, ErrorResponse):
                return res

            return self._unwrap_list(res["items"], BrawlerRanking)

        async def get_player_rankings(self, region: Optional[str] = None) -> list[PlayerRanking]:
            if region is None:
                region = 'global'

            res = await self._get(f"/rankings/{region}/players")
            if isinstance(res, ErrorResponse):
                return res

            return self._unwrap_list(res["items"], PlayerRanking)

        # brawlers

        async def get_brawlers(self) -> list[Brawler]:
            """Get a list of all the brawlers available in game.

            `sort_factor` is ignored if sorting was disabled."""
            res = await self._get("/brawlers")
            if isinstance(res, ErrorResponse):
                return res

            lst = self._unwrap_list(res["items"], Brawler)

            return lst

        async def get_brawler(self, id: Union[Union[int, str], BrawlerID]) -> Brawler:
            """Get a single brawler by their ID or an enumeration value.

            If for some reason the enum `BrawlerID` is not up to date, you can specify the literal brawler name instead.
            It will fetch all the brawlers and use the ID of the brawler you specified
            """
            res = await self._get(f"/brawlers/{await self._brawler_id(id)}")
            if isinstance(res, ErrorResponse):
                return res

            return Brawler.from_json(res)

        # events

        async def get_event_rotation(self) -> EventRotation:
            """Get currently ongoing event rotation"""
            res = await self._get(f"/events/rotation")
            if isinstance(res, ErrorResponse):
                return res

            return EventRotation.from_json(res)

        # --- paging methods --- #

        async def page_club_members(
                self, tag: str, per_page: int, *, max: int = 0
        ) -> Iterator[list[ClubMember]]:
            """Return a paginator over members of a club"""

            return AsyncRequestPaginator(self, f"/clubs/{tag}/members", per_page, max, ClubMember)

        async def page_club_rankings(
                self, per_page: int, region: Optional[str] = None, *, max: int = 0
        ) -> Iterator[list[ClubRanking]]:
            """Return a paginator over club rankings in a region (or worldwide if no region specified)"""

            if region is None:
                region = "global"

            return AsyncRequestPaginator(self, f"/rankings/{region}/clubs", per_page, max, ClubRanking)

        async def page_brawler_rankings(
            self, brawler_id: Union[Union[int, str], BrawlerID], per_page: int, region: Optional[str] = None, *, max: int = 0
        ) -> Iterator[list[BrawlerRanking]]:
            """Return a paginator over brawler rankings in a region (or worldwide if no region specified)
            NOTE: look at `Client.get_brawler` documentation for more information about `brawler_id`"""
            if region is None:
                region = "global"

            return AsyncRequestPaginator(self, f"/rankings/{region}/brawlers/{await self._brawler_id(brawler_id)}", per_page, max, BrawlerRanking)

        async def page_player_rankings(
            self, per_page: int, region: Optional[str] = None, *, max: int = 0
        ) -> Iterator[list[PlayerRanking]]:
            """Return a paginator over player rankings in a region (or worldwide if no region specified)"""
            if region is None:
                region = "global"

            return AsyncRequestPaginator(self, f"/rankings/{region}/players", per_page, max, PlayerRanking)

        async def page_brawlers(
            self, per_page: int, *, max: int = 0
        ) -> Iterator[list[Brawler]]:
            """Return a paginator over all the brawlers present in game at current time"""
            return AsyncRequestPaginator(self, f"/brawlers", per_page, max, Brawler)
