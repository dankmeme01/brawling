from typing import Iterator, Optional, Union
from urllib.parse import quote_plus
from dataclasses import dataclass
from pathlib import Path
from difflib import SequenceMatcher
import logging
import re

try:
    from requests_cache import CachedSession
    from datetime import timedelta
    CACHE_ENABLED = True
except ModuleNotFoundError:
    from requests import Session
    CACHE_ENABLED = False


from .models import *
from .exceptions import *
from .util import *

__all__ = [
    "Client",
    "ErrorResponse"
]

BASE_URL = "https://api.brawlstars.com/v1"
PROXY_URL = "https://bsproxy.royaleapi.dev/v1"

@dataclass
class ErrorResponse:
    error: APIException


class Client:
    """Brawl stars API client

    To obtain data from the API, use methods starting with get_*. They return a simple response model

    To paginate over data, use methods starting with page_*. They return iterators that yield response models.
    """
    def __init__(self, token: Union[str, Path], *, proxy: bool = False, strict_errors: bool = True, force_no_cache: bool = False):
        """Initialize the main client

        Args:
            token (str): Your token, as specified on the developer website
            proxy (bool, optional): Whether to use [a 3rd party proxy](https://docs.royaleapi.com/#/proxy). DISCLAIMER: Use at your own risk. I cannot guarantee the safety of this proxy. Defaults to False.
            strict_errors (bool, optional): Whether to raise exceptions if API returned a status code other than 200, or to return them. Will still raise non-API related exceptions. Defaults to True.
        """
        self.__logger = logging.getLogger("brawling")
        self.__logger.propagate = True
        self.__ch = logging.StreamHandler()
        self.__ch.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s"))
        self.__logger.addHandler(self.__ch)
        self._debug(False)
        self._headers = {"Authorization": f"Bearer {self._parse_token(token)}"}
        self._base = PROXY_URL if proxy else BASE_URL
        self._strict = strict_errors
        self._caching = CACHE_ENABLED and not force_no_cache

        if self._caching:
            self.session = CachedSession(cache_name=".bsapi_cache", use_temp=True, expire_after=timedelta(hours=1), cache_control=True)
        else:
            self.session = Session()

    def _parse_token(self, token: Union[str, Path]) -> str:
        if isinstance(token, Path):
            return token.read_text().strip()
        else:
            if token.startswith('eyJ0'):
                return token.strip()

            ppath = Path(token)
            if ppath.exists():
                return ppath.read_text().strip()
            else:
                # Supposedly dead code, unless they switch from JWT
                return token

    def _debug(self, debug: bool):
        """Toggle debug mode

        Args:
            debug (bool): Whether debug should be enabled or disabled
        """

        self.__ch.setLevel(logging.DEBUG if debug else logging.WARN)

    def _url(self, path: str):
        """Concatenate path to base URL

        Args:
            path (str): Pathname
        """

        return self._base + (path if path.startswith("/") else ("/" + path))

    def _get(self, url: str, params: dict = None) -> Union[ErrorResponse, Union[dict, list]]:
        """Get a JSON response from a URL, returning/throwing an exception if needed.

        Args:
            url (str): the URL

        Raises:
            Exception: If the status code is not 200 but there was no error information (shouldn't ever happen!)
            APIException: If the API returned an error

        Returns:
            Any or ErrorResponse: Either a JSON object (list/dict) or an ErrorResponse if an error has happened and strict mode is disabled.
        """
        if not url.startswith(self._base):
            url = self._base + quote_plus(url, safe='/')
        else:
            url = self._base + quote_plus(url[len(self._base):], safe='/')

        r = self.session.get(url, headers=self._headers, params=params)
        self.__logger.info("got url %s, status: %d", url, r.status_code)
        if r.status_code != 200:
            if not r.text:
                raise Exception(f"Got an error and no message, code: {r.status_code}")

            json = r.json()
            exc = generate_exception(r.status_code, json["reason"], json["message"])

            self.__logger.info("generated exception: %s", str(exc))

            return self._exc_wrapper(exc)

        json = r.json()

        return json

    def _verify_tag(self, tag: str):
        regex = re.compile(r"(#)[0289CGJLPOQRUVY]{3,}", re.IGNORECASE | re.MULTILINE)
        match = regex.match(tag)
        if not match:
            return InvalidTag("Invalid tag", "Incorrect tag was provided")

        return match.group().upper()

    def _exc_wrapper(self, exc: Exception) -> ErrorResponse:
        if self._strict:
            raise exc
        else:
            return ErrorResponse(exc)

    def _unwrap_list(self, json_list, cls: BaseModel):
        return [cls.from_json(x) for x in json_list]

    def _brawler_id(self, bid: Union[Union[int, str], BrawlerID]):
        if isinstance(bid, BrawlerID):
            return str(bid.value)

        val = str(bid).upper()
        if val.isdigit():
            return val

        # we got a name
        all_brawlers = self.get_brawlers()
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

    # python dunder methods

    def __del__(self):
        self.session.close()

    def __repr__(self) -> str:
        return f"<Client(proxy={self._base == PROXY_URL}, strict_errors={self._strict}, cache_enabled={self._caching})>"

    # --- public API methods --- #

    # players

    def get_battle_log(self, tag: str) -> list[Battle]:
        """Get a list of recent battles of a player by their tag. According to the API, it may take up to 30 minutes for a new battle to appear."""
        tag = self._verify_tag(tag)
        if isinstance(tag, Exception):
            return self._exc_wrapper(tag)

        res = self._get(f"/players/{tag}/battlelog")
        if isinstance(res, ErrorResponse):
            return res

        battle_list = res["items"]

        battles = []

        for b in battle_list:
            battles.append(SoloBattle.from_json(b) if "players" in b["battle"] else TeamBattle.from_json(b))

        return battles

    def get_player(self, tag: str) -> Player:
        """Get information about a player by their tag."""
        tag = self._verify_tag(tag)
        if isinstance(tag, Exception):
            return self._exc_wrapper(tag)

        res = self._get(f"/players/{tag}")
        if isinstance(res, ErrorResponse):
            return res

        return Player.from_json(res)

    # clubs

    def get_club_members(self, tag: str) -> list[ClubMember]:
        """Get members of a club by its tag."""
        tag = self._verify_tag(tag)
        if isinstance(tag, Exception):
            return self._exc_wrapper(tag)

        res = self._get(f"/clubs/{tag}/members")
        if isinstance(res, ErrorResponse):
            return res

        return self._unwrap_list(res["items"], ClubMember)

    def get_club(self, tag: str) -> Club:
        """Get the information about a club by its tag."""
        tag = self._verify_tag(tag)
        if isinstance(tag, Exception):
            return self._exc_wrapper(tag)

        res = self._get(f"/clubs/{tag}")
        if isinstance(res, ErrorResponse):
            return res

        return Club.from_json(res)

    # rankings

    # -- power play seasons not included due to being obsolete -- #

    def get_club_rankings(self, region: Optional[str] = None) -> list[ClubRanking]:
        if region is None:
            region = 'global'

        res = self._get(f"/rankings/{region}/clubs")
        if isinstance(res, ErrorResponse):
            return res

        return self._unwrap_list(res["items"], ClubRanking)

    def get_brawler_rankings(self, brawler_id: Union[Union[int, str], BrawlerID], region: Optional[str] = None) -> list[BrawlerRanking]:
        if region is None:
            region = 'global'

        res = self._get(f"/rankings/{region}/brawlers/{self._brawler_id(brawler_id)}")
        if isinstance(res, ErrorResponse):
            return res

        return self._unwrap_list(res["items"], BrawlerRanking)

    def get_player_rankings(self, region: Optional[str] = None) -> list[PlayerRanking]:
        if region is None:
            region = 'global'

        res = self._get(f"/rankings/{region}/players")
        if isinstance(res, ErrorResponse):
            return res

        return self._unwrap_list(res["items"], PlayerRanking)

    # brawlers

    def get_brawlers(self) -> list[Brawler]:
        """Get a list of all the brawlers available in game."""
        res = self._get("/brawlers")
        if isinstance(res, ErrorResponse):
            return res

        return self._unwrap_list(res["items"], Brawler)

    def get_brawler(self, id: Union[Union[int, str], BrawlerID]) -> Brawler:
        """Get a single brawler by their ID or an enumeration value.

        If for some reason the enum `BrawlerID` is not up to date, you can specify the literal brawler name instead.
        It will fetch all the brawlers and use the ID of the brawler you specified
        """
        res = self._get(f"/brawlers/{self._brawler_id(id)}")
        if isinstance(res, ErrorResponse):
            return res

        return Brawler.from_json(res)

    # events

    def get_event_rotation(self) -> EventRotation:
        """Get currently ongoing event rotation"""
        res = self._get(f"/events/rotation")
        if isinstance(res, ErrorResponse):
            return res

        return EventRotation.from_json(res)

    # --- paging methods --- #

    def page_club_members(
            self, tag: str, per_page: int, *, max: int = 0
    ) -> Iterator[list[ClubMember]]:
        """Return a paginator over members of a club"""

        return RequestPaginator(self, f"/clubs/{tag}/members", per_page, max, ClubMember)

    def page_club_rankings(
            self, per_page: int, region: Optional[str] = None, *, max: int = 0
    ) -> Iterator[list[ClubRanking]]:
        """Return a paginator over club rankings in a region (or worldwide if no region specified)"""

        if region is None:
            region = "global"

        return RequestPaginator(self, f"/rankings/{region}/clubs", per_page, max, ClubRanking)

    def page_brawler_rankings(
        self, brawler_id: Union[Union[int, str], BrawlerID], per_page: int, region: Optional[str] = None, *, max: int = 0
    ) -> Iterator[list[BrawlerRanking]]:
        """Return a paginator over brawler rankings in a region (or worldwide if no region specified)
        NOTE: look at `Client.get_brawler` documentation for more information about `brawler_id`"""
        if region is None:
            region = "global"

        return RequestPaginator(self, f"/rankings/{region}/brawlers/{self._brawler_id(brawler_id)}", per_page, max, BrawlerRanking)

    def page_player_rankings(
        self, per_page: int, region: Optional[str] = None, *, max: int = 0
    ) -> Iterator[list[PlayerRanking]]:
        """Return a paginator over player rankings in a region (or worldwide if no region specified)"""
        if region is None:
            region = "global"

        return RequestPaginator(self, f"/rankings/{region}/players", per_page, max, PlayerRanking)

    def page_brawlers(
        self, per_page: int, *, max: int = 0
    ) -> Iterator[list[Brawler]]:
        """Return a paginator over all the brawlers present in game at current time"""
        return RequestPaginator(self, f"/brawlers", per_page, max, Brawler)
